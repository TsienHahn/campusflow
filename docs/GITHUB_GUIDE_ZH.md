# 将项目完整展示在 GitHub

建议仓库名：`campusflow-student-dashboard`。
建议 Description：

> SQL-backed student dashboard with Python, SQLite and JavaScript. Course enrollment, learning analytics, persistent tasks and a GitHub Pages demo.

建议 Topics：`python`, `sqlite`, `sql`, `dashboard`, `student-management`,
`javascript`, `data-visualization`, `portfolio-project`。

## 1. 上传仓库

解压后，用 VS Code 打开 **campusflow 文件夹本身**。README.md 和 app.py 应位于仓库根目录。
先在 GitHub 创建一个空仓库，不自动添加 README，然后在 VS Code 终端执行：

```powershell
git init
git add .
git commit -m "Build SQL-backed CampusFlow student dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/campusflow-student-dashboard.git
git push -u origin main
```

把 YOUR_USERNAME 换成你的真实用户名。若已有 Git 仓库，直接 add/commit/push，
不重复 init 或添加 origin。使用 Git 能保留 `.github/workflows` 等隐藏目录，
比网页拖放更适合上传完整项目。数据库不提交；首次启动会自动创建虚构数据。

## 2. 开启可点击演示

1. 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
2. 打开 Actions → **Deploy demo to Pages** → Run workflow → 选择 main。
3. 等工作流成功，打开部署结果中的实际页面 URL。
4. 把该 URL 放到仓库 About 的 Website 字段，并添加到 README 的 Explore the result 部分。

演示可浏览七个页面并搜索课程；它使用真实 SQL 导出的 JSON 快照，是只读页面。
GitHub Pages 不运行 Python。要演示保存资料、选课和任务状态，必须本地运行完整项目。
请勿把静态演示描述成连接在线数据库的完整后端服务。

## 3. 让别人快速理解过程和结果

README 已整理：问题 → 功能 → 架构 → 复现实验 → 开发阶段 → 测试 → 局限。
进一步阅读 docs/CASE_STUDY.md、docs/DATABASE.md 和 docs/VALIDATION.md。
原始中文概念图标注为概念；不冒充实际英文项目截图。

启动本地项目后，可自行截取实际英文 Overview、Course Selection 和 Learning Analytics，
放入 docs/assets/，再在 README 中添加相对图片链接。截图前使用虚构数据。
建议录制 20–30 秒操作：3门课 → 选课 → 4门课 → 课表更新 → 刷新仍保留。
本包未伪造浏览器截图或操作录像。

## 4. 展示真实开发过程

当前包是完整实现，不应拆成虚构的过去提交或倒填开发日期。
从首次上传开始保留真实的增量 commit：例如增加登录、接入 MySQL、增加教师端、
修复发现的问题。可以为这些后续工作创建 GitHub Issues，再用 PR 关联解决。
CHANGELOG 记录当前版本，不声称存在未发生的历史。

## 5. 本地检查

```powershell
python -m unittest -v test_app
python app.py
```

测试工作流会在每次 push 和 PR 时运行。首次运行后检查 Actions 的真实结果，
不要仅凭配置文件宣称已经通过 GitHub CI。
