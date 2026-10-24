# 登录功能升级与运行

## 1. 停止旧服务并备份

在两个服务器终端分别按 Ctrl+C，停止 8000 和 8080 服务。
备份 E:\campusflow\data\campusflow.db，以及你自行修改过的源码。

## 2. 更新文件

将压缩包中的 campusflow 文件夹内容复制到 E:\campusflow，合并覆盖同名源码。
包中不包含数据库，不需要删除或覆盖 data 文件夹中的数据库。
请确保 app.py、schema.sql、static 下的文件和 scripts/build_demo.py 均更新，
不要仅复制 login.html。

## 3. 启动完整版本

```powershell
cd E:\campusflow
python -X utf8 app.py
```

浏览器访问 http://127.0.0.1:8000 ，自动进入 /login。

- Username: alex.morgan
- Password: CampusFlow2026!

可以点击 Use demo credentials 填充账号，然后点击 Sign in。
登录后可操作 Dashboard，右上角 Sign out 退出。
会话 8 小时后过期，退出后原会话立即失效。
资料里的联系邮箱与登录用户名分开，修改联系邮箱不改变登录账号。

启动时会自动创建 accounts 和 sessions 表，并为 ID=1 的原有演示学生创建账号。
已有账号不会在启动时重置，已有学生、选课、任务和学习记录会保留。
密码以 PBKDF2-HMAC-SHA256 加随机盐保存；数据库不保存明文密码。
这是本机演示账号，不用于真实学校部署；现已包含注册（/register），不包含重置密码或管理员账号管理页面。

## 4. 更新静态演示

```powershell
python -X utf8 scripts\build_demo.py
python -m http.server 8080 --bind 127.0.0.1 --directory docs/demo
```

打开 http://127.0.0.1:8080 ：先展示同风格的演示入口，点击 Open demo workspace。
静态入口不验证密码，页面明确标记只读。真实登录在 8000 的 Python 应用中。
如果浏览器显示旧内容，按 Ctrl+F5 刷新。

## 5. 检查与提交

```powershell
python -m unittest -v test_app
git add .
git commit -m "Add student login, sessions and sign out"
git push
```

如已开启 Pages，再到 Actions 手动运行 Deploy demo to Pages 工作流。
完整本地版本的登录功能不会在静态 Pages 中运行。
