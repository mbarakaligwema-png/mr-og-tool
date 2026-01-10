# MR OG TOOL - Server Deployment Guide

This guide explains how to deploy the **MR OG TOOL Server** specifically to **Render.com** (recommended for free/easy start).

## Prerequisites
- A GitHub account (to host your code repository).
- A Render.com account (can sign up with GitHub).

## Step 1: Push Code to GitHub
1. Create a new repository on GitHub (e.g., `mr-og-server`).
2. Upload ONLY the `server` folder contents (or the whole project, but we will configure Render to look at the `server` folder).
   - *Ideally, structure your repo so `requirements.txt` is at the root if possible, OR configure Root Directory in Render.*

## Step 2: Create Web Service on Render
1. Log in to dashboard.render.com.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Fill in the details:
   - **Name**: `mr-og-tool` (or any name you like).
   - **Region**: Frankfurt or Singapore (closest to Tanzania usually best, or just leave default).
   - **Branch**: `main`.
   - **Root Directory**: `server` (Important! Because our app is in the server folder).
   - **Runtime**: `Python 3`.
   - **Build Command**: `pip install -r requirements.txt` (Render should auto-detect this if requirements.txt is in the Root Directory).
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` (Or just reference the `Procfile`).

5. **Database Setup (Important for Persistence)**
   - Render's free Web Services spin down after inactivity. SQLite data (`users.db`) will be LOST.
   - For real usage, create a **PostgreSQL** database on Render:
     1. Go to Dashboard -> **New +** -> **PostgreSQL**.
     2. Create a database (e.g., `og-tool-db`).
     3. Copy the **Internal Database URL** (if creating Web Service in same account) or **External Database URL**.
     4. Go back to your Web Service -> **Environment**.
     5. Add Environment Variable:
        - Key: `DATABASE_URL`
        - Value: (Paste the Postgres URL you copied).

6. Click **Create Web Service**.

## Step 3: Get Your Server URL
- Once deployed, Render will give you a URL like: `https://mr-og-tool.onrender.com`.
- Copy this URL.

## Step 4: Configure the Tool (Client)
- On your computer (and your customers' computers), open the `config.json` file in the MR OG TOOL folder.
- Update `server_url` with your new online link:
  ```json
  {
      "server_url": "https://mr-og-tool.onrender.com"
  }
  ```
- Now, when you open the tool, it will connect to this online server instead of looking for one on your computer!

## Step 5: Create Admin User (Online)
- The first time the server starts, it creates specific default users if defined in code, OR you might need to register.
- Visit `https://mr-og-tool.onrender.com/register` to create your first account (or use `/admin` if default admin exists).
