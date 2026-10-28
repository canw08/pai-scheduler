# PAI Scheduler

A course scheduling application built with Vue 3 and Django, featuring WACE and ASE workflows, timetable editing, and Excel exports.

## Features

- **User authentication:** A custom Django user model with JWT authentication through SimpleJWT.
- **Projects and presets:** Create scheduling projects, configure presets, and import preset data.
- **Automatic scheduling:** Run WACE and ASE scheduling tasks in Python threads and query their status.
- **Timetable views:** View WACE timetables by class or teacher and adjust ASE timetables with drag and drop.
- **Excel exports:** Export timetables from both scheduling workflows.

Some pages still contain placeholder buttons. Available functionality depends on the current implementation.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Vue 3, TypeScript, Vite 6, Element Plus, UnoCSS, Pinia, Vue Router |
| Client utilities | Axios, SheetJS, Three.js for selected pages |
| Backend | Django 5.1.7, Django REST Framework, SimpleJWT, django-cors-headers |
| Data processing | NumPy, Pandas, OpenPyXL |
| Database | SQLite at `backend/paiclass/db.sqlite3` |

## Project Structure

```text
pai/
├── backend/paiclass/
│   ├── manage.py
│   ├── requirements.txt
│   ├── paiclass/        # Django settings and root URL configuration
│   ├── users/           # Users and authentication
│   ├── projects/        # Scheduling projects
│   ├── presets/         # Presets and format conversion
│   └── scheduler/       # WACE / ASE algorithms and task endpoints
├── frontend/
│   ├── src/api.ts       # Backend API configuration
│   ├── src/pages/nav/   # Login, projects, and settings
│   ├── src/pages/wace/  # WACE scheduling workflow
│   ├── src/pages/ase/   # ASE scheduling workflow
│   ├── src/components/  # Shared components and layouts
│   ├── src/stores/      # Application state
│   └── package.json
└── start.bat            # Windows development launcher
```

## Getting Started

Recommended environment:

- Python 3.11 or later
- Node.js 20 or later
- pnpm 9.15.0, as declared in `frontend/package.json`

The following commands use Windows PowerShell and assume you start in the repository root.

### Backend

```powershell
cd backend/paiclass
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
# Optional: create a Django administrator
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

- Backend: `http://127.0.0.1:8000`
- Django administration: `http://127.0.0.1:8000/admin/`

### Frontend

Open another terminal at the repository root:

```powershell
cd frontend
pnpm install
pnpm dev
```

Visit `http://localhost:5173`.

The API client in `frontend/src/api.ts` currently targets `http://127.0.0.1:8000`. The backend CORS configuration allows `http://localhost:5173`. Update the Django settings if you change the frontend address or port.

### Windows Launcher

After installing backend dependencies and applying database migrations, double-click `start.bat` in the repository root.

The launcher expects the virtual environment at `backend/paiclass/venv`. An existing environment at `backend/venv` does not satisfy this requirement. If frontend dependencies are missing, the launcher runs `pnpm install`.

Close the corresponding service terminals to stop the development servers.

## Development Commands

Run these commands in `frontend/`:

```powershell
pnpm typecheck
pnpm lint
pnpm build
pnpm preview
```

Run these commands in `backend/paiclass/`:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test
```

These are the available validation commands; their presence does not imply that all checks currently pass.

## API Entry Points

| Path | Purpose |
| --- | --- |
| `/api/users/` | User operations |
| `/api/presets/` | Preset operations |
| `/api/token/refresh/` | Refresh a JWT access token |
| `/api/project/` | Project operations |
| `/api/project/run/` | Start a scheduling task |
| `/api/project/run/status/` | Query scheduling task status |
| `/api/project/fitness/` | Evaluate timetable fitness |

Refer to each Django application's `urls.py` and `views.py` for HTTP methods, request parameters, and authentication requirements.

The current Django settings target local development. Configure a separate secret key, allowed hosts, and production settings before deployment.

## Repository Management

The repository root manages both `backend/` and `frontend/` as ordinary directories in a single Git repository.

```powershell
git status
git add .
git commit -m "Update frontend and backend"
```

Local backups of the previous nested repositories are stored in `.git-backups/`, including `backend.git`, `frontend.git`, and `frontend-paiclass.git`. This directory is ignored by Git. Previous commit histories remain in those backups and have not been imported into the root repository's history.

The root repository does not currently have a remote configured. Configure the intended remote before pushing. The frontend's previous remote configuration remains in its backup and is not automatically applied to the root repository.

Keep virtual environments, dependencies, SQLite databases, caches, and build output out of version control.
