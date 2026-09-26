#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把本地题库 JSON 打包成 data/bank.js,供网页端直接加载。
用法: python3 build_bank.py [题库.json 路径]
不传参数时默认读取 ../刷题工具/data/题库.json(与旧版刷题工具共用一份题库)。
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(BASE_DIR, "..", "刷题工具", "data", "题库.json")
OUT_FILE = os.path.join(BASE_DIR, "data", "bank.js")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    for i, q in enumerate(data):
        q.setdefault("id", "q%d" % (i + 1))
        if q.get("answer") not in q.get("options", {}):
            raise ValueError("题目 %s 的 answer(%r)不在 options 中" % (q.get("id"), q.get("answer")))
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("window.BANK=")
        f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")
    print("已生成 %s(共 %d 题)" % (OUT_FILE, len(data)))


if __name__ == "__main__":
    main()
