"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/admin_dashboard");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      Redirecting to admin dashboard...
    </div>
  );
}
