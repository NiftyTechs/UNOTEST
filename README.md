# UNOTEST — Azure Python Flask Web Application

A full-stack Python Flask web application hosted on **Microsoft Azure App Service**, integrated with **Azure SQL Database**, **Microsoft Entra ID**, and **GitHub Actions** for automated deployment.

This project demonstrates how to build, deploy, secure, and manage a cloud-based web application using Microsoft Azure and GitHub.

## 1. Project Overview

UNOTEST is a demonstration application designed for learning and testing cloud development.

The application includes:

- **Task Manager:** Add, complete, and delete tasks using browser localStorage.
- **Test Records:** Add, view, update, and delete records using a Python Flask REST API.
- **Azure SQL Database:** Persistent storage for test records.
- **Microsoft Entra ID:** Microsoft account authentication through Azure App Service.
- **GitHub Actions:** Automatic deployment when changes are pushed to the `main` branch.
- **Managed Identity:** Passwordless authentication between Azure App Service and Azure SQL Database.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Cloud Platform | Microsoft Azure |
| Web Hosting | Azure App Service |
| Backend | Python 3.14 / Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | Azure SQL Database |
| Database Driver | mssql-python |
| Authentication | Microsoft Entra ID |
| Database Authentication | System-Assigned Managed Identity |
| Source Control | GitHub |
| CI/CD | GitHub Actions |
| Web Server | Gunicorn |

## 3. Application Architecture

```text
GitHub Repository
       |
       v
GitHub Actions
       |
       v
Azure App Service
       |
       +---- Python Flask Application
       |           |
       |           +---- REST API
       |           +---- HTML / CSS / JavaScript
       |
       +---- Microsoft Entra ID
       |           |
       |           +---- User Authentication
       |
       +---- Managed Identity
                   |
                   v
            Azure SQL Database
                   |
                   v
             dbo.TestRecords
```

## 4. Azure Resources

The demonstration uses the following Azure resources:

| Resource | Name |
|---|---|
| Web App | `unotest-python-app` |
| SQL Server | `sql-unotest-niftytechs` |
| SQL Database | `sqldb-unotest` |
| SQL Table | `dbo.TestRecords` |
| GitHub Repository | `NiftyTechs/UNOTEST` |
| Region | Central US |
| Operating System | Linux |

**Live Application:**

https://unotest-python-app-fubjchdkcudmdngj.centralus-01.azurewebsites.net

**GitHub Repository:**

https://github.com/NiftyTechs/UNOTEST

## 5. Project Structure

```text
UNOTEST/
│
├── app.py
├── requirements.txt
├── index.html
├── styles.css
├── script.js
├── README.md
│
└── .github/
    └── workflows/
        └── main_unotest-python-app.yml
```

### File Descriptions

- `app.py` — Flask application, API endpoints, and SQL database operations.
- `requirements.txt` — Required Python dependencies.
- `index.html` — Frontend interface for managing tasks and test records.
- `styles.css` — Application styling.
- `script.js` — Frontend functionality and REST API calls.
- `README.md` — Project documentation.
- `.github/workflows/` — GitHub Actions deployment configuration.

## 6. Run Locally

### Requirements

- Python with compatible application dependencies
- Git
- Visual Studio Code or another code editor
- Access to Azure SQL Database if testing SQL functionality

### Step 1 — Clone Repository

```bash
git clone https://github.com/NiftyTechs/UNOTEST.git
cd UNOTEST
```

### Step 2 — Create Python Virtual Environment

```bash
python3 -m venv .venv
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

The application uses these settings:

| Variable | Description |
|---|---|
| `SQL_SERVER` | Azure SQL server hostname |
| `SQL_DATABASE` | Azure SQL database name |

For Azure App Service:

```text
SQL_SERVER=sql-unotest-niftytechs.database.windows.net
SQL_DATABASE=sqldb-unotest
```

These variables are configured in:

**Azure Portal → App Services → unotest-python-app → Settings → Environment variables**

The production database connection uses `ActiveDirectoryMSI`, which is intended for an Azure managed identity. Local development requires a compatible authentication method and appropriate Azure SQL permissions.

Do not commit passwords, connection secrets, or access tokens to GitHub.

### Step 5 — Start Flask

```bash
python app.py
```

Open the local address displayed in your terminal.

The application can serve its frontend locally, but SQL endpoints require a valid database connection.

## 7. Azure SQL Database

The application stores test records in the following SQL table.

### Create Table

```sql
IF OBJECT_ID('dbo.TestRecords', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.TestRecords (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Email NVARCHAR(200) NOT NULL,
        Notes NVARCHAR(500) NULL,
        CreatedAt DATETIME2 NOT NULL
            DEFAULT SYSUTCDATETIME()
    );
END;
```

### Insert Test Records

```sql
INSERT INTO dbo.TestRecords
    (Name, Email, Notes)
VALUES
    ('John Smith', 'john@example.com',
     'First Azure SQL test'),
    ('Jane Doe', 'jane@example.com',
     'Testing Flask and SQL');
```

### Retrieve Records

```sql
SELECT *
FROM dbo.TestRecords
ORDER BY Id DESC;
```

Records stored in Azure SQL persist across application restarts and deployments.

## 8. Managed Identity and SQL Permissions

The App Service uses a **System-Assigned Managed Identity** to authenticate to Azure SQL.

Enable it under:

**Azure Portal → App Services → unotest-python-app → Identity → System assigned → On**

Then, using an authorized Microsoft Entra SQL administrator, run:

```sql
CREATE USER [unotest-python-app]
FROM EXTERNAL PROVIDER;

GRANT SELECT, INSERT, UPDATE, DELETE
ON OBJECT::dbo.TestRecords
TO [unotest-python-app];
```

To verify the database user:

```sql
SELECT name, type_desc
FROM sys.database_principals
WHERE name = 'unotest-python-app';
```

Expected result:

```text
unotest-python-app    EXTERNAL_USER
```

If the user already exists, do not run `CREATE USER` again.

The managed identity allows the application to access SQL without storing SQL credentials in the source code.

## 9. REST API Endpoints

The Flask backend exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check Flask application |
| GET | `/api/db-health` | Check SQL connection |
| GET | `/api/records` | Retrieve all records |
| GET | `/api/records/{id}` | Retrieve one record |
| POST | `/api/records` | Create a record |
| PUT | `/api/records/{id}` | Update a record |
| DELETE | `/api/records/{id}` | Delete a record |

### Flask Health Check

```text
GET /api/health
```

Expected:

```json
{
  "framework": "flask",
  "status": "ok"
}
```

### SQL Connection Health Check

```text
GET /api/db-health
```

Expected:

```json
{
  "database": "connected",
  "status": "ok"
}
```

### Create Record — Example Request

```json
{
  "name": "Test User",
  "email": "test@example.com",
  "notes": "Testing Python Flask API"
}
```

The record is inserted into `dbo.TestRecords`.

## 10. GitHub Actions — Continuous Deployment

UNOTEST is connected to Azure App Service using GitHub Actions.

### Deployment Process

1. Update application code.
2. Commit changes to GitHub.
3. Push changes to the `main` branch.
4. GitHub Actions builds the application.
5. GitHub Actions authenticates to Azure.
6. The application is deployed to Azure App Service.
7. Verify the deployed application.

### Configure GitHub Deployment

In Azure Portal:

1. Open **App Services**.
2. Select your Web App.
3. Open **Deployment Center**.
4. Select **GitHub**.
5. Select the repository and branch.
6. Configure deployment authentication.
7. Save.

For this project, GitHub Actions uses an Azure user-assigned managed identity with federated credentials.

The GitHub deployment identity is separate from the system-assigned identity used to connect Flask to Azure SQL.

### Startup Command

If automatic Flask detection fails, configure:

```bash
gunicorn --bind=0.0.0.0:8000 app:app
```

## 11. Microsoft Entra ID Authentication

UNOTEST supports Microsoft Entra ID authentication through Azure App Service.

Configuration location:

**Azure Portal → App Services → unotest-python-app → Authentication**

Recommended configuration:

| Setting | Value |
|---|---|
| Identity Provider | Microsoft |
| Tenant Configuration | Workforce |
| Supported Accounts | Single Tenant |
| Restrict Access | Require Authentication |
| Unauthenticated Requests | HTTP 302 Redirect |
| Redirect Provider | Microsoft |

### Restrict Access to Specific Users

To allow only selected Microsoft accounts:

1. Open the Microsoft identity provider configuration.
2. Find **Additional checks**.
3. Select **Allow requests from specific identities**.
4. Enter the authorized Microsoft Entra user Object IDs.
5. Save and test access.

Alternatively, Enterprise Application user assignments can be required and managed in Microsoft Entra.

**Note:** Single-tenant authentication alone does not restrict access to only Member accounts or only one specific user. Explicit authorization restrictions are necessary.

## 12. Troubleshooting

### GitHub Deployment Failed

Possible cause: GitHub Actions identity lacks Azure permissions.

Solution:

- Verify the federated identity configuration.
- Confirm the Azure subscription and tenant IDs.
- Assign an appropriate deployment role to the identity at the Web App scope.
- Retry GitHub Actions.

### Flask Application Not Detected

Possible cause: Missing application files or incomplete deployment.

Solution:

- Verify `app.py` exists in the repository root.
- Verify `requirements.txt`.
- Check deployment logs.
- Configure the Gunicorn startup command if necessary.

### SQL Database Unavailable

Check:

- `SQL_SERVER` environment variable.
- `SQL_DATABASE` environment variable.
- Managed identity configuration.
- Azure SQL firewall.
- SQL database user permissions.

### Azure SQL Firewall Error

Example:

```text
Client with IP address 'x.x.x.x'
is not allowed to access the server.
```

Solution:

1. Open **Azure SQL Server → Networking**.
2. Enable access from selected networks.
3. Add the Web App's required outbound IP addresses.
4. Save firewall settings.
5. Test the connection again.

Avoid enabling unrestricted access from all Azure services when narrower rules are sufficient.

### Records Are Not Loading

Open:

```text
/api/db-health
```

If the database is unavailable, check Azure App Service application logs and the SQL connection settings.

## 13. Cost Considerations

This demonstration was built using Azure resources selected for low-cost educational testing.

- Azure App Service: Free F1 plan, subject to limits.
- Azure SQL Database: Free offer, subject to eligibility and monthly allowances.
- GitHub Actions: Subject to GitHub usage limits.
- Microsoft Entra ID: Features and licensing depend on tenant configuration.

Azure SQL's free offer can provide 100,000 vCore seconds and 32 GB of data storage per month, subject to the offer terms.

To avoid additional SQL compute charges, select the option to pause database access when the monthly free limit is reached.

Always review the Azure pricing summary before creating resources. Other services and configurations may incur charges.

## 14. Security Considerations

This is an educational application.

Before using it with real information:

- Require authentication.
- Restrict access to authorized users.
- Validate API permissions server-side.
- Protect environment variables and credentials.
- Use managed identities wherever possible.
- Restrict Azure SQL firewall rules.
- Avoid storing sensitive data in public test environments.
- Review logging and monitoring settings.

Tasks stored in localStorage remain in the user's browser. SQL records are stored centrally in Azure SQL Database.

## 15. Classroom Learning Objectives

By completing this project, students will learn how to:

1. Create and manage a GitHub repository.
2. Deploy a Python Flask application to Azure App Service.
3. Configure automatic deployments using GitHub Actions.
4. Create SQL tables in Azure SQL Database.
5. Build REST API endpoints.
6. Perform CRUD operations with Python and SQL.
7. Configure Azure managed identities.
8. Troubleshoot network connectivity and firewall permissions.
9. Implement Microsoft Entra ID authentication.
10. Understand basic cloud security and resource costs.

## 16. Project Completion Checklist

- [ ] GitHub repository created
- [ ] Python Flask application deployed
- [ ] GitHub Actions configured
- [ ] Azure App Service running
- [ ] Azure SQL Database created
- [ ] SQL table created
- [ ] System-assigned managed identity enabled
- [ ] SQL permissions configured
- [ ] SQL firewall configured
- [ ] Flask connected to Azure SQL
- [ ] Records displayed from SQL Database
- [ ] New records can be added
- [ ] Existing records can be updated
- [ ] Records can be deleted
- [ ] Microsoft Entra authentication configured
- [ ] Application access restrictions tested

---

## Project Information

**Project:** UNOTEST  
**Organization:** NiftyTechs Group LLC  
**Platform:** Microsoft Azure  
**Repository:** https://github.com/NiftyTechs/UNOTEST  
**Purpose:** Educational demonstration of cloud application development, deployment, database integration, and authentication.

**Important:** Students recreating this project should use their own Azure subscriptions, unique resource names, GitHub repositories, and Microsoft Entra identities.
