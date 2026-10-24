# 注册功能更新说明

1. Ctrl+C 停止旧 Python 服务，备份 E:\campusflow 和 data\campusflow.db。
2. 将更新包 campusflow 里的内容合并到 E:\campusflow，覆盖源码；保留原数据库。
3. 不要只复制 register.html：需要一起更新 app.py、static/ 和 scripts/build_demo.py。
4. 启动：

```powershell
cd E:\campusflow
python -X utf8 app.py
```

打开 http://127.0.0.1:8000/login ，点击 Create an account。
也可以直接打开 http://127.0.0.1:8000/register 。

## 注册信息

- Full name：姓名，1–80 字符。
- Email address：有效格式邮箱，仅作为联系资料；本地演示不发送验证邮件。
- Username：3–32 字符，字母、数字、点、下划线或短横线，以字母或数字开头。
  自动转成小写保存，不能与已有用户名重复；登录使用用户名，不是邮箱。
- Study program：Computer Science / Data Science / Software Engineering。
- Password：10–128 字符。
- Confirm password：必须与密码一致。

点击 Create account 后跳回登录页，显示创建成功提示。使用新账号登录。
学号自动生成；初始学期为 1、目标为 120 学分。新用户的课程、任务和学习记录为空，
GPA 显示为横线，学分和学习时长为零。可以在 Course Selection 中选课。
密码以带随机盐的哈希保存，不保存明文。

## 建议验收步骤

1. 注册一个新用户并登录。
2. 检查姓名、专业与注册信息一致，首页不存在 Alex 的课程或记录。
3. 选一门课程，刷新后确认保留。
4. Sign out 后重新登录，确认数据仍保留。
5. 重复注册相同用户名，确认收到提示。
6. 填写不同的两次密码，确认无法注册。

## 静态演示

```powershell
python -X utf8 scripts\build_demo.py
python -m http.server 8080 --bind 127.0.0.1 --directory docs/demo
```

8080 / GitHub Pages 是只读展示，不运行注册、登录 API，也不采集账号密码。
注册功能在 8000 的完整版本中运行。浏览器旧缓存可用 Ctrl+F5 刷新。

## 测试与 GitHub 提交

```powershell
python -m unittest -v test_app
git add .
git commit -m "Add student registration and isolated new workspaces"
git push
```

当前本地版本不包含邮箱验证、找回密码或公开服务所需的滥用防护。
