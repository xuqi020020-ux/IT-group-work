# NoteHub – Document Collaboration System

# NoteHub —— 文档协作管理系统

---

## 1. Project Overview ｜ 项目概述

**EN**

NoteHub is a lightweight web-based document management and collaboration system built with **Django**.
It allows users to create, edit, share, comment on documents, and submit edit suggestions.
The system also includes role-based permissions and an administrator panel for user and document management.

**中文**

NoteHub 是一个基于 **Django** 构建的轻量级网页文档管理与协作系统。
用户可以创建、编辑、分享文档、发表评论以及提交修改建议。
系统包含基于角色的权限控制，以及管理员后台用于用户与文档管理。

---

## 2. Tech Stack ｜ 技术栈

| Category        | Technology               |
| --------------- | ------------------------ |
| Backend         | Django 2.x               |
| Database        | SQLite                   |
| Frontend        | HTML / CSS / Bootstrap 5 |
| Version Control | Git & GitHub             |
| Environment     | Anaconda / Python 3.7+   |

---

## 3. Core Features ｜ 核心功能

### 3.1 User System ｜ 用户系统

**EN**

* User login / logout
* Admin and normal user roles
* Password setup for first login
* Django admin panel support

**中文**

* 用户登录 / 登出
* 管理员与普通用户角色区分
* 首次登录可设置密码
* 支持 Django 管理后台

---

### 3.2 Document Management ｜ 文档管理

**EN**

* Create, edit, delete documents
* Dashboard document list
* Visibility control: `Private / Shared / Public / Moderated`

**中文**

* 创建、编辑、删除文档
* 仪表盘文档列表
* 可见性控制：`私密 / 共享 / 公开 / 审核中`

---

### 3.3 Comment System ｜ 评论系统

**EN**

* Users can comment on accessible documents
* Private documents restrict comment visibility

**中文**

* 用户可以对可访问文档发表评论
* 私密文档限制评论查看权限

---

### 3.4 Edit Suggestions ｜ 修改建议

**EN**

* Users can submit edit suggestions
* Document owner can **Accept / Reject**
* Accepted suggestions automatically update document content

**中文**

* 用户可以提交修改建议
* 文档所有者可 **接受 / 拒绝**
* 接受后自动更新文档内容

---

### 3.5 Search Function ｜ 搜索功能

**EN**

* Search by **Document Title**
* Search by **Author Name**
* Permission-aware results:

  * Admin: all documents
  * Owner: own + shared + public
  * User: shared + public

**中文**

* 按 **文档标题** 搜索
* 按 **作者名** 搜索
* 权限控制搜索结果：

  * 管理员：全部文档
  * 所有者：自己 + 被分享 + 公开
  * 普通用户：被分享 + 公开

---

### 3.6 Admin Management ｜ 管理员管理

**EN**

* Manage users
* Delete users and handle their documents
* Moderate documents

**中文**

* 管理用户账号
* 删除用户并处理其文档
* 审核文档内容

---

## 4. Project Structure ｜ 项目结构

```
NoteHub/
├── config/        # Django project settings
├── core/          # Main application logic
├── templates/     # HTML templates
├── db.sqlite3     # Database
└── manage.py
```

---

## 5. How to Run ｜ 运行方式

### 5.1 Environment Setup ｜ 环境准备

```bash
conda create -n rango python=3.7
conda activate rango
pip install django
```

---

### 5.2 Start Project ｜ 启动项目

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open browser:

```
http://127.0.0.1:8000/
```

---

## 6. Screenshots（Temporarily vacant） 

* Login Page
* Dashboard
* Document Detail
* Suggestion Review
* Admin Panel


---

## 7. Future Improvements ｜ 后续改进方向

**EN**

* AI document summarization
* Notification system
* File upload support
* UI theme customization

**中文**

* AI 文档摘要
* 通知系统
* 文件上传支持
* UI 主题定制

---

## 8. Author ｜ 作者

**Name:** Qi Xu
**Course:** Web Systems / ITECH
**Year:** 2026

---
