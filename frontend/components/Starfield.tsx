"use client";
import { useRef, useEffect } from "react";

/**
 * 纯前端 Canvas 星野 / 粒子背景
 */
export default function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    let w = (canvas.width = window.innerWidth);
    let h = (canvas.height = window.innerHeight);

    const stars = Array.from({ length: 120 }, () => ({
      x: Math.random() * w - w / 2,
      y: Math.random() * h - h / 2,
      z: Math.random() * w,
    }));

    const draw = () => {
      ctx.fillStyle = "#0d0d0d";
      ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = "#ffffff";

      stars.forEach((s) => {
        s.z -= 2;
        if (s.z <= 0) s.z = w;

        const k = 128 / s.z;
        const px = s.x * k + w / 2;
        const py = s.y * k + h / 2;

        if (px >= 0 && px <= w && py >= 0 && py <= h) {
          const size = (1 - s.z / w) * 2;
          ctx.fillRect(px, py, size, size);
        }
      });

      requestAnimationFrame(draw);
    };

    draw();

    // 适配窗口缩放
    const handleResize = () => {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 -z-10 opacity-50" />;
}
