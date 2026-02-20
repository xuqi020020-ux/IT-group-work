部署中出现问题：用户功能页面无法正常退出；管理员界面页面设计无法正常显示（已修复
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

## NoteHub – Collaborative Document Management System

---

### 中文说明

#### 项目简介

NoteHub 是一个基于 Django 的多用户协作文档管理系统，支持文档创建、分享、评论、修改建议以及管理员内容治理功能。

该系统旨在模拟一个小型组织内部的知识管理与协作平台。

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

---

### 技术栈

* Django 2.x
* SQLite
* Bootstrap 5
* Git / GitHub

---

### 运行方式

```bash
conda activate rango
python manage.py migrate
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

## English Description

### Project Overview

NoteHub is a Django-based multi-user collaborative document management system.
It supports document creation, sharing, comments, edit suggestions, file attachments, and administrative governance.

The system simulates an internal knowledge-sharing platform for small organizations.

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
* “Shared With Me” dashboard

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

---

### Tech Stack

* Django 2.x
* SQLite
* Bootstrap 5
* Git / GitHub

---

### How to Run

```bash
conda activate rango
python manage.py migrate
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
