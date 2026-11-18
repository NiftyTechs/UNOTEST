# Azure + GitHub Task Manager

Simple HTML/CSS/JavaScript task manager. Tasks are stored in your browser's local storage, not on a server.

## Run locally

Open `index.html` in a modern browser, or run `python3 -m http.server 8000` in this folder and visit http://localhost:8000.

## Deploy to Azure Static Web Apps

1. Create a new repository on GitHub.
2. Upload `index.html`, `styles.css`, `script.js`, and `README.md` to the **root** of the repository, then commit to `main`.
3. In Azure Portal, create a **Static Web App** and select the **Free** hosting plan.
4. Choose **GitHub** as the deployment source, authorize access, and select your repository and `main` branch.
5. Under Build Details, use **Custom**: App location `/`, API location blank, Output location blank.
6. Select **Review + create** and **Create**. Azure creates a GitHub Actions workflow in `.github/workflows/`.
7. Open the repository's **Actions** tab to monitor deployment. In Azure's Static Web App resource, open the generated URL.

Any subsequent commit to `main` triggers a redeployment.

Note: Do not put secret keys in these files: they are downloaded to visitors' browsers.
