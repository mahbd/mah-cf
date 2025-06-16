# Codeforces Dashboard (mah-cf)

A full-stack web application that aggregates Codeforces problem and submission data for registered users. The backend is built with Django and Django REST Framework, and the frontend is a React single-page application.

## Features

- **User Management**: Register Codeforces handles, track solve counts and submission stats.
- **Problem Listing**: List all tracked Codeforces problems with solver statistics.
- **Submission Listing**: View submissions filtered by user handle or user batch.
- **External Sync**: Periodically fetch user submissions from the Codeforces API and update local records.
- **Frontend Integration**: Serve a React build for a modern UI.

## Prerequisites

- Python 3.9+ (tested on 3.10/3.11)
- Node.js & npm (for front-end development)
- PostgreSQL (or any Django-supported database)

## Setup & Installation

1. **Clone the repository**

```powershell
git clone <repository_url> e:\django\mah-cf
cd e:\django\mah-cf
```

2. **Create a Python virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

3. **Install Python dependencies**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment / settings**

- Update `config.py` or set environment variables for:
  - `SECRET_KEY`
  - Database connection (e.g., `DATABASE_URL`)

5. **Run database migrations**

```powershell
python manage.py migrate
```

6. **(Optional) Create a superuser**

```powershell
python manage.py createsuperuser
```

7. **Build / Serve the Frontend**

If you have the React source:

```powershell
cd cf_front
npm install
npm run build
```

The production build is output to `cf_front/build` and served by Django at the root URL.

8. **Run the development server**

```powershell
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/api/` and the React app at `http://localhost:8000/`.

## API Endpoints

### Authentication

- `POST /api/login/` — authenticate with Django credentials; returns a JWT.
- `POST /api/logout/` — invalidate session.

### Users

- `GET /api/users/` — list all users (registered Codeforces handles).
- `POST /api/users/` — register a new user with a CF handle.
- `GET /api/users/id=<pk>/` — retrieve, update or delete a user.

### Problems

- `GET /api/problems/` — list all tracked problems.
- `GET /api/problems/cf_handle=<handle>/` — problems solved by a specific user.
- `GET /api/problems/batch=<batch>/` — problems solved by a batch of users.

### Submissions

- `GET /api/submissions/` — list all submissions.
- `GET /api/submissions/cf_handle=<handle>/` — submissions for a specific user.
- `GET /api/submissions/batch=<batch>/` — submissions for a user batch.

### React Feed (legacy)

- `GET /cf/get_list/start=<start>end=<end>/` — returns paginated problem list for frontend.

### External Sync (admin)

- `GET /external/cf/usa/handle=<handle>/` — sync submissions for a single user (async).
- `GET /external/cf/uaa/` — sync submissions for all users (async).
- `POST /external/add_cf_handle/` — bulk add new CF handles.
- `GET /external/transfer_problems/` — transfer local problem data to an external service.

## Running Tests

```powershell
python manage.py test api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with tests and documentation

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
