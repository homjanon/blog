# 老张随笔

投资思考 · 生活记录 · 老张的碎碎念

> 站点：**https://blog.hellohopo.dpdns.org**（GitHub Pages）

## 写作方式（两种任选）

### ① 网页在线编辑器（推荐，手机/电脑都能写）
打开 **https://blog.hellohopo.dpdns.org/write.html**：
- 按钮式编辑：加粗 / 小标题 / 列表 一键插入
- 右侧实时预览
- 填标题 + 选分类 + 发布密码 → 点「发布」即上线
- 发布密码在 Cloudflare Worker 环境变量 `WRITE_PASSWORD` 中配置

### ② WPS/Word 写（本地）
用 Word/WPS 写文章，保存为 `.docx`，放入 `posts/` 文件夹，跑 `python build.py` 自动转换。

## 目录结构

```
posts/            # 源文章（.docx 或 .md）
  └── 2026-08-08-标题.docx   # 命名规则：日期-标题
index.html        # 首页（自动生成）
posts_html/       # 文章页（自动生成）
write.html        # 在线编辑器
build.py          # 转换脚本（docx→HTML，mammoth 引擎）
.github/workflows/blog.yml   # 自动构建（push 后自动生成页面）
```

## 标签分类

- `投资随笔`（蓝色）— 投资思考、持仓复盘、策略笔记
- `生活记录`（绿色）— 生活感悟、备考、公文心得

## 自动构建

`posts/` 有更新（push 或在线发布）时，GitHub Actions 自动：
1. 安装依赖（mammoth / markdown / python-docx）
2. 跑 `build.py` 生成首页 + 文章页
3. 提交生成的 HTML → GitHub Pages 自动部署

## 免责声明

文章仅为个人记录，不构成投资建议。
