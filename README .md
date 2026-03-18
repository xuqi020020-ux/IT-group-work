# NoteHub – Collaborative Document Management System

---

## English Description

### Project Overview

NoteHub is a Django-based multi-user collaborative document management system.
It supports document creation, sharing, comments, edit suggestions, file attachments, and administrative governance.

The system simulates an internal knowledge-sharing platform for small organizations.

---

### Deployment Issues

User function page could not log out properly; Admin interface page design was not displaying correctly (fixed)

**1. `config/settings.py`**
- Added `whitenoise` middleware — lets WhiteNoise take over static file serving, fixing the missing CSS in the admin interface
- Added `STATIC_ROOT` and `STATICFILES_STORAGE` — tells Django where to store collected static files and to use WhiteNoise for compressed storage
- Changed `DEBUG` to be controlled by an environment variable
- Added `CSRF_TRUSTED_ORIGINS` — makes Django trust the Replit domain, preventing POST requests from being blocked by CSRF validation

**2. `requirements.txt`**
- Added `whitenoise` — serves static files (CSS, JS, images) directly in production without needing Nginx/Apache
- Added `gunicorn` — production WSGI server used to run Django on Replit

**3. `templates/base.html`**
- Changed the logout `<a>` link to a `<form method="post">` with a CSRF token
- Django 5.x security updates require logout to use POST requests; GET requests return a 405 error. (This project originally used Django 2.x to align with textbook content)

---

### Feature Updates

1. Modified `templates/base.html` to display "Dashboard" as a standalone text link in the navbar inside the `<nav>` tag, and changed the `<a>` tag to a `<span>` tag so the NoteHub logo becomes purely decorative text.

2. Using Bootstrap 5's built-in colour classes `bg-primary`, `text-white`, and `rounded px-2`, modified the link section inside the `<nav>` tag in `templates/base.html` to highlight the navbar button corresponding to the current page.

3. Added `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` in `config/settings.py` so that closing the browser immediately logs the user out, requiring re-login on the next visit (not guaranteed to trigger in all cases).

4. Installed the `django-simple-captcha` library, modified `config/settings.py`, configured `config/urls.py`, created a form in `core/forms.py`, updated the `templates/registration/login.html` frontend template, and synced the database — adding a graphical CAPTCHA to the login page via a third-party library.

5. Using the `Pillow` image processing library: extended the user profile model (`core/models.py`), created a profile editing form (`core/forms.py`), wrote backend view logic (`core/views.py`), configured routing (`core/urls.py`), created the frontend profile editing page (`templates/core/profile.html`), updated the navbar to replace the username with an avatar (`templates/base.html`), and ran database migrations — implementing a personalised user profile page (nickname, avatar, bio) accessible by clicking the avatar in the navbar.

6. Extended the database model (`core/models.py`), created a settings form (`core/forms.py`), wrote settings view logic (`core/views.py`), registered routes (`core/urls.py`), applied user settings globally and added a gear icon (`templates/base.html`), and created the settings page with interactive scripts (`templates/core/settings.html`), followed by database migration — implementing a settings page accessible via a gear icon at the far right of the navbar. The settings page includes modules for Page Display, Brightness, Special Features, and Account Management.

7. Using the Web Speech API, added a conditional check in `document_detail.html`: if the current user has enabled the feature, a "🔊 Read Aloud" button is displayed along with the corresponding JavaScript speech script — implementing the text-to-speech feature under the Special Features module.

8. Added a notifications page accessible via a bell icon in the navbar, aggregating all in-site notifications (review / comment / edit suggestion / deletion notifications). Implemented by extending the database model (`core/models.py`), writing notification views and trigger logic (`core/views.py`), triggering notifications from existing views, updating the dashboard view to show a red dot badge on relevant files, configuring admin review notifications (`core/admin.py`), registering notification routes (`core/urls.py`), updating the global navbar and dashboard view, and running database migrations — the bell icon displays a red dot, and clicking into the dashboard shows a prominent red "New Activity" label on the corresponding documents.

9. *(If the admin CSS issue has already been fixed, this may not be needed)* Fixed missing CSS/static file issue in the Django admin panel, and applied the modern Jazzmin admin theme. Done by modifying `config/settings.py` to include the theme, and running `python manage.py collectstatic` in the terminal to collect CSS/JS files into the `staticfiles` folder.

---

### Core Features

**User System**

* Login / Logout
* Admin and Normal User roles

**Document Management**

* Create / Read / Update / Delete
* Ownership tracking

**Visibility & Access**

* Private / Shared / Public / Moderated

**Document Sharing**

* Share with specific users
* "Shared With Me" dashboard

**Edit Suggestions**

* Copy-based suggestion mode
* Owner Accept / Reject workflow

**Comments**

* Add and delete comments

**Search**

* Search by title and author
* Permission-aware results

**Attachments**

* Upload / Download / Delete files

**Admin Governance**

* Batch moderation of documents
* User deletion with document transfer rules

**Personalized User Information**

* Enter nickname / Change avatar / Enter personal information

**Page Settings**

* Adjust page size and text size
* Adjust page brightness
* Text-to-speech
* Account logout

**Message Notifications**

* Receive review notifications / comment notifications / attachment upload notifications / modification suggestion notifications
* Delete notifications
* One-click read confirmation
* Go to specific notification document

---

### Tech Stack

* Django 2.x
* SQLite
* Bootstrap 5
* Git / GitHub
* captcha
* Pillow
* jazzmin

---

### How to Run

```bash
conda activate rango
python manage.py migrate
python manage.py runserver
```

Update function execution method:

```bash
# 1. Delete the old database (Windows: del db.sqlite3, Mac/Linux: rm db.sqlite3)
rm db.sqlite3

# 2. Install all project dependencies
pip install -r requirements.txt

# 3. Generate migration files
python manage.py makemigrations

# 4. Execute the migration (seed.py will regenerate test accounts and automatically trigger signals to create their profiles)
python manage.py migrate

# 5. Run the server
python manage.py runserver

# 6. Run jazzmin
python manage.py collectstatic
# (when prompted whether to overwrite, type yes and press Enter)
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000
```

Admin panel:

```
/admin/
```

---

## 中文说明

### 项目简介

NoteHub 是一个基于 Django 的多用户协作文档管理系统，支持文档创建、分享、评论、修改建议以及管理员内容治理功能。

该系统旨在模拟一个小型组织内部的知识管理与协作平台。

---

### 部署问题

用户功能页面无法正常退出；管理员界面页面设计无法正常显示（已修复）

**1. `config/settings.py`**
- 添加了 `whitenoise` 中间件--让 whitenoise 接管静态文件服务，解决 admin 界面 CSS 丢失的问题
- 添加了 `STATIC_ROOT` 和 `STATICFILES_STORAGE`--告知 Django 静态文件收集后的存放位置，以及用 whitenoise 压缩存储
- 修改了 `DEBUG` 为环境变量控制
- 添加了 `CSRF_TRUSTED_ORIGINS`--使 Django 信任 Replit 域名，避免 POST 请求被 CSRF 验证拦截

**2. `requirements.txt`**
- 添加了 `whitenoise`--用于在生产环境直接提供静态文件（CSS、JS、图片），不需要额外的 Nginx/Apache
- 添加了 `gunicorn`--生产环境的 WSGI 服务器，用于Replit 部署运行 Django

**3. `templates/base.html`**
- 把 logout 的 `<a>` 链接改成了 `<form method="post">` 带 CSRF token
- Django 5.x 安全更新要求 logout 必须用 POST 请求，用 GET 请求会返回 405 错误。（而本项目最开始为了贴合教学内容，使用的是教材里提供的Django 2.x）

---

### 更新功能

1. 修改前端 `templates/base.html` 模板文件在 `<nav>` 标签内将"Dashboard"作为一个独立的文本链接显示在菜单栏中，把 `<a>` 标签改为 `<span>` 标签让导航栏上的 NoteHub 标志变成纯展示的文本。

2. 通过Bootstrap 5的内置颜色类：`bg-primary`、`text-white` 和 `rounded px-2`，修改 `templates/base.html` 内 `<nav>` 标签内包含链接的部分，实现高亮当前所在界面的菜单栏按钮。

3. 在 `config/settings.py` 文件内添加 `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`，实现关闭浏览器网页后立刻注销，下次打开必须重新登录（不能保证完全可以触发）。

4. 通过安装 `django-simple-captcha` 验证码库，修改 `config/settings.py`、配置 `config/urls.py`、创建 `core/forms.py` 表单、修改 `templates/registration/login.html` 的前端模板、同步数据库，实现在登录页面使用第三方库添加图形验证码。

5. 使用处理图像依赖 Pillow 库，增加用户资料模型（修改 `core/models.py`）、创建资料修改表单（修改 `core/forms.py`）、编写后端视图逻辑（修改 `core/views.py`）、配置路由（修改 `core/urls.py`）、创建前端修改界面（`templates/core/profile.html`）、修改导航栏将用户名替换为头像（修改 `templates/base.html`）、更新数据库，实现个性化配置基本用户信息（昵称、头像、个人资料图片）界面，点击菜单栏上的头像可以进入。

6. 扩展数据库模型（修改 `core/models.py`）、创建设置表单（修改 `core/forms.py`）、编写设置视图逻辑（修改 `core/views.py`）、注册路由（修改 `core/urls.py`）、全局应用用户设置和添加齿轮图标（修改 `templates/base.html`）、创建设置界面及交互脚本（新建 `templates/core/settings.html`）、更新数据库。实现了一个设置界面，位置在菜单栏最右边，是一个齿轮图案，点击这个图案后就可以进入设置界面。设置页面有"页面显示"模块、"网页亮度"模块、"特殊功能"模块和"账号管理"模块。

7. 使用Web Speech API，在 `document_detail.html` 中加入一个判断：如果当前用户开启了该功能，就显示一个"朗读"按钮（🔊 Read Aloud），并配上对应的发音 JavaScript 脚本。实现特殊功能模块的文本转语音功能。

8. 添加了一个通知界面，通过菜单栏的铃声图案进入。聚合用户站点内的所有通知（审核通知/评论通知/修改建议通知/删除通知）。通过扩展数据库模型（修改 `core/models.py`）、编写通知视图和触发逻辑（修改 `core/views.py`）、在原有的视图中触发通知、修改 dashboard 视图，为文件加上"动态"红点、配置管理后台的审核通知（修改 `core/admin.py`）、注册通知路由（修改 `core/urls.py`）、修改全局菜单栏和Dashboard视图和数据迁移，实现铃铛图案弹出红点，点进仪表盘，对应的文档也会贴上醒目的红色 New Activity 标签。

9. （如果已经修复好了，那就不用这个了吧）修复管理员后台CSS静态样式文件丢失问题，同时装饰现代化 Django Admin 主题 Jazzmin 主题。通过修改配置引入主题（`config/settings.py`）、在终端中执行 `python manage.py collectstatic` 命令将CSS/JS 文件收集到 staticfiles 文件夹。

---

### 核心功能

**用户系统**

* 登录 / 登出
* 管理员与普通用户角色

**文档管理**

* 创建 / 查看 / 编辑 / 删除
* 文档归属与更新时间

**权限与可见性**

* Private / Shared / Public / Moderated

**文档分享**

* 指定用户名分享
* Shared With Me 页面

**修改建议**

* 副本提交
* Owner 审核 Accept / Reject

**评论系统**

* 评论 / 删除评论

**搜索功能**

* 按标题 / 作者搜索
* 权限过滤结果

**文件附件**

* 上传 / 下载 / 删除附件

**管理员治理**

* 批量打回文档
* 删除用户时自动治理文档

**个性化用户信息**

* 填写昵称 / 修改头像 / 填写个人资料

**页面设置**

* 修改页面大小、文字大小
* 修改页面亮度
* 文字转语音
* 账户登出

**消息通知**

* 接收审核通知/评论通知/上传附件通知/修改建议通知
* 删除通知
* 一键已读
* 转到具体通知文档

---

### 技术栈

* Django 2.x
* SQLite
* Bootstrap 5
* Git / GitHub
* captcha
* Pillow
* jazzmin

---

### 运行方式

```bash
conda activate rango
python manage.py migrate
python manage.py runserver
```

更新功能运行方式：

```bash
# 1. 删除旧数据库（Windows用 del db.sqlite3，Mac/Linux用 rm db.sqlite3）
rm db.sqlite3

# 2. 安装所有项目依赖
pip install -r requirements.txt

# 3. 生成迁移文件
python manage.py makemigrations

# 4. 执行迁移（此时 seed.py 会重新生成测试账号，并自动触发信号创建出它们的 Profile）
python manage.py migrate

# 5. 运行服务器
python manage.py runserver

# 6. jazzmin运行方式
python manage.py collectstatic
# （当提示是否覆盖时，输入 yes 并回车）
python manage.py runserver
```

访问：

```
http://127.0.0.1:8000
```

管理员后台：

```
/admin/
```

---
