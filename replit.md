# NoteHub

## Overview
NoteHub is a Django-based document management and collaboration platform. Users can create, edit, share, and comment on documents. It includes features like edit suggestions, document attachments, and content moderation.

## Project Architecture
- **Framework**: Django 5.x (Python 3.11)
- **Database**: PostgreSQL (via DATABASE_URL environment variable)
- **Config module**: `config/` (settings, urls, wsgi)
- **Main app**: `core/` (models, views, forms, urls, admin, seed data)
- **Templates**: `templates/` (base.html + core/ and registration/ subdirectories)

## Key Files
- `config/settings.py` - Django settings (DB config, allowed hosts, CSRF)
- `config/urls.py` - Root URL configuration
- `core/models.py` - Data models (Document, EditSuggestion, Comment, DocumentAttachment)
- `core/views.py` - View logic
- `core/forms.py` - Form definitions
- `core/seed.py` - Default user seeding script
- `manage.py` - Django management command entry point

## Default Users (seeded)
- **manager** / manager@10086 (admin/superuser)
- **test01** / groupmember01
- **test02** / groupmember02
- **test03** / groupmember03

## Running
- Development: `python manage.py runserver 0.0.0.0:5000`
- Production: `gunicorn --bind=0.0.0.0:5000 config.wsgi:application`

## Recent Changes
- 2026-02-17: Imported and configured for Replit environment
  - Set ALLOWED_HOSTS to ['*'] for Replit proxy compatibility
  - Added CSRF_TRUSTED_ORIGINS for Replit domains
  - Set X_FRAME_OPTIONS = 'ALLOWALL' for iframe embedding
  - Configured PostgreSQL database connection (removed ssl_require for Replit DB)
  - Added DEFAULT_AUTO_FIELD for Django 5.x compatibility
  - Added gunicorn for production deployment
