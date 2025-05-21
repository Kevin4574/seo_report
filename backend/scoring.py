# scoring.py

import json
from pathlib import Path

# —— 1. 配置权重和阈值 —— 
# 每个维度满分 20 分
WEIGHTS = {
    "tech": 20,
    "content": 20,
    "structure": 20,
    "perf": 20,
    "authority": 20,
}

# 这里把各子项的最高分平分给该维度，简单示例
def score_tech(rep):
    checks = [
        rep["status_code"] == 200,
        rep["security"]["hsts"],
        rep["security"]["csp"],
        rep["robots"]["status"] == 200,
        len(rep["robots"]["sitemaps"]) > 0,
    ]
    return sum(checks) / len(checks) * WEIGHTS["tech"]

def score_content(rep):
    a = rep["analysis"]
    checks = [
        a["h1_count"] == 1,
        a["images_missing_alt_count"] == 0,
        a["text_ratio_percent"] >= 5,
    ]
    return sum(checks) / len(checks) * WEIGHTS["content"]

def score_structure(rep):
    a = rep["analysis"]
    checks = [
        a["links_internal_count"] > a["links_external_count"],
        len(a["schema_types"]) > 0,
        len(a["nav_links"]) > 0,
    ]
    return sum(checks) / len(checks) * WEIGHTS["structure"]

# 临时占位，后面接 Lighthouse/外链数据
def score_perf(rep):
    """
    基于 Lighthouse 性能指标打分：
      - LCP: 最佳 <=2.5s → 满分；最差 >=5s → 0；否则线性映射
      - INP: 最佳 <=200ms → 满分；最差 >=1000ms → 0；否则线性映射
      - CLS: 最佳 <=0.1 → 满分；最差 >=0.25 → 0；否则线性映射
    三项等权，每项占 20/3 分。
    """
    perf = rep.get("perf", {})
    lcp = perf.get("lcp", 5)
    inp = perf.get("inp", 1000)
    cls = perf.get("cls", 0.25)

    # 每项最大得分
    per_metric = WEIGHTS["perf"] / 3

    # LCP 分数
    if lcp <= 2.5:
        lcp_score = per_metric
    elif lcp >= 5:
        lcp_score = 0
    else:
        lcp_score = (5 - lcp) / (5 - 2.5) * per_metric

    # INP 分数
    if inp <= 200:
        inp_score = per_metric
    elif inp >= 1000:
        inp_score = 0
    else:
        inp_score = (1000 - inp) / (1000 - 200) * per_metric

    # CLS 分数
    if cls <= 0.1:
        cls_score = per_metric
    elif cls >= 0.25:
        cls_score = 0
    else:
        cls_score = (0.25 - cls) / (0.25 - 0.1) * per_metric

    return lcp_score + inp_score + cls_score




def score_authority(rep):
    return 0

def get_scores(rep):
    tech    = score_tech(rep)
    content = score_content(rep)
    structure = score_structure(rep)
    perf    = score_perf(rep)
    authority = score_authority(rep)
    overall = tech + content + structure + perf + authority
    return {
        "overall": round(overall, 1),
        "pillars": {
            "tech":    round(tech, 1),
            "content": round(content, 1),
            "structure": round(structure, 1),
            "perf":    round(perf, 1),
            "authority": round(authority, 1),
        },
    }

if __name__ == "__main__":
    # 简易测试
    raw = json.loads(Path("reports/raw.json").read_text(encoding="utf-8"))
    scores = get_scores(raw)
    print(json.dumps(scores, indent=2, ensure_ascii=False))
