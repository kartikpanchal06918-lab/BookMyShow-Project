# BookMyShow: Netlify public URL with Django backend

Netlify hosts the public URL and proxies all requests to the Django service on Render. This preserves Django routing, sessions, forms and chatbot endpoints while the browser stays on the Netlify domain.

## 1. Push to GitHub
From the folder containing `manage.py`, create a GitHub repository and run:
```powershell
git init
git add .
git commit -m "Prepare BookMyShow deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```
Do not commit `venv` or `.env`.

## 2. Deploy the Django backend
1. Sign in to Render and connect GitHub.
2. Select **New + -> Blueprint**.
3. Choose this repository and apply the `render.yaml` blueprint.
4. Wait for `bookmyshow-django` to deploy. Copy its URL, e.g. `https://bookmyshow-django.onrender.com`.
5. In Render Environment, set `CSRF_TRUSTED_ORIGINS` to include your exact Netlify origin, e.g. `https://your-site.netlify.app`, plus `https://*.netlify.app` and `https://*.onrender.com`.

## 3. Publish through Netlify
1. Edit `NETLIFY_DEPLOY/_redirects`. Replace `BACKEND-HOSTNAME` with the actual Render hostname. Example:
```text
/* https://bookmyshow-django.onrender.com/:splat 200
```
2. Save. In Netlify choose **Add new site / Deploy manually** and upload the `NETLIFY_DEPLOY` folder. For an existing site, drag this folder into its Deploys page.
3. Open the `.netlify.app` URL. The Netlify proxy should keep the address on Netlify while Django responds.

## 4. Finish setup and test
Create an admin account from Render Shell: `python manage.py createsuperuser`. The PostgreSQL database starts empty; add genres, languages, theatres, movies and show schedules through `/admin/`. Local SQLite records are not automatically copied. Test registration, login, movie pages, booking, reviews, chatbot and voice in Chrome/Edge.

## Hosting notes
Render free web services may sleep when idle. Check the current database free-plan expiry/retention shown in Render before evaluation. Media uploads need persistent storage for long-term retention; the included local media directory is in the repository, but new uploads to an ephemeral service filesystem may not survive restarts/redeploys.
