#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把两路题库合并打包成 data/bank.js,供网页端直接加载:
1. 自编题库 ../刷题工具/data/题库.json(与旧版刷题工具共用)
2. 历年真题 data/zhenti.json(import_zhenti.py 从 src-exams/ 生成)
用法: python3 build_bank.py [自编题库.json 路径]
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(BASE_DIR, "..", "刷题工具", "data", "题库.json")
ZHEN_TI = [
    os.path.join(BASE_DIR, "data", "zhenti.json"),      # 2018-2023 结构化真题
    os.path.join(BASE_DIR, "data", "zhenti-extra.json"),  # 2024-2026 机考回忆版
]
OUT_FILE = os.path.join(BASE_DIR, "data", "bank.js")


def validate(q, idx):
    q.setdefault("id", "q%d" % (idx + 1))
    if q.get("answer") not in q.get("options", {}):
        raise ValueError("题目 %s 的 answer(%r)不在 options 中" % (q.get("id"), q.get("answer")))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    bank = []
    for path in [src] + ZHEN_TI:
        if not os.path.exists(path):
            print("警告: %s 不存在,跳过" % path)
            continue
        with open(path, "r", encoding="utf-8") as f:
            part = json.load(f)
        print("载入 %s:%d 题" % (path, len(part)))
        bank.extend(part)
    seen = set()
    for i, q in enumerate(bank):
        validate(q, i)
        if q["id"] in seen:
            raise ValueError("题目 id 重复: %s" % q["id"])
        seen.add(q["id"])
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("window.BANK=")
        f.write(json.dumps(bank, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")
    print("已生成 %s(共 %d 题)" % (OUT_FILE, len(bank)))


if __name__ == "__main__":
    main()
