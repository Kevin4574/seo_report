import matplotlib
matplotlib.use("Agg")        # ← 在任何 pyplot import 之前设置后端


import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scoring import get_scores


def save_gauge(overall, out_path):
    fig, ax = plt.subplots()
    ax.pie(
        [overall, 100 - overall],
        startangle=180,
        counterclock=False,
        wedgeprops={"width": 0.4}
    )
    ax.set_aspect("equal")
    plt.title(f"Overall SEO Score: {overall}/100")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()



def save_headings(analysis, out_path):
    counts = [
        analysis["h1_count"],
        analysis["h2_count"],
        analysis["h3_count"],
    ]
    fig, ax = plt.subplots()
    ax.bar(["H1", "H2", "H3"], counts)
    ax.set_ylabel("Count")
    plt.title("Heading Tag Distribution")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def save_link_pie(analysis, out_path):
    internal = analysis["links_internal_count"]
    external = analysis["links_external_count"]
    fig, ax = plt.subplots()
    ax.pie(
        [internal, external],
        labels=["Internal", "External"],
        autopct="%1.0f%%",
        startangle=90
    )
    ax.set_title("Internal vs External Links")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def save_radar(pillars, out_path):
    labels = list(pillars.keys())
    values = [pillars[label] for label in labels]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels) + 1, endpoint=True)
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, values, marker="o")
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 20)
    plt.title("Five-Dimension SEO Radar")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def save_security_heatmap(security, out_path):
    # 准备数据
    headers = ["HSTS", "CSP"] + list(security.get("other_security_headers", {}).keys())
    values = [
        1 if security.get("hsts") else 0,
        1 if security.get("csp") else 0,
    ] + [1] * len(security.get("other_security_headers", {}))
    matrix = np.array([values])
    fig, ax = plt.subplots()
    cax = ax.imshow(matrix, cmap="Greens", aspect="auto")
    ax.set_xticks(np.arange(len(headers)))
    ax.set_xticklabels(headers, rotation=45, ha="right")
    ax.set_yticks([])
    plt.title("Security Headers Presence Heatmap")
    fig.colorbar(cax, orientation="horizontal", pad=0.2)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def save_schema_cloud(analysis, out_path):
    types = analysis.get("schema_types", [])
    if not types:
        # 空图示占位
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No schema types found", ha="center", va="center")
        ax.axis("off")
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
        return
    # 统计频次
    from collections import Counter
    cnt = Counter(types)
    labels, freqs = zip(*cnt.most_common(10))
    fig, ax = plt.subplots()
    ax.bar(labels, freqs)
    plt.xticks(rotation=45, ha="right")
    plt.title("Top Schema.org Types")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def save_perf_line(rep, out_path):
    ttfb = rep.get("ttfb_ms") or 0
    baseline = 800  # ms 基准值
    fig, ax = plt.subplots()
    ax.plot([0, 1], [baseline, ttfb], marker="o")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Target <800ms", "Your TTFB"])
    plt.title("TTFB vs Target")
    plt.ylabel("Milliseconds")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def main():
    out_dir = Path("reports")
    rep = json.loads((out_dir / "raw.json").read_text(encoding="utf-8"))
    scores = get_scores(rep)
    # 旧图
    save_gauge(scores["overall"],      out_dir / "gauge.png")
    save_headings(rep["analysis"],     out_dir / "headings.png")
    save_link_pie(rep["analysis"],     out_dir / "links.png")
    save_radar(scores["pillars"],      out_dir / "radar.png")
    # 新增图
    save_security_heatmap(rep["security"], out_dir / "security_heatmap.png")
    save_schema_cloud(rep["analysis"],      out_dir / "schema_cloud.png")
    save_perf_line(rep,                     out_dir / "perf_line.png")
    print("✅ 新增所有图表已生成 -> reports/*.png")

if __name__ == "__main__":
    main()
