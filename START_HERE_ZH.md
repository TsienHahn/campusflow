# CampusFlow 启动说明

这是完整的英文版学生 Dashboard 项目，使用 **Python + SQLite + HTML/CSS/JavaScript**。
不需要安装第三方 Python 包，也不需要 npm。所有界面数据由后端从 SQL 数据库读取。

## 运行

1. 安装 Python 3.10 或更高版本。
2. 解压项目包，进入包含 `app.py` 的 `campusflow` 文件夹。
3. 在 VS Code 中打开这个文件夹，再打开终端，运行：

```powershell
python app.py
```

Windows 如果不识别 python，可以运行 `py app.py`。

4. 浏览器打开 **http://127.0.0.1:8000**。
5. 用 Ctrl+C 关闭服务。

不要双击 index.html；页面需要 Python 接口。

## 可以操作的功能

- Overview：查看学习进度、学分、GPA、本周学习时长、待办和今日课表。
- My Profile：编辑姓名和邮箱，保存到数据库。
- Course Selection：搜索、选课、退课；自动检查课程名额和时间冲突。
- My Courses：查看在读课程和进度；Details 展示课程说明。
- Learning Analytics：查看 SQL 学习记录生成的趋势。
- Grades & Credits：查看已完成和在读课程、学分、成绩。
- Timetable：根据选课结果生成一周课表。
- 待办复选框：更新 SQL 中的完成状态。

数据库文件是 `data/campusflow.db`，SQL 表结构在 `schema.sql`。
修改数据库后刷新页面即可查看最新结果。启动不会覆盖已有数据。
例如选修 Data Visualization，Overview 的课程数量会增加；退课后减少。
Artificial Intelligence 与 Machine Learning 有时间冲突，会拒绝选课并解释原因。

这是单学生本地演示，使用虚构数据和 4.0 制 GPA。未加入登录、真实学校数据接口、
课程视频、教师录分或自动学习时长采集。学习记录、成绩和进度可以通过 SQL 修改。
如需接入你已有的 MySQL／SQL Server／PostgreSQL，需要提供表结构，适配后端数据层。

完整英文文档、接口和修改 SQL 的例子见 README.md。
测试命令：`python -m unittest -v test_app`，使用独立临时数据库。
