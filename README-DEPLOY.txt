AGRI VISION — 5 MIN DEPLOY

1) Create a GitHub repository and upload EVERYTHING inside this folder.

2) RENDER BACKEND
- Go to Render -> New + -> Web Service.
- Connect the GitHub repository.
- Root Directory: backend
- Runtime: Python 3
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn server:app
- Create Web Service.
- Wait for the service to become Live.
- Copy its URL, e.g. https://agrivision-api.onrender.com

3) CONNECT FRONTEND
- Open frontend/config.js
- Replace YOUR-RENDER-SERVICE.onrender.com with your real Render URL.
- Commit/push the change to GitHub.

4) VERCEL FRONTEND
- Go to Vercel -> Add New -> Project.
- Import the same GitHub repository.
- Root Directory: frontend
- Framework Preset: Other
- Build Command: leave empty
- Output Directory: .
- Deploy.

5) TEST
Open the Vercel URL and upload a leaf image. Prediction requests go to Render.

IMPORTANT: Render free services can sleep after inactivity, so the first prediction after a while may take longer.
