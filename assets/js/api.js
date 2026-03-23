// Global API functions for file:// compatibility
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '' 
    ? 'http://127.0.0.1:8000/api' 
    : 'https://YOUR_BACKEND_APP.onrender.com/api'; // Replace with your Render URL after deployment

async function analyzeCode(code, save = false, fileName = '') {
    const response = await fetch(`${API_BASE_URL}/analyze/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, save: save, fileName: fileName })
    });
    return await response.json();
}

async function compareCode(code1, code2) {
    const response = await fetch(`${API_BASE_URL}/compare/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code1: code1, code2: code2 })
    });
    return await response.json();
}

async function explainCode(code, timeComplexity) {
    const response = await fetch(`${API_BASE_URL}/explain/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, timeComplexity: timeComplexity })
    });
    return await response.json();
}

async function fixCode(code, issueDesc) {
    const response = await fetch(`${API_BASE_URL}/fix/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, issue: issueDesc })
    });
    return await response.json();
}

async function learnCode(code, timeComplexity) {
    const response = await fetch(`${API_BASE_URL}/learn/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, timeComplexity: timeComplexity })
    });
    return await response.json();
}

async function loginCode(code) {
    const response = await fetch(`${API_BASE_URL}/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })
    });
    return await response.json();
}

async function fetchHistory() {
    const response = await fetch(`${API_BASE_URL}/history/`);
    return await response.json();
}

