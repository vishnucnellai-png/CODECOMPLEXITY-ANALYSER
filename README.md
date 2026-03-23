# Code Complexity Analyzer

[![Frontend: HTML/CSS/JS](https://img.shields.io/badge/Frontend-HTML%2FCCSS%2FJS-blue?style=flat-square)](#)
[![Backend: Django](https://img.shields.io/badge/Backend-Django-092E20?style=flat-square&logo=django)](#)
[![Deployment: Vercel & Render](https://img.shields.io/badge/Deployment-Vercel%20%26%20Render-black?style=flat-square)](#)

A powerful, full-stack web application designed for comprehensive static code analysis. The application performs deep algorithmic parsing to calculate Time Complexity, Cyclomatic Complexity, Maximum Nesting Depth, and accurate Lines of Code. Delivered via a high-performance Single-Page Application (SPA) interface, it provides instant AI-powered optimizations, historical tracking, and dynamic architecture visualization modules.

## Key Features
- **Real-Time Code Analysis:** Immediate execution and calculation of complexity metrics directly from the integrated editor.
- **Deep Insights and Fixes:** Generates specific, actionable suggestions to optimize execution bottlenecks, lower cyclomatic complexity, and reduce deep nesting.
- **Side-by-Side Comparison:** Direct comparative analysis of algorithmic efficiency between differing coding approaches.
- **History and Security Login:** Implementation of a strict access protocol to securely catalog and save analyzed code snippets to the backend database.
- **Educational Deep Dives:** Provides a simulated step-by-step execution trace along with an automated masterclass explaining the code logic.
- **Architecture Visualization:** Dynamically generated architecture flowcharts built with Mermaid.js.

## Technology Stack
- **Frontend Layer:** HTML5, CSS3 (Custom Design System with scalable component architecture), Vanilla JavaScript (ES6 Modules)
- **Editor Integration:** Monaco Editor (Microsoft VS Code infrastructure)
- **Backend Architecture:** Python 3, Django 
- **Analysis Engine:** Python `ast` (Abstract Syntax Tree) module for algorithmic parsing and control flow calculation.
- **Database Architecture:** SQLite / MongoDB ready
- **Hosting / CI:** Pre-configured for Vercel (Frontend) and Render (Backend WSGI).

## Local Installation Guide

For Windows users, execute the provided `start_app.bat` script to automatically initialize the backend server and launch the application.

**Manual Initialization:**

### 1. Initialize the Backend
```bash
cd backend
python -m venv .venv
source .venv/scripts/activate  # On Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py runserver 127.0.0.1:8000
```

### 2. Initialize the Frontend
As a decoupled frontend architecture, no compilation is strictly required. Open `index.html` locally via a modern browser or serve it utilizing a local development server (e.g., VS Code Live Server).

## Production Deployment
The application is structured for independent micro-deployments:
- The **Frontend** is configured for automated serverless deployment on [Vercel](https://vercel.com/).
- The **Backend** utilizes `gunicorn` with open CORS headers for immediate Platform-as-a-Service deployment on [Render](https://render.com/).

*Configuration Note: To link the layers in a production environment, update the `API_BASE_URL` constant within `assets/js/api.js` to target your deployed backend instance.*
