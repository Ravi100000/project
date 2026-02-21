# FleetFlow

Lightweight fleet management Django app used for demos and testing.

Quick start (Windows / PowerShell)

1. Create & activate virtualenv

```powershell
cd C:\Users\ADMIN\PycharmProjects\Project\FleetFlow
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Apply migrations and seed demo data

```powershell
python manage.py migrate
python seed_data.py
```

4. Run development server

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000 — default admin printed by seeder: `admin` / `admin123`.

Using PostgreSQL

- Edit or create a `.env` in the project root to set `USE_SQLITE=False` and your Postgres settings (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
- A helper script is provided at `scripts/migrate_to_postgres.ps1` to dump current SQLite data to `fixtures/all_data.json`, create the Postgres DB/user (if `psql` is available), install the driver, run migrations and load the fixture. Review the script before running.

Example `.env` (DO NOT commit credentials to Git):

```
SECRET_KEY=change-me-for-prod
DEBUG=False
USE_SQLITE=False
DB_NAME=fleetflow_db
DB_USER=fleetflow_user
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=5432
```

Notes & troubleshooting

- The project defaults to SQLite when `USE_SQLITE=True` (recommended for local development).
- On Windows installing `psycopg2-binary` may require Visual C++ Build Tools. If you prefer, use `psycopg[binary]` or run the project with SQLite.
- Seed data lives in `seed_data.py`. A full JSON fixture is produced at `fixtures/all_data.json` when migrating to Postgres.
- If you accidentally moved or archived `db.sqlite3`, check the `removed_data/` folder created by the migration helper.

Testing

```powershell
python manage.py test
```

Security

- Never commit `.env` with secrets. Add `.env` to `.gitignore` if needed.

Questions or next steps

- Want me to create a GitHub-ready README with badges and CI examples? I can add them.
