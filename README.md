# 老张随笔

投资思考 · 生活记录 · 老张的碎碎念

> 站点：**https://blog.hellohopo.dpdns.org**（GitHub Pages）

## 写作方式

- 用 **Word/WPS** 写文章，保存为 `.docx`，放入 `posts/` 文件夹
- 跑 `python build.py` 自动转换 → 生成首页列表 + 文章页 HTML → 推送上线
- 也兼容 Markdown（`posts/*.md`）

## 目录结构

```
posts/            # 源文章（.docx 或 .md）
  └── 2026-08-08-标题.docx   # 命名规则：日期-标题
index.html        # 首页（脚本自动生成）
posts_html/       # 文章页（脚本自动生成）
build.py          # 转换脚本（docx→HTML，mammoth 引擎）
```

## 标签分类

- `投资随笔`（蓝色）— 投资思考、持仓复盘、策略笔记
- `生活记录`（绿色）— 生活感悟、备考、公文心得

## 免责声明

文章仅为个人记录，不构成投资建议。
