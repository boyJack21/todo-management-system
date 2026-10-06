# Todo Management System

A full-stack task management application built with Django REST Framework, Vue 3, PostgreSQL, and JWT authentication.

## Overview

The application provides a personal workspace where authenticated users can organise work into projects and tasks, track priorities and due dates, add subtasks, and switch between list, Kanban, calendar, and analytics views.

## Key features

- User registration and JWT-based authentication
- User-scoped projects, tasks, and subtasks
- Task priority, status, notes, due dates, recurrence, and reminders
- Kanban, calendar, list, and analytics views
- Password-reset workflow with email support
- PostgreSQL persistence
- Responsive Vue 3 frontend
- REST API built with Django REST Framework

## Architecture

```text
Vue 3 / Vite frontend
        |
        | HTTP + JWT
        v
Django REST Framework API
        |
        v
PostgreSQL
```

The backend enforces ownership at the queryset and serializer layers so authenticated users can only access their own projects, tasks, and subtasks.

## Tech stack

**Backend:** Python, Django, Django REST Framework, SimpleJWT, PostgreSQL  
**Frontend:** Vue 3, Vue Router, Axios, Vite  
**Development:** Git, REST APIs, environment-based configuration

## Local setup

### Backend

```bash
cd backend
python -m venv env
source env/bin/activate   # Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Update `backend/.env` with your PostgreSQL credentials.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The frontend reads the backend URL from `VITE_API_BASE_URL`.

## Security notes

- Application secrets and database passwords are loaded from environment variables.
- JWT authentication protects user-specific API routes.
- Project and task ownership is validated server-side.
- Password-reset responses do not reveal whether a reset email was actually sent.

## What I focused on

This project was built to practise end-to-end application development: designing relational models, exposing authenticated REST endpoints, enforcing per-user data access, building a stateful frontend, and connecting the frontend to a PostgreSQL-backed Django API.
