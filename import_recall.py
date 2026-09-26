#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 src-exams/recall-*.txt(2024-2026 机考回忆版,格式见 dump_recall.py 模块注释)
转换成与题库同构的 data/zhenti-extra.json,由 build_bank.py 合并进 bank.js。

- 回忆版残缺题(选项配对损坏、缺答案)不收录,宁缺毋滥
- 个别题目答案由整理者依据教材知识核定,解析中注明
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_zhenti import classify, html_to_text  # noqa: E402  复用考点归类与文本清洗

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, "data", "zhenti-extra.json")

# 文件名 -> (试卷名, 来源标签, 解析补充)
PAPERS = {
    "recall-2024a.txt": ("2024年上半年综合知识真题(回忆版)", "2024上·回忆版", None),
    "recall-2024b.txt": ("2024年下半年综合知识真题(回忆版)", "2024下·回忆版", None),
    "recall-2025a.txt": ("2025年上半年综合知识真题(回忆版)", "2025上·回忆版", None),
    "recall-2025b.txt": ("2025年下半年综合知识真题(回忆版)", "2025下·回忆版", None),
    "recall-2026a.txt": ("2026年上半年综合知识真题(回忆版)", "2026上·回忆版", "回忆版整理,答案已由整理者核定"),
}

EXPLAIN_APPEND = {
    ("recall-2026a.txt", 2): "回忆版原帖未给参考答案,答案由整理者依据标准化常识核定(GB 为强制性国家标准代号,GB/T 为推荐性)。",
    ("recall-2026a.txt", 3): "回忆版原帖未给参考答案,答案由整理者核定:两点连线上的点仍在可行域内,x+y=72 恒定,仅 (42,30) 满足。",
    ("recall-2026a.txt", 4): "回忆版原帖未给参考答案,答案由整理者核定:2NF 消除部分函数依赖,3NF 在此基础上消除非主属性对码的传递函数依赖。",
}


def parse_canonical(path):
    """解析规范文本 -> [{num, stem, opts, answer, note}]"""
    questions, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        if line.startswith("### "):
            cur = {"num": int(line[4:]), "stem": [], "opts": {}, "answer": None, "note": []}
            questions.append(cur)
        elif "|" in line and line[0] in "ABCD":
            letter, _, text = line.partition("|")
            cur["opts"][letter] = text.strip()
        elif line.startswith("备注|"):
            cur["note"].append(line[3:])
        elif line.startswith("答案: "):
            cur["answer"] = line[4:].strip()
        elif cur is not None:
            cur["stem"].append(line)
    return questions


def main():
    out, skipped = [], 0
    for fname, (paper, source, note_all) in PAPERS.items():
        path = os.path.join(BASE_DIR, "src-exams", fname)
        if not os.path.exists(path):
            print("警告: 缺少 %s" % path)
            continue
        kept = 0
        for q in parse_canonical(path):
            answer = q["answer"]
            if answer not in q["opts"]:
                skipped += 1     # 缺答案 / 答案非单一字母 / 选项残缺
                continue
            explanation = "；".join(x for x in q["note"] if x)
            append = EXPLAIN_APPEND.get((fname, q["num"]))
            if append:
                explanation = (explanation + "；" if explanation else "") + append
            elif note_all:
                explanation = (explanation + "；" if explanation else "") + note_all
            stem = " ".join(q["stem"]).strip()
            out.append({
                "id": "zt%s-%02d" % (fname[7:11] + fname[11], q["num"]),
                "category": classify(stem, " ".join(q["opts"].values())),
                "question": stem,
                "options": q["opts"],
                "answer": answer,
                "explanation": explanation or "考生回忆版,暂无解析。",
                "paper": paper,
                "source": source,
            })
            kept += 1
        print("%s:收录 %d 题" % (fname, kept))
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print("已生成 %s,共 %d 题(跳过 %d 题残缺/缺答案)" % (OUT_FILE, len(out), skipped))


if __name__ == "__main__":
    main()
