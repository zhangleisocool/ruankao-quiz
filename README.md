# 系统分析师刷题 PWA

软考高级「系统分析师」备考刷题工具。纯静态网页(PWA),无需后端、无需安装,
iPhone 上用 Safari「添加到主屏幕」即可像原生 app 一样使用,**离线也能刷题**。

> 题库:**500 题** = 125 自编题 + **375 道历年真题**(2018–2023 六套综合知识卷,含解析)

## 📱 iPhone 上使用

1. 用 Safari 打开:https://zhangleisocool.github.io/ruankao-quiz/
2. 点底部「分享」按钮 → **添加到主屏幕**
3. 桌面上出现「刷题」图标,打开即是全屏 app

- 首次打开需要联网,之后全部资源已缓存,**无网也能刷题**
- 做题记录保存在手机本地(localStorage),只在这台设备上
- 换手机前:进入「分析」页 → 数据备份 → 导出记录;新设备上导入即可

## ✨ 功能

- 按考点刷题 / 全部随机混刷,可指定每组题数(10/20/30/全部)
- **模拟考试**:选一套真题卷或智能组卷(全库按考点均衡抽 75 题),整卷限时
  (默认 150 分钟,与真实考试一致)、答题卡跳题、题目标记、交卷后统一评分
  (及格线 = 60%),逐题回顾,成绩留档;倒计时归零自动交卷,中途退出时钟照走
- 答题立即判分并显示解析(模考中不判分,交卷后统一回顾)
- **错题本**:答错自动收录(含模考);回做时**连续答对 2 次**自动移出,答错重新计数
- **错题分析**:薄弱考点(作答 ≥5 次且正确率 <85%)、各考点正确率、高频错题排行、常错选项分布
- 深色模式自适应;iPhone 刘海屏/底部安全区适配
- 中断可续:做题/模考中途退出,下次打开提示继续

## 🚀 部署(GitHub Pages)

仓库推送到 GitHub 后,在 **Settings → Pages** 选择 `main` 分支 `/ (root)` 即可,
之后每次 push 自动重新发布。

### 更新题库

自编题库源文件在本地 `../刷题工具/data/题库.json`,改完后:

```bash
python3 build_bank.py          # 重新生成 data/bank.js
# 同时把 sw.js 里的 CACHE 版本号 +1(让已安装的客户端刷新缓存)
git add -A && git commit -m "更新题库" && git push
```

### 真题数据管道

```bash
# 1. 原始真题 JSON 放在 src-exams/choice-20xx.json(已入库)
# 2. 清洗转换:HTML 转纯文本、剔除含图题、按关键词归类考点、识别专业英语题
python3 import_zhenti.py        # 生成 data/zhenti.json
# 3. 合并打包
python3 build_bank.py
```

真题归类用关键词规则自动完成(题干权重高、选项权重低,命中 ≥2 分才归类),
少数不匹配的归入「综合其他」,如发现个别归错考点可手工改 `data/zhenti.json` 后重新 build。

## 💻 本地开发

```bash
python3 -m http.server 8642
# 浏览器打开 http://127.0.0.1:8642
```

直接双击 index.html 也能用(此时无 Service Worker,不影响功能)。

## 🗂 目录结构

```
├── index.html            # 应用本体(HTML/CSS/JS 单文件)
├── data/bank.js          # 合并题库(build_bank.py 生成,勿手改)
├── data/zhenti.json      # 清洗后的真题(import_zhenti.py 生成)
├── src-exams/            # 原始真题 JSON(2018–2023 综合知识卷)
├── manifest.webmanifest  # PWA 清单
├── sw.js                 # Service Worker(离线缓存)
├── icons/                # 应用图标(make_icons.py 生成)
├── build_bank.py         # 题库合并打包脚本
├── import_zhenti.py      # 真题清洗转换脚本
└── make_icons.py         # 图标生成脚本
```

## 说明

- 做题记录仅存放在用户设备本地,不上传服务器
- 真题来自开源整理项目 [xiaolidan00/ruankao-question](https://github.com/xiaolidan00/ruankao-question)(2018–2023,
  网络回忆版整理);题干含图的题(共 54 道)纯文本无法呈现,暂未收录;2024 年机考后的真题暂无公开结构化数据
- 仅供个人备考学习使用
