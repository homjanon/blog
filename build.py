#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老张随笔 · 博客构建脚本
- 扫描 posts/ 下的 .docx 和 .md 文件
- 用 mammoth 把 docx 转 HTML（保留标题/加粗/列表/表格/图片）
- 生成文章页 posts_html/xxx.html + 首页 index.html
用法: python build.py
"""
import base64
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
POSTS_DIR = BASE / "posts"
HTML_DIR = BASE / "posts_html"
INDEX = BASE / "index.html"

# 标签分类（文件名关键词 → 分类）
CATEGORY_RULES = [
    (("投资", "股票", "基金", "ETF", "银行", "持仓", "策略", "市场", "估值", "分红", "港股", "美股", "A股", "红利"), "投资随笔"),
]
DEFAULT_CAT = "生活记录"

STYLE = """
<style>
:root{--bg:#f6f8fa;--card:#fff;--ink:#1a1a1a;--sub:#6b7280;--line:#e5e7eb;
--blue:#185fa5;--green:#3b6d11;--accent:#2563eb}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.8}
.wrap{max-width:720px;margin:0 auto;padding:24px 20px 60px}
.head{display:flex;align-items:center;justify-content:space-between;padding:14px 0 18px;border-bottom:1px solid var(--line);margin-bottom:24px}
.site{font-size:19px;font-weight:600}
.back{font-size:13px;color:var(--sub);text-decoration:none}
.back:hover{color:var(--accent)}
.post-meta{color:var(--sub);font-size:13px;margin-bottom:28px}
.post-title{font-size:26px;font-weight:600;line-height:1.5;margin-bottom:12px}
.post-body{font-size:16px}
.post-body h2{font-size:20px;margin:28px 0 12px;padding-left:10px;border-left:4px solid var(--accent)}
.post-body h3{font-size:17px;margin:22px 0 10px}
.post-body p{margin:12px 0}
.post-body strong{font-weight:600}
.post-body blockquote{margin:14px 0;padding:10px 16px;background:#eef4fb;border-left:4px solid var(--accent);color:#33475b;border-radius:0 8px 8px 0}
.post-body code{background:#f1f3f5;border-radius:4px;padding:2px 6px;font-size:14px;font-family:Consolas,monospace}
.post-body pre{background:#1e293b;color:#e2e8f0;border-radius:10px;padding:16px;overflow-x:auto;margin:14px 0;font-size:13px}
.post-body pre code{background:none;padding:0}
.post-body table{border-collapse:collapse;margin:14px 0;width:100%}
.post-body th,.post-body td{border:1px solid var(--line);padding:8px 12px;font-size:14px}
.post-body th{background:#f1f5f9;font-weight:600}
.post-body img{max-width:100%;border-radius:10px;margin:12px 0}
.post-body hr{border:none;border-top:1px solid var(--line);margin:24px 0}
.back-home{margin-top:40px;padding-top:20px;border-top:1px solid var(--line);font-size:13px}
.foot{text-align:center;color:var(--sub);font-size:12px;margin-top:40px;padding-top:20px;border-top:1px solid var(--line)}
</style>
"""

INDEX_STYLE = """
<style>
:root{--bg:#f6f8fa;--card:#fff;--ink:#1a1a1a;--sub:#6b7280;--line:#e5e7eb;--blue:#185fa5;--green:#3b6d11;--accent:#2563eb}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.8}
.wrap{max-width:720px;margin:0 auto;padding:24px 20px 60px}
.head{display:flex;align-items:center;justify-content:space-between;padding:14px 0 18px;border-bottom:1px solid var(--line);margin-bottom:24px}
.site{font-size:19px;font-weight:600}
.sub{font-size:13px;color:var(--sub);margin-top:2px}
.back{font-size:13px;color:var(--sub);text-decoration:none}
.back:hover{color:var(--accent)}
.list{display:flex;flex-direction:column;gap:14px}
.item{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;text-decoration:none;color:var(--ink);transition:transform .12s,box-shadow .12s}
.item:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.06)}
.item-date{font-size:12px;color:var(--sub);font-family:Consolas,monospace}
.item h2{font-size:16px;font-weight:600;margin:6px 0 6px}
.item .desc{font-size:13px;color:var(--sub);line-height:1.7}
.tags{display:flex;gap:8px;margin-top:10px}
.tag{font-size:11px;border-radius:999px;padding:2px 10px}
.tag.inv{background:#e6f1fb;color:var(--blue)}
.tag.life{background:#eaf3de;color:var(--green)}
.empty{text-align:center;color:var(--sub);padding:60px 0;font-size:14px}
.foot{text-align:center;color:var(--sub);font-size:12px;margin-top:40px;padding-top:20px;border-top:1px solid var(--line)}
</style>
"""


def detect_category(filename):
    for keywords, cat in CATEGORY_RULES:
        if any(k in filename for k in keywords):
            return cat
    return DEFAULT_CAT


def slugify(title):
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', title).strip('-')
    return s or 'post'


def parse_docx(path):
    import mammoth
    with open(path, 'rb') as f:
        result = mammoth.convert_to_html(f)
        return result.value  # html 字符串


def parse_md(path):
    import markdown
    text = path.read_text(encoding='utf-8')
    md = markdown.Markdown(extensions=['extra', 'sane_lists', 'tables'])
    return md.convert(text)


def extract_title_docx(path):
    """从 docx 第一个标题或文件名提取标题"""
    try:
        import docx
        d = docx.Document(str(path))
        for p in d.paragraphs:
            if p.text.strip() and p.style.name.startswith('Heading'):
                return p.text.strip()
            if p.text.strip():
                return p.text.strip()[:50]
    except Exception:
        pass
    return path.stem


def build_article(filename):
    """转换单篇文章，返回 (slug, meta)"""
    path = POSTS_DIR / filename
    if path.suffix.lower() == '.docx':
        html_body = parse_docx(path)
        title = extract_title_docx(path)
    elif path.suffix.lower() in ('.md', '.markdown'):
        html_body = parse_md(path)
        title = filename[:filename.rfind('.')]
        # 尝试从 md 提取 # 标题
        m = re.match(r'#\s+(.+)', path.read_text(encoding='utf-8'))
        if m:
            title = m.group(1).strip()
    else:
        return None

    # 文件名: YYYY-MM-DD-标题.docx
    m = re.match(r'(\d{4}-\d{2}-\d{2})[_-]*(.*)', filename)
    date = m.group(1) if m else datetime.now().strftime('%Y-%m-%d')
    slug = slugify(title)
    category = detect_category(filename)

    # 生成文章页
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · 老张随笔</title>
{STYLE}
</head>
<body>
<div class="wrap">
  <div class="head">
    <div>
      <div class="site">老张随笔</div>
      <div class="post-meta">{date} · {category}</div>
    </div>
    <a class="back" href="../index.html">← 返回首页</a>
  </div>
  <h1 class="post-title">{title}</h1>
  <div class="post-body">
{html_body}
  </div>
  <div class="back-home"><a class="back" href="../index.html">← 返回全部文章</a></div>
  <div class="foot">老张随笔 · 投资思考与生活记录 · 不构成投资建议</div>
</div>
</body>
</html>"""
    HTML_DIR.mkdir(exist_ok=True)
    (HTML_DIR / f"{slug}.html").write_text(html, encoding='utf-8')

    return slug, {'title': title, 'date': date, 'category': category, 'slug': slug}


def build_index(articles):
    """生成首页"""
    # 按日期倒序
    articles.sort(key=lambda a: a['date'], reverse=True)
    items_html = []
    for a in articles:
        tag_cls = 'inv' if a['category'] == '投资随笔' else 'life'
        # 摘要：取文章页前 120 字（简单截取标题后）
        items_html.append(f"""<a class="item" href="posts_html/{a['slug']}.html">
  <div class="item-date">{a['date']}</div>
  <h2>{a['title']}</h2>
  <div class="tags"><span class="tag {tag_cls}">{a['category']}</span></div>
</a>""")
    list_html = '\n'.join(items_html) if items_html else '<div class="empty">还没有文章，第一篇在路上了…</div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>老张随笔 · 投资思考与生活记录</title>
{INDEX_STYLE}
</head>
<body>
<div class="wrap">
  <div class="head">
    <div>
      <div class="site">老张随笔</div>
      <div class="sub">投资思考 · 生活记录 · 老张的碎碎念</div>
    </div>
    <a class="back" href="https://hellohopo.dpdns.org/">工具箱 →</a>
  </div>
  <div class="list">
{list_html}
  </div>
  <div class="foot">老张随笔 · {len(articles)} 篇 · 不构成投资建议</div>
</div>
</body>
</html>"""
    INDEX.write_text(html, encoding='utf-8')


def main():
    if not POSTS_DIR.is_dir():
        POSTS_DIR.mkdir()
        print("已创建 posts/ 文件夹，请放入 .docx 或 .md 文章")
        return
    files = sorted([f.name for f in POSTS_DIR.iterdir()
                    if f.suffix.lower() in ('.docx', '.md', '.markdown')])
    if not files:
        print("posts/ 文件夹为空，没有文章可构建")
        build_index([])
        return
    articles = []
    for fname in files:
        try:
            r = build_article(fname)
            if r:
                slug, meta = r
                articles.append(meta)
                print(f"✅ {fname} → posts_html/{slug}.html")
        except Exception as e:
            print(f"❌ {fname} 转换失败: {e}")
    build_index(articles)
    print(f"\n🎉 构建完成: {len(articles)} 篇文章，首页 index.html 已更新")


if __name__ == '__main__':
    main()
