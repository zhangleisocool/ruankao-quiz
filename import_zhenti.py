#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 src-exams/choice-20xx.json(系统分析师综合知识真题,来源:github.com/xiaolidan00/ruankao-question)
转换成与题库同构的 data/zhenti.json,再由 build_bank.py 合并进 bank.js。

- 题干/解析为 HTML,转纯文本;上标 x^2、下标 x_1 保留记号
- 题干或选项含图的题跳过(纯文本 app 无法呈现)
- 按关键词把真题归入现有考点(题干权重高,选项权重低);专业英语题单独识别;无命中归"综合其他"
- 保留卷面题号:id 形如 zt2019-07(第 7 题,含跳过时的空洞)
"""
import html
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src-exams")
OUT_FILE = os.path.join(BASE_DIR, "data", "zhenti.json")
YEARS = range(2018, 2024)

# (考点, 关键词列表)。命中打分:题干 ×2,选项 ×1,取最高分考点;并列取先出现者。
RULES = [
    ("信息安全", ["数字签名", "报文摘要", "防火墙", "入侵检测", "漏洞", "木马", "病毒", "恶意代码", "跨站",
                 "SQL注入", "网络攻击", "拒绝服务", "密钥", "加密", "解密", "对称密码", "公钥", "私钥",
                 "RSA", "AES", "DES", "MD5", "SHA", "认证", "数字证书", "CA认证", "PKI", "安全"]),
    ("计算机网络", ["子网", "掩码", "路由", "IPv6", "IPv4", "IP报文", "IP地址", "IP协议", "TCP", "UDP",
                  "HTTP", "HTTPS", "DNS", "DHCP", "ARP", "FTP", "SMTP", "POP3", "以太网", "交换机",
                  "VLAN", "网关", "拓扑", "带宽", "集线器", "网络", "协议"]),
    ("数据库", ["数据库", "SQL", "关系模式", "范式", "函数依赖", "关系代数", "E-R", "ER图", "实体联系",
               "事务", "封锁", "并发控制", "视图", "索引", "主键", "外键", "候选键", "反规范化",
               "分布式数据库", "NoSQL", "数据仓库", "数据挖掘", "商业智能", "数据字典"]),
    ("操作系统与计算机组成", ["进程", "线程", "信号量", "PV操作", "死锁", "银行家", "调度算法", "页式", "段式",
                      "虚拟存储", "虚存", "页面置换", "LRU", "FIFO", "内存", "高速缓存", "Cache", "流水线",
                      "中断", "寻址", "补码", "原码", "反码", "浮点", "寄存器", "总线", "磁盘", "位示图",
                      "海明", "CRC", "循环冗余", "指令", "CPU", "I/O", "DMA", "RISC", "CISC", "操作系统",
                      "文件系统", "索引节点"]),
    ("UML与面向对象", ["UML", "用例图", "类图", "顺序图", "序列图", "通信图", "状态图", "活动图", "部署图",
                 "构件图", "包图", "对象图", "面向对象", "封装", "继承", "多态", "重载", "重写", "类",
                 "设计模式", "观察者", "策略", "工厂方法", "抽象工厂", "单例", "适配器", "桥接", "装饰",
                 "外观", "享元", "代理", "命令", "备忘录", "访问者", "迭代器", "职责链", "中介者",
                 "解释器", "模板方法", "组合模式", "开闭原则", "里氏", "依赖倒置"]),
    ("结构化分析与数据流图", ["数据流图", "数据流程", "DFD", "父图", "子图", "变换流", "事务流", "结构化设计",
                     "结构化分析", "结构化方法", "变换中心"]),
    ("需求工程", ["需求", "业务流程", "业务过程", "业务流程建模", "QFD"]),
    ("软件工程与过程模型", ["瀑布", "原型", "增量", "螺旋", "喷泉", "敏捷", "Scrum", "极限编程", "结对编程",
                    "过程模型", "CMM", "CMMI", "软件过程", "净室", "逆向工程", "重构", "软件复用",
                    "构件", "软件测试", "测试用例", "白盒", "黑盒", "回归测试", "单元测试", "集成测试",
                    "确认测试", "系统测试", "软件维护", "适应性维护", "完善性维护", "配置管理", "软件质量",
                    "McCall", "软件度量", "软件工程", " McCabe", "圈复杂度", "软件评审", "里程碑", "基线"]),
    ("系统架构与可靠性", ["可靠性", "MTBF", "MTTR", "可用性", "冗余", "容错", "架构风格", "管道", "过滤器",
                  "中间件", "架构评估", "ATAM", "SAAM", "质量属性", "性能", "吞吐", "集群", "负载均衡",
                  "微服务", "SOA", "云计算", "大数据", "架构", "分层", "MVC", "MVVM", "事件驱动",
                  "富互联网应用", "物联网", "嵌入式"]),
    ("项目管理与计算", ["项目管理", "挣值", "挣得值", "成本偏差", "进度偏差", "成本绩效指数", "进度绩效指数",
                  "关键路径", "甘特图", "PERT", "风险评估", "风险暴露", "风险管理", "干系人", "WBS",
                  "进度管理", "成本管理", "沟通渠道", "团队建设", "项目经理", "项目范围", "项目章程"]),
    ("知识产权与标准化", ["著作权", "专利", "商标", "知识产权", "软件保护条例", "署名权", "发表权", "修改权",
                   "保护期限", "侵权", "许可", "标准化", "国家标准", "国际标准", "行业标准", "企业标准",
                   "GB/T", "ISO", "IEC", "标准代号"]),
    ("数学与算法", ["时间复杂度", "空间复杂度", "排序", "二分", "分治", "动态规划", "贪心", "回溯", "分支限界",
                "最短路径", "最小生成树", "拓扑排序", "哈夫曼", "二叉树", "遍历", "图论", "邻接矩阵",
                "线性规划", "排队论", "概率", "期望", "方差", "矩阵", "递推", "递归",
                "斐波那契", "KMP", "模式匹配", "散列", "哈希", "数学", "运筹", "决策", "对策论",
                "指派问题", "运输问题", "等价类"]),
]

EN_RATIO = re.compile(r"[A-Za-z]")
CLOZE_NOISE = re.compile(r"请作答第.{1,4}(?:个)?空[。.]?")


def html_to_text(s):
    if not s:
        return ""
    s = re.sub(r"(?is)<(script|style).*?</\1>", "", s)
    s = re.sub(r"(?i)<sup>(.*?)</sup>", r"^\1", s)
    s = re.sub(r"(?i)<sub>(.*?)</sub>", r"_\1", s)
    s = re.sub(r"(?i)<\s*(br|/p|/div|/li|/h[1-6]|/tr)[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = CLOZE_NOISE.sub("", s)
    s = s.replace(" ", " ").replace("　", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines).strip()


def is_english(text):
    letters = len(EN_RATIO.findall(text))
    return letters > 40 and letters / max(1, len(text.replace("\n", ""))) > 0.55


def classify(title, opt_text):
    if is_english(title):
        return "专业英语"
    best, best_score = None, 0
    for cat, kws in RULES:
        score = 0
        for kw in kws:
            if kw in title:
                score += 2
            if kw in opt_text:
                score += 1
        if score > best_score:
            best, best_score = cat, score
    # 低于 2 分说明只有选项里的弱信号,宁可不归类
    return best if best_score >= 2 else "综合其他"


def main():
    out = []
    for y in YEARS:
        path = os.path.join(SRC_DIR, "choice-%d.json" % y)
        with open(path, "r", encoding="utf-8") as f:
            qs = json.load(f)["data"]["questionList"]
        kept = skipped = 0
        for i, q in enumerate(qs, start=1):
            title_raw = q.get("title") or ""
            items = q.get("itemList") or []
            opt_raw = [it.get("content") or "" for it in items]
            if "<img" in title_raw or any("<img" in c for c in opt_raw):
                skipped += 1
                continue
            options = {}
            for it in items:
                letter = (it.get("chooseValue") or "").strip().upper()
                text = html_to_text(it.get("content"))
                if not letter or not text:
                    options = None
                    break
                options[letter] = text
            if not options or q.get("answer") not in options:
                skipped += 1
                continue
            title = html_to_text(title_raw)
            explain = html_to_text(q.get("analyze"))
            opt_text = " ".join(options.values())
            out.append({
                "id": "zt%d-%02d" % (y, i),
                "category": classify(title, opt_text),
                "question": title,
                "options": options,
                "answer": q["answer"],
                "explanation": explain,
                "paper": "%d年系统分析师综合知识真题" % y,
                "source": "%d年真题" % y,
            })
            kept += 1
        print("%d 年:收录 %d 题,跳过 %d 题(含图或数据缺失)" % (y, kept, skipped))
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print("已生成 %s,共 %d 题" % (OUT_FILE, len(out)))


if __name__ == "__main__":
    main()
