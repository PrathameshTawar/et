from __future__ import annotations
import json
import logging

logger = logging.getLogger(__name__)


def _get_bedrock():
    try:
        import boto3
        return boto3.client("bedrock-runtime", region_name="us-east-1")
    except Exception:
        return None


def generate_image(prompt: str) -> str:
    bedrock = _get_bedrock()
    if bedrock is None:
        raise RuntimeError("AWS boto3 not available")

    body = json.dumps({
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 10,
        "steps": 50
    })

    try:
        response = bedrock.invoke_model(
            modelId="stability.stable-diffusion-xl-v1",
            body=body
        )
        result = json.loads(response["body"].read())
        return result["artifacts"][0]["base64"]
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {e}")
