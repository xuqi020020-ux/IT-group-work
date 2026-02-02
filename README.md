NoteHub – Collaborative Document Management System
 
中文说明
项目简介
NoteHub 是一个基于 Django 的多用户协作文档管理系统，支持文档创建、分享、评论、修改建议以及管理员内容治理功能。
该系统旨在模拟一个小型组织内部的知识管理与协作平台。
 
核心功能
用户系统
•	登录 / 登出
•	管理员与普通用户角色
文档管理
•	创建 / 查看 / 编辑 / 删除
•	文档归属与更新时间
权限与可见性
•	Private / Shared / Public / Moderated
文档分享
•	指定用户名分享
•	Shared With Me 页面
修改建议
•	副本提交
•	Owner 审核 Accept / Reject
评论系统
•	评论 / 删除评论
搜索功能
•	按标题 / 作者搜索
•	权限过滤结果
文件附件
•	上传 / 下载 / 删除附件
管理员治理
•	批量打回文档
•	删除用户时自动治理文档
 
技术栈
•	Django 2.x
•	SQLite
•	Bootstrap 5
•	Git / GitHub
 
运行方式
conda activate rango
python manage.py migrate
python manage.py runserver
访问：
http://127.0.0.1:8000
管理员后台：/admin/
 
English Description
Project Overview
NoteHub is a Django-based multi-user collaborative document management system.
It supports document creation, sharing, comments, edit suggestions, file attachments, and administrative governance.
The system simulates an internal knowledge-sharing platform for small organizations.
 
Core Features
User System
•	Login / Logout
•	Admin and Normal User roles
Document Management
•	Create / Read / Update / Delete
•	Ownership tracking
Visibility & Access
•	Private / Shared / Public / Moderated
Document Sharing
•	Share with specific users
•	“Shared With Me” dashboard
Edit Suggestions
•	Copy-based suggestion mode
•	Owner Accept / Reject workflow
Comments
•	Add and delete comments
Search
•	Search by title and author
•	Permission-aware results
Attachments
•	Upload / Download / Delete files
Admin Governance
•	Batch moderation of documents
•	User deletion with document transfer rules
 
Tech Stack
•	Django 2.x
•	SQLite
•	Bootstrap 5
•	Git / GitHub
 
How to Run
conda activate rango
python manage.py migrate
python manage.py runserver
Open:
http://127.0.0.1:8000
Admin panel:/admin/

