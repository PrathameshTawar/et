"""
Media pipeline service for JSON script -> vertical MP4 reels.
"""

from __future__ import annotations

import random
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config import settings


class MediaPipelineError(RuntimeError):
    def __init__(self, step: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.step = step
        self.details = details or {}


@dataclass
class SceneTiming:
    index: int
    text: str
    start: float
    end: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "text": self.text,
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "duration": round(self.end - self.start, 3),
        }


class MediaPipelineService:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        self.media_dir = base_dir / "media"
        self.templates_dir = self.media_dir / "templates"
        self.music_dir = self.media_dir / "music"
        self.output_dir = self.media_dir / "output"
        self.temp_dir = self.media_dir / "tmp"

        for path in [self.media_dir, self.templates_dir, self.music_dir, self.output_dir, self.temp_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def render(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        run_id = f"render_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        run_dir = self.temp_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        script_text = self._extract_script_text(payload)
        scene_timings = self._build_scene_timings(payload)
        if not scene_timings:
            raise MediaPipelineError("split_scenes", "No scenes generated from payload")

        total_duration = max(scene.end for scene in scene_timings)
        template_video = self._resolve_template_video(payload.get("template_video"))
        overlay_video = run_dir / "overlay.mp4"
        voiceover_mp3 = run_dir / "voiceover.mp3"
        merged_mp4 = run_dir / "merged.mp4"
        polished_mp4 = run_dir / "polished.mp4"
        final_mp4 = self.output_dir / f"{run_id}.mp4"

        self._generate_voiceover_polly(
            text=script_text,
            output_path=voiceover_mp3,
            voice_id=payload.get("voice_id", "Joanna"),
            language_code=payload.get("language_code", "en-US"),
            engine=payload.get("polly_engine", "neural"),
        ) if not payload.get("mock_tts", False) else self._generate_voiceover_mock(voiceover_mp3, total_duration)
        self._overlay_text(template_video, scene_timings, total_duration, overlay_video)
        self._merge_voiceover(overlay_video, voiceover_mp3, merged_mp4)
        self._add_background_music(merged_mp4, polished_mp4, payload.get("background_music"))
        self._format_vertical_output(polished_mp4, final_mp4)
        upload_result = (
            self._upload_to_s3(final_mp4, payload.get("s3_key_prefix", "renders"))
            if not payload.get("skip_s3_upload", False)
            else {"video_url": str(final_mp4), "s3_key": ""}
        )

        return {
            "status": "success",
            "run_id": run_id,
            "video_url": upload_result["video_url"],
            "s3_key": upload_result["s3_key"],
            "local_output": str(final_mp4),
            "timings": [scene.to_dict() for scene in scene_timings],
            "meta": {
                "template_video": str(template_video),
                "duration_seconds": round(total_duration, 3),
                "voice_id": payload.get("voice_id", "Joanna"),
                "bucket": settings.AWS_S3_BUCKET,
                "mock_tts": bool(payload.get("mock_tts", False)),
                "skip_s3_upload": bool(payload.get("skip_s3_upload", False)),
            },
        }

    def _extract_script_text(self, payload: Dict[str, Any]) -> str:
        text = payload.get("script_text", "")
        if text:
            return str(text).strip()

        scenes = payload.get("scenes", [])
        merged = " ".join(str(scene.get("text", "")).strip() for scene in scenes if str(scene.get("text", "")).strip())
        if merged:
            return merged

        raise MediaPipelineError("input_validation", "Provide script_text or scenes[].text")

    def _build_scene_timings(self, payload: Dict[str, Any]) -> List[SceneTiming]:
        scenes = payload.get("scenes", [])
        if scenes:
            valid_scenes = [scene for scene in scenes if str(scene.get("text", "")).strip()]
        else:
            script_text = self._extract_script_text(payload)
            chunks = [chunk.strip() for chunk in script_text.replace("\n", " ").split(".") if chunk.strip()]
            valid_scenes = [{"text": chunk} for chunk in chunks]

        if not valid_scenes:
            return []

        total = 0.0
        timings: List[SceneTiming] = []
        for idx, scene in enumerate(valid_scenes, start=1):
            text = str(scene.get("text", "")).strip()
            duration = scene.get("duration_sec")
            if duration is None:
                duration = max(2.0, min(8.0, len(text.split()) / 2.6))
            duration = float(duration)
            if duration <= 0:
                raise MediaPipelineError("split_scenes", f"Invalid duration for scene {idx}: {duration}")
            timings.append(SceneTiming(index=idx, text=text, start=total, end=total + duration))
            total += duration
        return timings

    def _resolve_template_video(self, template_name: Optional[str]) -> Path:
        if template_name:
            candidate = Path(template_name)
            if not candidate.is_absolute():
                candidate = self.templates_dir / template_name
            if candidate.exists():
                return candidate
            raise MediaPipelineError("create_templates", f"Template video not found: {template_name}")

        templates = sorted(self.templates_dir.glob("*.mp4"))
        if not templates:
            raise MediaPipelineError(
                "create_templates",
                f"No template videos found in {self.templates_dir}. Add 3-4 vertical mp4 files."
            )
        return random.choice(templates)

    def _generate_voiceover_polly(
        self,
        text: str,
        output_path: Path,
        voice_id: str,
        language_code: str,
        engine: str,
    ) -> None:
        if not settings.AWS_REGION:
            raise MediaPipelineError("tts_integration", "AWS_REGION is not configured")
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise MediaPipelineError("tts_integration", "AWS credentials are missing for Polly")

        polly = boto3.client("polly", region_name=settings.AWS_REGION)

        base_payload = {
            "Text": text,
            "OutputFormat": "mp3",
            "VoiceId": voice_id,
            "LanguageCode": language_code,
            "TextType": "text",
        }
        try:
            response = polly.synthesize_speech(**base_payload, Engine=engine)
        except (BotoCoreError, ClientError):
            try:
                response = polly.synthesize_speech(**base_payload)
            except (BotoCoreError, ClientError) as exc:
                raise MediaPipelineError("tts_integration", f"Polly synthesis failed: {exc}") from exc
        except Exception as exc:
            raise MediaPipelineError("tts_integration", f"Polly synthesis failed: {exc}") from exc

        stream = response.get("AudioStream")
        if stream is None:
            raise MediaPipelineError("tts_integration", "Polly returned no audio stream")

        output_path.write_bytes(stream.read())

    def _generate_voiceover_mock(self, output_path: Path, duration_seconds: float) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            f"{duration_seconds:.3f}",
            "-q:a",
            "9",
            "-acodec",
            "libmp3lame",
            str(output_path),
        ]
        self._run_cmd(cmd, "tts_mock")

    def _overlay_text(
        self,
        template_video: Path,
        scene_timings: List[SceneTiming],
        total_duration: float,
        output_path: Path,
    ) -> None:
        draw_filters: List[str] = []
        for scene in scene_timings:
            escaped_text = self._escape_drawtext(scene.text)
            draw_filters.append(
                "drawtext="
                "fontcolor=white:fontsize=56:line_spacing=10:"
                "x=(w-text_w)/2:y=h-(text_h*2):"
                "box=1:boxcolor=black@0.45:boxborderw=30:"
                f"text='{escaped_text}':"
                f"enable='between(t,{scene.start:.3f},{scene.end:.3f})'"
            )

        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            + ",".join(draw_filters)
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(template_video),
            "-t",
            f"{total_duration:.3f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
        self._run_cmd(cmd, "write_ffmpeg_overlay")

    def _merge_voiceover(self, input_video: Path, voiceover_mp3: Path, output_path: Path) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_video),
            "-i",
            str(voiceover_mp3),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ]
        self._run_cmd(cmd, "merge_voiceover")

    def _add_background_music(self, input_video: Path, output_path: Path, background_music: Optional[str]) -> None:
        music_path = self._resolve_background_music(background_music)
        if music_path is None:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_video),
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                str(output_path),
            ]
            self._run_cmd(cmd, "add_background_music")
            return

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_video),
            "-stream_loop",
            "-1",
            "-i",
            str(music_path),
            "-filter_complex",
            "[1:a]volume=0.14[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ]
        self._run_cmd(cmd, "add_background_music")

    def _format_vertical_output(self, input_video: Path, output_path: Path) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_video),
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        self._run_cmd(cmd, "format_output")

    def _resolve_background_music(self, background_music: Optional[str]) -> Optional[Path]:
        if background_music:
            candidate = Path(background_music)
            if not candidate.is_absolute():
                candidate = self.music_dir / background_music
            if candidate.exists():
                return candidate
            raise MediaPipelineError("add_background_music", f"Background music file not found: {background_music}")

        defaults = sorted(self.music_dir.glob("*.mp3"))
        return defaults[0] if defaults else None

    def _upload_to_s3(self, file_path: Path, key_prefix: str) -> Dict[str, str]:
        if not settings.AWS_S3_BUCKET:
            raise MediaPipelineError("upload_to_s3", "AWS_S3_BUCKET is not configured")

        key_prefix = key_prefix.strip("/") or "renders"
        s3_key = f"{key_prefix}/{file_path.name}"
        s3 = boto3.client("s3", region_name=settings.AWS_REGION)

        try:
            s3.upload_file(str(file_path), settings.AWS_S3_BUCKET, s3_key, ExtraArgs={"ContentType": "video/mp4"})
            video_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": settings.AWS_S3_BUCKET, "Key": s3_key},
                ExpiresIn=7 * 24 * 60 * 60,
            )
        except (BotoCoreError, ClientError) as exc:
            raise MediaPipelineError("upload_to_s3", f"S3 upload failed: {exc}") from exc

        return {"s3_key": s3_key, "video_url": video_url}

    def _run_cmd(self, cmd: List[str], step: str) -> None:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise MediaPipelineError(
                step=step,
                message=f"{step} failed with exit code {result.returncode}",
                details={
                    "command": " ".join(shlex.quote(part) for part in cmd),
                    "stderr": result.stderr[-4000:],
                    "stdout": result.stdout[-1000:],
                },
            )

    @staticmethod
    def _escape_drawtext(text: str) -> str:
        escaped = text.replace("\\", "\\\\")
        escaped = escaped.replace(":", r"\:")
        escaped = escaped.replace("'", r"\'")
        escaped = escaped.replace("%", r"\%")
        escaped = escaped.replace("\n", " ")
        return escaped
