# UNOTEST — Flask App Service Demo

This is a Python Flask web app containing the existing localStorage task manager and a new test-record form/table backed by a Flask API.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 and test the table. GET /api/health returns `{"framework":"flask","status":"ok"}`.

## Deploy from GitHub to Azure App Service

1. Upload the **contents** of this folder to the root of GitHub repo `NiftyTechs/UNOTEST` on branch `main`, replacing the original frontend files.
2. Create an Azure **Web App**, choose **Code**, **Python**, **Linux**, and a compatible plan.
3. Under your App Service **Deployment Center**, choose **GitHub**, authorize access, select `NiftyTechs/UNOTEST` and branch `main`, and save to create the GitHub Actions workflow.
4. If startup detection does not work, set **Startup Command** to `gunicorn --bind=0.0.0.0:8000 app:app`.
5. Open the App Service default domain. Test `/api/health` and the form.

**Important:** The records API uses temporary in-process memory. Records reset after restarts/deployments and might differ between workers/instances. Never enter sensitive/personal information in this public demo. For real shared storage, add a managed database (for example Azure SQL or PostgreSQL), authentication and appropriate access controls.
