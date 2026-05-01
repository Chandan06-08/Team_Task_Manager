# Ethara Task Management

A Django-based task and project management app with a modern corporate UI, REST API support, and role-based access control.

## Key Features

- User signup, login, and session-based authentication
- Project creation and membership management via `Membership` roles
- Task creation, assignment, status tracking, priority levels, and due dates
- Dashboard summaries and project detail pages with improved layout and visual hierarchy
- REST API endpoints for Users, Projects, and Tasks
- Project-level role-based access control: `ADMIN` and `MEMBER`

## Architecture

- Django with Django REST Framework
- SQL-backed models using Django ORM
- Project–Membership–Task relationships with proper foreign keys and join tables
- API serializers enforce relationship validation and project membership

## Setup

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Run database migrations:
   ```bash
   python manage.py migrate
   ```
3. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Environment

Create a `.env` file or set environment variables for production deployment:

- `DJANGO_SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`
- `DATABASE_URL` (for PostgreSQL on Railway or other hosts)

## Deployment

Railway deployment steps:

1. Connect your GitHub repository to Railway.
2. Ensure `requirements.txt` includes `gunicorn`, `dj-database-url`, and `whitenoise`.
3. Verify `Procfile` contains:
   ```text
   web: gunicorn ethara.wsgi --log-file -
   ```
4. Set Railway environment variables:
   - `DJANGO_SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS`
   - `DATABASE_URL`
5. Run migrations after deploy:
   ```bash
   railway run python manage.py migrate
   railway run python manage.py collectstatic --noinput
   ```

## API Endpoints

The app exposes a REST API under `/api/`:

- `GET /api/users/`
- `GET /api/projects/`
- `POST /api/projects/`
- `GET /api/tasks/`
- `POST /api/tasks/`

### Permissions

- All API endpoints require authentication.
- API querysets are restricted to projects and tasks that belong to the authenticated user.
- Creating a project automatically assigns the creator as `ADMIN` for that project.
- Task validation ensures the task project belongs to the requesting user and the assignee is a project member.

## Models and Relationships

- `Project`
  - `creator` (User)
  - `members` via `Membership`
- `Membership`
  - `user`
  - `project`
  - `role` (`ADMIN` / `MEMBER`)
- `Task`
  - `project`
  - `assignee` (User)
  - `created_by` (User)

## Role-Based Access Control

- `ADMIN`: Can create projects, add or remove members, and manage tasks
- `MEMBER`: Can view assigned projects and interact with tasks belonging to their projects

## Frontend UI

- Uses modern card-style dashboard and two-column project detail layout
- Glass-style form inputs with stronger focus states
- Hover lift, subtle motion, and responsive buttons for a polished corporate feel

## Notes

- This project currently uses Django ORM with SQL-backed models.
- NoSQL backends are not configured by default.
- The app is structured for easy extension with additional REST API permissions and richer RBAC logic.
