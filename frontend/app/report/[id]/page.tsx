// frontend/app/report/[id]/page.tsx
"use client";




import remarkGfm from "remark-gfm";
import type { PluggableList } from "react-markdown/lib/react-markdown"


import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import LoadingOverlay, { Progress } from "@/components/LoadingOverlay";

export default function ReportPage() {
  const { id } = useParams();
  const router = useRouter();

  const [md, setMd] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<Progress>({
    value: 0,
    label: "已排队，等待开始",
  });

  // 轮询状态
  useEffect(() => {
    if (!id) return;
    let canceled = false;

    const timer = setInterval(async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/status/${id}`
      );
      if (res.ok) {
        const js = await res.json();
        if (!canceled) setStatus({ value: js.percent, label: js.message });
        if (["done", "error"].includes(js.stage)) clearInterval(timer);
      }
    }, 1000);

    return () => {
      canceled = true;
      clearInterval(timer);
    };
  }, [id]);

  // 轮询 markdown
  useEffect(() => {
    if (!id) return;
    let canceled = false;

    (async function loop() {
      while (!canceled) {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/report/${id}/markdown`,
          { cache: "no-store" }
        );
        if (res.ok) {
          const text = await res.text();
          if (!canceled) {
            setMd(text);
            setLoading(false);
          }
          break;
        }
        await new Promise((r) => setTimeout(r, 1000));
      }
    })();

    return () => {
      canceled = true;
    };
  }, [id]);

  if (!id) return null;

  return (
    <>
      {loading && <LoadingOverlay show progress={status} />}
      {!loading && md && (
        <div className="report-wrapper mx-auto max-w-4xl">
          <ReactMarkdown
            className="prose mx-auto"
            remarkPlugins={[remarkGfm] as PluggableList}  // ← 提示 TS 这是合法数组
          >
            {md}
          </ReactMarkdown>
        </div>
      )}
    </>
  );
}
