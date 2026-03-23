# 📊 Code Complexity Analyzer

[![Frontend: HTML/CSS/JS](https://img.shields.io/badge/Frontend-HTML%2FCCSS%2FJS-blue?style=flat-square)](#)
[![Backend: Django](https://img.shields.io/badge/Backend-Django-092E20?style=flat-square&logo=django)](#)
[![Deployment: Vercel & Render](https://img.shields.io/badge/Deployment-Vercel%20%26%20Render-black?style=flat-square)](#)

A powerful, full-stack web application that performs deep static code analysis. It calculates algorithmic Time Complexity (e.g., `O(n)`), Cyclomatic Complexity, Max Nesting Depth, and accurate Lines of Code. Boasting a premium, highly dynamic Single-Page Application (SPA) interface, it provides instant AI-powered suggestions, history tracking, and an interactive architecture visualization module.

## ✨ Key Features
- **⚡ Real-Time Code Analysis:** Type in the editor and watch your complexity metrics update instantly as you write.
- **🔍 Deep Insights & Fixes:** Generates specific suggestions to optimize bottlenecks, lower cyclomatic complexity, and reduce deep nesting.
- **⚖️ Side-by-Side Comparison:** Compare the algorithmic efficiency of two entirely different approaches instantly.
- **💾 History & Security Login:** "Code Login" developer-only access protocol to securely save your analyzed code snippets to the database.
- **🧠 Educational Deep Dives:** See a simulated step-by-step execution trace and read a generated masterclass explaining your exact code logic.
- **🌳 Architecture Visualization:** Dynamically generated architecture flowcharts built with Mermaid.js.

## 🛠️ Technology Stack
- **Frontend Layer:** Vanilla HTML5, CSS3 (Custom Design System with Glassmorphism, shimmers, & smooth micro-animations), Vanilla JavaScript
- **Editor Integration:** Monaco Editor (The engine behind VS Code)
- **Backend Architecture:** Python 3, Django 
- **Analysis Engine:** Python `ast` (Abstract Syntax Tree) module for algorithmic parsing and cyclomatic calculation.
- **Database:** SQLite / MongoDB ready
- **Hosting / CI:** Prep-configured for **Vercel** (Frontend) and **Render** (Backend WSGI).

## 🚀 Getting Started Locally

If you are on Windows, simply double-click the `start_app.bat` script! It handles the entire startup sequence for you.

**Manual Startup:**

### 1. Start the Backend (API)
```bash
cd backend
python -m venv .venv
# Activate virtual environment
source .venv/scripts/activate  # On Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py runserver 127.0.0.1:8000
```

### 2. Start the Frontend
Since it's a completely decoupled frontend architecture, simply open `index.html` in your favorite modern browser safely via the file protocol, or use a tool like VS Code Live Server.

## 🌐 Production Deployment
The application is structured for independent micro-deployments:
- **Frontend** is configured for 1-click serverless deployment on [Vercel](https://vercel.com/).
- **Backend** is configured with `gunicorn` and open CORS/Hosts for immediate PaaS deployment on [Render](https://render.com/).

*To link them in production, update the `API_BASE_URL` constant at the very top of `assets/js/api.js` to point to your live Render instance.*

---
*Built with ❤️ to foster a cleaner, more efficient coding future.*
