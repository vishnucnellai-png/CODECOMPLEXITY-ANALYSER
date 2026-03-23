let isCompareMode = false;

document.addEventListener('DOMContentLoaded', async () => {
    const editors = await initEditors();
    const { editor, editor2 } = editors;

    setupUI(editors);

    const statusEl = document.getElementById('global-status');
    const cycloVal = document.getElementById('cyclo-complexity');
    const timeVal = document.getElementById('time-complexity');
    const nestingVal = document.getElementById('nesting-depth');
    const locVal = document.getElementById('loc');
    const alertsContainer = document.getElementById('alerts-container');
    
    const btnRunAnalysis = document.getElementById('btn-run-analysis');
    const btnRunAnalysisNav = document.getElementById('btn-run-analysis-nav');
    const btnCompare = document.getElementById('btn-compare-mode');
    const editor2Container = document.getElementById('editor-container-2');

    btnCompare.addEventListener('click', () => {
        isCompareMode = !isCompareMode;
        if(isCompareMode) {
            btnCompare.innerText = 'Compare Mode: ON';
            btnCompare.classList.add('primary-btn');
            btnCompare.classList.remove('secondary-btn');
            editor2Container.style.display = 'block';
            editor.layout();
            editor2.layout();
        } else {
            btnCompare.innerText = 'Compare Mode: OFF';
            btnCompare.classList.add('secondary-btn');
            btnCompare.classList.remove('primary-btn');
            editor2Container.style.display = 'none';
        }
    });

    btnRunAnalysis.addEventListener('click', () => {
        if(isCompareMode) runComparison();
        else runAnalysis();
    });

    if (btnRunAnalysisNav) {
        btnRunAnalysisNav.addEventListener('click', () => {
            if(isCompareMode) runComparison();
            else runAnalysis();
        });
    }

    let typingTimer;
    const LIVE_DELAY = 800; // 800ms debounce
    
    const handleContentChange = () => {
        statusEl.innerHTML = 'Typing...';
        statusEl.className = 'status analyzing';
        
        clearTimeout(typingTimer);
        typingTimer = setTimeout(liveAnalyze, LIVE_DELAY);
    };

    editor.onDidChangeModelContent(handleContentChange);
    editor2.onDidChangeModelContent(handleContentChange);
    
    async function liveAnalyze() {
        try {
            const code = editor.getValue();
            const result = await analyzeCode(code, false);
            
            const liveTime = document.getElementById('live-time-complexity');
            const liveCyclo = document.getElementById('live-cyclo-complexity');
            const liveAlerts = document.getElementById('live-alerts-container');
            const sgText = document.getElementById('live-suggestion-text');
            
            if (liveTime) liveTime.innerText = result.timeComplexity;
            if (liveCyclo) liveCyclo.innerText = result.cyclomaticComplexity;
            
            if (liveAlerts) {
                liveAlerts.innerHTML = '';
                let hasAlerts = false;
                
                if (!result.alerts || result.alerts.length === 0) {
                    liveAlerts.innerHTML = `<div class="live-alert success"><strong>Clean Code</strong><br/><span style="font-size: 0.8rem; opacity: 0.8;">No major issues detected.</span></div>`;
                    statusEl.innerHTML = '🟢 Code Valid';
                    statusEl.className = 'status valid';
                    if(window.applyMonacoMarkers) window.applyMonacoMarkers(editor, []);
                    if(sgText) sgText.innerText = "Code looks optimal. Keep up the good work!";
                } else {
                    hasAlerts = true;
                    let maxSeverity = 'warning';
                    result.alerts.forEach(alert => {
                        if (alert.type === 'danger') maxSeverity = 'error';
                        let alertClass = alert.type === 'danger' ? 'danger' : 'warning';
                        liveAlerts.innerHTML += `<div class="live-alert ${alertClass}" style="margin-bottom:8px"><strong>${alert.title}</strong><br/><span style="font-size: 0.8rem; opacity: 0.8;">${alert.text}</span></div>`;
                    });
                    
                    if (maxSeverity === 'error') {
                        statusEl.innerHTML = '🔴 Error Found';
                        statusEl.className = 'status error';
                    } else {
                        statusEl.innerHTML = '🟡 Warning Detected';
                        statusEl.className = 'status warning';
                    }
                    if(window.applyMonacoMarkers) window.applyMonacoMarkers(editor, result.alerts);
                    if(sgText) sgText.innerText = "Issues detected. Click 'Analyze Code ⚡' to generate an AI fix.";
                }
            }
        } catch (e) {
            console.error("Live analysis silently failed", e);
        }
    }
    
    document.getElementById('save-analysis').addEventListener('click', async () => {
        const isLoggedIn = sessionStorage.getItem('isLoggedIn');
        if (isLoggedIn !== 'true') {
            document.getElementById('login-overlay').classList.remove('hidden');
        } else {
            await performSave();
        }
    });

    window.addEventListener('triggerExplicitSave', async () => {
        await performSave();
    });

    async function performSave() {
        const fileName = prompt("Enter a name for this code snippet:", "My Code Snippet");
        if (fileName === null || fileName.trim() === "") return;

        const code = editor.getValue();
        const btn = document.getElementById('save-analysis');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;
        try {
            const data = await analyzeCode(code, true, fileName.trim());
            if (data && !data.error) {
                btn.innerText = 'Saved!';
                setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 2000);
            } else {
                btn.innerText = 'Error Saving';
                setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 2000);
            }
        } catch (e) {
            btn.innerText = 'Error Saving';
            setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 2000);
        }
    }

    async function runAnalysis() {
        const btn = document.getElementById('btn-run-analysis');
        const spinner = btn ? btn.querySelector('.btn-spinner') : null;
        const btnText = btn ? btn.querySelector('.btn-text') : null;
        
        if(btnText) btnText.innerText = 'Analyzing...';
        if(spinner) spinner.style.display = 'block';
        if(btn) btn.disabled = true;
        
        statusEl.innerHTML = 'Analyzing...';
        statusEl.className = 'status analyzing';
        document.querySelectorAll('.metric-card').forEach(c => c.classList.add('loading'));
        
        try {
            const code = editor.getValue();
            const result = await analyzeCode(code, false);
            
            locVal.innerText = result.loc;
            timeVal.innerText = result.timeComplexity;
            cycloVal.innerText = result.cyclomaticComplexity;
            nestingVal.innerText = result.maxNestingDepth;
            
            const qg = document.getElementById('quality-gate-badge');
            if (result.cyclomaticComplexity !== '-' && result.cyclomaticComplexity > 5) {
                cycloVal.style.color = 'var(--danger)';
                if (qg) {
                    qg.innerText = 'QUALITY GATE FAILED';
                    qg.className = 'badge danger';
                }
            } else {
                cycloVal.style.color = '';
                if (qg) {
                    qg.innerText = 'QUALITY GATE PASSED';
                    qg.className = 'badge success';
                }
            }
            
            alertsContainer.innerHTML = '';
            let hasAlerts = false;
            if (!result.alerts || result.alerts.length === 0) {
                alertsContainer.innerHTML = `<div class="alert info"><strong>Clean Code:</strong> No major performance or complexity issues detected.</div>`;
            } else {
                hasAlerts = true;
                result.alerts.forEach(alert => {
                    let alertClass = alert.type === 'danger' ? 'warning' : alert.type; 
                    alertsContainer.innerHTML += `<div class="alert ${alertClass}" style="margin-bottom:1rem"><strong>${alert.title}:</strong> ${alert.text}</div>`;
                });
            }
            
            if (hasAlerts && !result.alerts.some(a => a.title === 'Clean Code')) {
                const fixBtn = document.createElement('button');
                fixBtn.className = 'secondary-btn';
                fixBtn.style.width = '100%';
                fixBtn.innerText = '✨ Fix Issue / Generate Suggested Code';
                fixBtn.onclick = async () => {
                    fixBtn.innerText = '🤖 Analyzing & Fixing... (Please wait)';
                    fixBtn.disabled = true;
                    const issueDesc = result.alerts.map(a => `${a.title}: ${a.text}`).join('. ');
                    try {
                        const fixData = await fixCode(code, issueDesc);
                        if (fixData.error) {
                            alert('Fix Error: ' + fixData.error);
                        } else {
                            const model = editor.getModel();
                            const currentCode = model.getValue();
                            const separator = '\n\n# ─────────────────────────────────────────\n# ✨ AI-Fixed Version\n# ─────────────────────────────────────────\n\n';
                            model.pushEditOperations([], [{ range: model.getFullModelRange(), text: currentCode + separator + fixData.fixedCode }], () => null);
                            window.switchView('view-dashboard');
                            editor.revealLine(model.getLineCount());
                            editor.focus();
                        }
                    } catch (e) {
                        alert('Connection failed.');
                    } finally {
                        fixBtn.innerText = '✨ Fix Issue / Generate Suggested Code';
                        fixBtn.disabled = false;
                    }
                };
                alertsContainer.appendChild(fixBtn);
            }

            document.getElementById('nav-analyze').disabled = false;
            window.switchView('view-analyze');
            
            statusEl.innerHTML = '🟢 Analysis Complete';
            statusEl.className = 'status valid';

        } catch (error) {
            alertsContainer.innerHTML = `<div class="alert warning"><strong>Connection Error:</strong> Backend API unreachable.</div>`;
            window.switchView('view-analyze'); // Force view regardless so they see the error
        } finally {
            if(btnText) btnText.innerText = '⚡ Analyze Code';
            if(spinner) spinner.style.display = 'none';
            if(btn) btn.disabled = false;
            document.querySelectorAll('.metric-card').forEach(c => c.classList.remove('loading'));
        }
    }

    async function runComparison() {
        const btn = document.getElementById('btn-run-analysis');
        const spinner = btn ? btn.querySelector('.btn-spinner') : null;
        const btnText = btn ? btn.querySelector('.btn-text') : null;
        
        if(btnText) btnText.innerText = 'Comparing...';
        if(spinner) spinner.style.display = 'block';
        if(btn) btn.disabled = true;
        document.querySelectorAll('.metric-card').forEach(c => c.classList.add('loading'));

        try {
            const data = await compareCode(editor.getValue(), editor2.getValue());
            const r1 = data.code1;
            const r2 = data.code2;

            locVal.innerHTML = `<span style="color:var(--text-main)">${r1.loc}</span> &nbsp;<span style="font-size:0.6em;color:var(--text-muted)">vs</span>&nbsp; <span style="color:var(--primary)">${r2.loc}</span>`;
            timeVal.innerHTML = `<span style="color:var(--text-main)">${r1.timeComplexity}</span> &nbsp;<span style="font-size:0.6em;color:var(--text-muted)">vs</span>&nbsp; <span style="color:var(--primary)">${r2.timeComplexity}</span>`;
            cycloVal.innerHTML = `<span style="color:var(--text-main)">${r1.cyclomaticComplexity}</span> &nbsp;<span style="font-size:0.6em;color:var(--text-muted)">vs</span>&nbsp; <span style="color:var(--primary)">${r2.cyclomaticComplexity}</span>`;
            nestingVal.innerHTML = `<span style="color:var(--text-main)">${r1.maxNestingDepth}</span> &nbsp;<span style="font-size:0.6em;color:var(--text-muted)">vs</span>&nbsp; <span style="color:var(--primary)">${r2.maxNestingDepth}</span>`;
            
            cycloVal.style.color = '';
            
            alertsContainer.innerHTML = '<h3 style="margin-bottom:1rem;color:var(--text-main)">Code 1 Alerts (Left)</h3>';
            if (r1.alerts) {
                r1.alerts.forEach(a => {
                    let alertClass = a.type === 'danger' ? 'warning' : a.type;
                    alertsContainer.innerHTML += `<div class="alert ${alertClass}" style="margin-bottom:0.5rem"><strong>${a.title}:</strong> ${a.text}</div>`;
                });
            }
            
            alertsContainer.innerHTML += '<h3 style="margin-top:1.5rem;margin-bottom:1rem;color:var(--primary)">Code 2 Alerts (Right)</h3>';
            if (r2.alerts) {
                r2.alerts.forEach(a => {
                    let alertClass = a.type === 'danger' ? 'warning' : a.type;
                    alertsContainer.innerHTML += `<div class="alert ${alertClass}" style="margin-bottom:0.5rem"><strong>${a.title}:</strong> ${a.text}</div>`;
                });
            }
            
            document.getElementById('nav-analyze').disabled = false;
            window.switchView('view-analyze');

        } catch (error) {
            alertsContainer.innerHTML = `<div class="alert warning"><strong>Connection Error:</strong> Backend API unreachable.</div>`;
            window.switchView('view-analyze'); // Force view
        } finally {
            if(btnText) btnText.innerText = '⚡ Analyze Code';
            if(spinner) spinner.style.display = 'none';
            if(btn) btn.disabled = false;
            document.querySelectorAll('.metric-card').forEach(c => c.classList.remove('loading'));
        }
    }
});
