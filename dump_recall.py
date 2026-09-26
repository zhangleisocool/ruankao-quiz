#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性脚本:把抓回来的 2024 真题回忆页(/tmp HTML)清洗成规范文本,
输出到 src-exams/recall-*.txt,供 import_recall.py 二次转换。

规范格式:
### <题号>
题干(可多行)
A|选项文本
B|选项文本
C|选项文本
D|选项文本
答案: <字母>

来源:
- 2024上半年  blog.csdn.net/zzjjiaa/article/details/142171684
- 2024下半年  blog.csdn.net/java_faep/article/details/144426936
- 2025/2026 的碎片题量太少,直接手写在 import_recall.py 里
"""
import html as h
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "src-exams")


def to_lines(path):
    """取 CSDN 正文区并转纯文本行"""
    raw = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r'<div id="content_views"[^>]*>([\s\S]*?)</article>', raw)
    seg = m.group(0) if m else raw
    seg = re.sub(r"<script[\s\S]*?</script>", "", seg)
    seg = re.sub(r"<style[\s\S]*?</style>", "", seg)
    seg = re.sub(r"<(br|/p|/div|/li|/h[1-6]|/tr)[^>]*>", "\n", seg)
    seg = re.sub(r"<[^>]+>", " ", seg)
    seg = h.unescape(seg)
    lines = [re.sub(r"\s+", " ", l).strip() for l in seg.split("\n") if l.strip()]
    # 修复题号数字被空格拆开的情况:『1 7 、』→『17、』
    lines = [re.sub(r"^(\d)\s+(\d)\s*([、.．])", r"\1\2\3", l) for l in lines]
    return lines


def extract_opts(line):
    """从一行里拆出 (字母, 选项文本);支持同行多选项与『D指令寄存器』式无分隔符"""
    marks = [(m.start(1), m.group(1), m.end()) for m in re.finditer(r"(?:^|\s)([A-D])(?:\s*[：:.、]\s*|\s+)", line)]
    if not marks:
        m = re.match(r"^([A-D])[：:.、]?\s*(\S.*)$", line)
        if m and len(line) < 80:
            return [(m.group(1), m.group(2).strip())]
        return []
    out = []
    for k, (spos, letter, epos) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else len(line)
        text = line[epos:end].strip()
        if text:
            out.append((letter, text))
    return out


def parse_numbered(lines, ans_pattern, ans_fallback=None):
    starts = [i for i, l in enumerate(lines) if re.match(r"^\d{1,2}\s*[、.．]\s*\S", l)]
    questions = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        block = lines[s:e]
        head = re.match(r"^(\d{1,2})\s*[、.．]\s*(.*)$", block[0])
        num, stem = int(head.group(1)), head.group(2)
        opts, answer, body = {}, None, []
        for l in block[1:]:
            if re.match(r"^\s*(参考)?答案[:：]", l):
                m = re.match(r"^\s*(?:参考)?答案[:：]\s*([A-D])\s*$", l)
                if m and not answer:
                    answer = m.group(1)
                continue
            if ans_fallback and re.match(r"^\s*解析[:：]", l):
                m = re.match(ans_fallback, l)
                if m and not answer:
                    answer = m.group(1)
                continue
            found = extract_opts(l)
            if found:
                for letter, text in found:
                    opts[letter] = (opts.get(letter, "") + " " + text).strip()
                continue
            body.append(l)
        if stem and len(opts) >= 3:
            questions.append({"num": num, "stem": stem, "opts": opts, "answer": answer, "extra": body})
    return questions


def write_canonical(fname, questions):
    path = os.path.join(OUT, fname)
    with open(path, "w", encoding="utf-8") as f:
        for q in questions:
            f.write("### %d\n%s\n" % (q["num"], q["stem"]))
            for letter in sorted(q["opts"]):
                f.write("%s|%s\n" % (letter, q["opts"][letter]))
            if q["extra"]:
                f.write("备注|%s\n" % " ／ ".join(q["extra"])[:300])
            f.write("答案: %s\n\n" % (q["answer"] or "?"))
    print("写出 %s:%d 题(其中 %d 题缺答案)" % (path, len(questions), sum(1 for q in questions if not q["answer"])))


def main():
    lines = to_lines("/tmp/zt-new/csdn-2024h2.html")
    qs = parse_numbered(lines, r"^参考答案[:：]\s*([A-D])")
    write_canonical("recall-2024b.txt", qs)

    lines = to_lines("/tmp/zt-new/csdn-2024h1.html")
    qs = parse_numbered(lines, r"^答案[:：]\s*([A-D])$", r"^解析[:：]\s*([A-D])\s*$")
    write_canonical("recall-2024a.txt", qs)


if __name__ == "__main__":
    main()
