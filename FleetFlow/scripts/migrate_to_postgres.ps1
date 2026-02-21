<#
PowerShell helper to migrate local SQLite data to PostgreSQL for FleetFlow.

How it works:
- Dumps current data from the SQLite DB (runs with USE_SQLITE=1)
- Attempts to create the Postgres user/database via `psql` (if available)
- Writes a .env file (if missing) with DB settings (password 12345)
- Installs `psycopg2-binary` into the virtualenv if needed
- Runs `manage.py migrate` against Postgres and loads the dumped fixture
- Archives `db.sqlite3` and data files into `removed_data/` after success

Usage (PowerShell):
    cd <project root>
    .venv\Scripts\Activate.ps1
    .\scripts\migrate_to_postgres.ps1

Notes:
- You must have PostgreSQL server running locally and `psql` on PATH for automatic DB/user creation.
- If `psql` is not available, create the DB/user manually (see instructions below).
#>

Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $projectRoot

Write-Host "1) Dumping current data from SQLite to fixtures/all_data.json"
New-Item -ItemType Directory -Force -Path fixtures | Out-Null

# Run dumpdata using the existing SQLite DB by forcing USE_SQLITE=1
$env:USE_SQLITE = 'True'
python manage.py dumpdata --natural-foreign --natural-primary --exclude auth.permission --exclude contenttypes --indent 2 > fixtures/all_data.json
if ($LASTEXITCODE -ne 0) {
    Write-Error "dumpdata failed. Aborting."
    Pop-Location
    exit 1
}
Remove-Item Env:USE_SQLITE

Write-Host "2) Ensuring .env exists (will not overwrite existing .env)"
if (-Not (Test-Path .env)) {
    @"
SECRET_KEY=change-me-for-prod
DEBUG=False
USE_SQLITE=False
DB_NAME=fleetflow_db
DB_USER=fleetflow_user
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=5432
"@ | Out-File -FilePath .env -Encoding utf8 -Force
    Write-Host ".env created with PostgreSQL settings (DB_PASSWORD=12345)."
} else {
    Write-Host ".env already exists — please ensure it contains correct Postgres settings." -ForegroundColor Yellow
}

Write-Host "3) Attempting to create Postgres user/database (requires psql on PATH and a postgres superuser)."
if (Get-Command psql -ErrorAction SilentlyContinue) {
    try {
        psql -c "CREATE USER fleetflow_user WITH PASSWORD '12345';" -U postgres
        psql -c "CREATE DATABASE fleetflow_db OWNER fleetflow_user;" -U postgres
        Write-Host "Postgres DB and user created (or already exist)."
    } catch {
        Write-Warning "Automatic DB/user creation failed — you may need to run psql commands manually as a superuser."
    }
} else {
    Write-Warning "psql not found on PATH. Please create the database and user manually:"
    Write-Host "  CREATE USER fleetflow_user WITH PASSWORD '12345';"
    Write-Host "  CREATE DATABASE fleetflow_db OWNER fleetflow_user;"
}

Write-Host "4) Installing psycopg2-binary into virtualenv (if not present)"
try {
    .venv\Scripts\python.exe -m pip install psycopg2-binary==2.9.9 -q
} catch {
    Write-Warning "Installing psycopg2-binary failed; try installing manually or use a wheel appropriate for your Python version."
}

Write-Host "5) Running migrations against Postgres"
.venv\Scripts\python.exe manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Error "migrate failed. Aborting."
    Pop-Location
    exit 1
}

Write-Host "6) Loading fixture into Postgres"
.venv\Scripts\python.exe manage.py loaddata fixtures/all_data.json
if ($LASTEXITCODE -ne 0) {
    Write-Error "loaddata failed. Aborting."
    Pop-Location
    exit 1
}

Write-Host "7) Archiving old data files into removed_data/"
New-Item -ItemType Directory -Force -Path removed_data | Out-Null
if (Test-Path db.sqlite3) { Move-Item db.sqlite3 removed_data\ };
Get-ChildItem -Path . -Include "test_results*.txt","full_traceback*.txt","full_error*.txt" -File -ErrorAction SilentlyContinue | ForEach-Object { Move-Item $_.FullName removed_data\ }

Write-Host "Migration complete. Verify Postgres DB contains the data and remove removed_data/ if you want to delete the backups."
Pop-Location