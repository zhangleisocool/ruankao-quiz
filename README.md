# 系统分析师刷题 PWA

软考高级「系统分析师」备考刷题工具。纯静态网页(PWA),无需后端、无需安装,
iPhone 上用 Safari「添加到主屏幕」即可像原生 app 一样使用,**离线也能刷题**。

> 题库:125 题 / 12 个考点(与本地版 `刷题工具` 共用一份数据,见下文"更新题库")

## 📱 iPhone 上使用

1. 用 Safari 打开:https://zhangleisocool.github.io/ruankao-quiz/
2. 点底部「分享」按钮 → **添加到主屏幕**
3. 桌面上出现「刷题」图标,打开即是全屏 app

- 首次打开需要联网,之后全部资源已缓存,**无网也能刷题**
- 做题记录保存在手机本地(localStorage),只在这台设备上
- 换手机前:进入「分析」页 → 数据备份 → 导出记录;新设备上导入即可

## ✨ 功能

- 按考点刷题 / 全部随机混刷,可指定每组题数(10/20/30/全部)
- 答题立即判分并显示解析
- **错题本**:答错自动收录;回做时**连续答对 2 次**自动移出,答错重新计数
- **错题分析**:薄弱考点(作答 ≥5 次且正确率 <85%)、各考点正确率、高频错题排行、常错选项分布
- 深色模式自适应;iPhone 刘海屏/底部安全区适配
- 中断可续:做题中途退出,下次打开提示继续

## 🚀 部署(GitHub Pages)

仓库推送到 GitHub 后,在 **Settings → Pages** 选择 `main` 分支 `/ (root)` 即可,
之后每次 push 自动重新发布。

### 更新题库

题库源文件放在本地 `../刷题工具/data/题库.json`,改完后:

```bash
python3 build_bank.py          # 重新生成 data/bank.js
# 同时把 sw.js 里的 CACHE 版本号 +1(让已安装的客户端刷新缓存)
git add -A && git commit -m "更新题库" && git push
```

## 💻 本地开发

```bash
python3 -m http.server 8642
# 浏览器打开 http://127.0.0.1:8642
```

直接双击 index.html 也能用(此时无 Service Worker,不影响功能)。

## 🗂 目录结构

```
├── index.html            # 应用本体(HTML/CSS/JS 单文件)
├── data/bank.js          # 题库(build_bank.py 生成,勿手改)
├── manifest.webmanifest  # PWA 清单
├── sw.js                 # Service Worker(离线缓存)
├── icons/                # 应用图标(make_icons.py 生成)
├── build_bank.py         # 题库打包脚本
└── make_icons.py         # 图标生成脚本
```

## 说明

- 做题记录仅存放在用户设备本地,不上传服务器
- 仅供个人备考学习使用
