#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 app 图标(纯标准库,不依赖 PIL):圆角渐变方块 + 白色对勾,带抗锯齿。
输出 icons/icon-512.png / icon-192.png / icon-180.png / icon-32.png
"""
import math
import os
import struct
import zlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "icons")
SIZES = [512, 192, 180, 32]
COLOR_TOP = (59, 130, 246)     # #3b82f6
COLOR_BOTTOM = (29, 78, 216)   # #1d4ed8
CHECK_PTS = [(-0.25, -0.02), (-0.06, 0.18), (0.30, -0.24)]  # 屏幕坐标 y 朝下:短笔向下,长笔挑上去
CHECK_HW = 0.075               # 对勾线宽的一半(相对边长)


def clamp(x, a, b):
    return a if x < a else (b if x > b else x)


def sd_round_rect(px, py, hw, hh, r):
    qx = abs(px) - (hw - r)
    qy = abs(py) - (hh - r)
    ox, oy = max(qx, 0.0), max(qy, 0.0)
    return math.hypot(ox, oy) + min(max(qx, qy), 0.0) - r


def sd_seg(px, py, a, b):
    abx, aby = b[0] - a[0], b[1] - a[1]
    apx, apy = px - a[0], py - a[1]
    t = clamp((apx * abx + apy * aby) / (abx * abx + aby * aby), 0.0, 1.0)
    return math.hypot(apx - t * abx, apy - t * aby)


def render(size):
    # 所有几何量都用归一化坐标 [-0.5, 0.5],只在换算像素覆盖度时乘 size
    radius = 0.225
    pts = CHECK_PTS
    rows = []
    for y in range(size):
        row = bytearray()
        py = (y + 0.5) / size - 0.5
        t = (y + 0.5) / size
        bg = tuple(COLOR_TOP[i] + (COLOR_BOTTOM[i] - COLOR_TOP[i]) * t for i in range(3))
        for x in range(size):
            px = (x + 0.5) / size - 0.5
            d_bg = sd_round_rect(px, py, 0.5, 0.5, radius)
            a_bg = clamp(0.5 - d_bg * size, 0.0, 1.0)
            if a_bg <= 0.0:
                row += b"\x00\x00\x00\x00"
                continue
            d_chk = min(sd_seg(px, py, pts[0], pts[1]), sd_seg(px, py, pts[1], pts[2]))
            a_chk = clamp(0.5 - (d_chk - CHECK_HW) * size, 0.0, 1.0)
            c = tuple(255 * a_chk + bg[i] * (1 - a_chk) for i in range(3))
            row += bytes((round(c[0]), round(c[1]), round(c[2]), round(a_bg * 255)))
        rows.append(bytes(row))
    return rows


def write_png(path, size, rows):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + r for r in rows)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for size in SIZES:
        path = os.path.join(OUT_DIR, "icon-%d.png" % size)
        write_png(path, size, render(size))
        print("已生成 %s" % path)


if __name__ == "__main__":
    main()
