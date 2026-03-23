function setupUI(editors) {
    const { editor, loginEditor } = editors;

    // SPA Navigation Logic
    const navBtns = document.querySelectorAll('.spa-nav .nav-btn');
    const views = document.querySelectorAll('.spa-view');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.disabled) return;
            const targetId = btn.getAttribute('data-target');
            switchView(targetId);
        });
    });

    window.switchView = function(viewId) {
        views.forEach(v => v.classList.remove('active'));
        navBtns.forEach(b => b.classList.remove('active'));
        
        const targetView = document.getElementById(viewId);
        if(targetView) targetView.classList.add('active');
        
        const activeBtn = document.querySelector(`.nav-btn[data-target="${viewId}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        if (viewId === 'view-dashboard') {
            setTimeout(() => {
                editor.layout();
                if(window.editor2) window.editor2.layout();
            }, 50);
        } else if (viewId === 'view-visualize') {
            renderArchitectureDiagram();
        } else if (viewId === 'view-history') {
            loadHistory();
        }
    };

    // Tab Logic for Analysis Results
    const tabBtns = document.querySelectorAll('.js-tabs .tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            const targetTab = document.getElementById(tabId);
            if(targetTab) targetTab.classList.add('active');
        });
    });

    // History Page Logic
    async function loadHistory() {
        const listDiv = document.getElementById('history-list');
        listDiv.innerHTML = '<div style="color:var(--text-muted)">Loading history...</div>';
        try {
            const data = await fetchHistory();
            if (data.error) {
                listDiv.innerHTML = `<div class="alert danger">Error: ${data.error}</div>`;
                return;
            }
            if (!data.history || data.history.length === 0) {
                listDiv.innerHTML = '<div style="color:var(--text-muted)">No saved analysis history found.</div>';
                return;
            }
            window.appHistoryData = data.history; 
            renderHistoryList(data.history);
        } catch (e) {
            listDiv.innerHTML = `<div class="alert warning">Connection Error: Cannot reach API.</div>`;
        }
    }

    function renderHistoryList(historyData) {
        const listDiv = document.getElementById('history-list');
        listDiv.innerHTML = '';
        if(historyData.length === 0) {
            listDiv.innerHTML = '<div style="color:var(--text-muted)">No matching snippets.</div>';
            return;
        }

        historyData.forEach((record, index) => {
            const card = document.createElement('div');
            card.style.cssText = 'background: var(--bg-card); padding: 20px; border-radius: 8px; border: 1px solid var(--border); display: flex; flex-direction: column; gap: 10px;';
            
            const fname = record.fileName || 'Untitled Snippet';
            let dateStr = 'Unknown Date';
            if (record.createdAt) {
                const d = new Date(record.createdAt);
                dateStr = d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            }

            const header = document.createElement('div');
            header.style.cssText = 'display: flex; justify-content: space-between; font-size: 14px; color: var(--text-muted); padding-bottom: 8px; border-bottom: 1px solid var(--border);';
            const cycloColor = record.cyclomaticComplexity > 5 ? 'var(--danger)' : 'var(--success)';
            header.innerHTML = `<span><strong style="color:var(--text-main); font-size: 1.05rem;">📄 ${fname}</strong> <span style="font-size:0.85rem; margin-left:12px;">🕒 ${dateStr}</span></span><span>⚡ Time: <span class="badge" style="background:var(--bg-main)">${record.timeComplexity}</span> | Cyclomatic: <span class="badge" style="background:var(--bg-main); color:${cycloColor}">${record.cyclomaticComplexity}</span></span>`;
            
            const previewCode = document.createElement('pre');
            previewCode.style.cssText = 'margin:0; padding:15px; background:#0f172a; color:#cbd5e1; font-family:monospace; border-radius:6px; max-height:100px; overflow:hidden; text-overflow:ellipsis; font-size:13px; margin-top: 5px;';
            previewCode.textContent = record.code.substring(0, 200) + (record.code.length > 200 ? '...' : '');
            
            const restoreBtn = document.createElement('button');
            restoreBtn.className = 'secondary-btn';
            restoreBtn.style.alignSelf = 'flex-start';
            restoreBtn.innerText = '🔁 Restore to Dashboard';
            restoreBtn.onclick = () => {
                const model = editor.getModel();
                model.pushEditOperations([], [{ range: model.getFullModelRange(), text: record.code }], () => null);
                window.switchView('view-dashboard');
                setTimeout(() => editor.focus(), 100);
            };
            
            card.appendChild(header);
            card.appendChild(previewCode);
            card.appendChild(restoreBtn);
            listDiv.appendChild(card);
        });
    }

    // History Filter & Search
    document.getElementById('history-search').addEventListener('input', () => filterHistory());
    document.getElementById('history-filter').addEventListener('change', () => filterHistory());

    function filterHistory() {
        if(!window.appHistoryData) return;
        const q = document.getElementById('history-search').value.toLowerCase();
        const f = document.getElementById('history-filter').value;

        const filtered = window.appHistoryData.filter(item => {
            const matchesSearch = item.code.toLowerCase().includes(q);
            const matchesFilter = (f === 'all') || (item.timeComplexity.includes(f));
            return matchesSearch && matchesFilter;
        });
        renderHistoryList(filtered);
    }

    // Generate AI Insights
    document.getElementById('btn-generate-insights').addEventListener('click', async () => {
        const code = editor.getValue();
        const timeVal = document.getElementById('time-complexity').innerText;
        const tc = (timeVal === '-' || timeVal === '') ? 'O(n)' : timeVal; 

        const stepsDiv = document.getElementById('learning-steps');
        const deepDiveDiv = document.getElementById('learning-deepdive');
        const explanationDiv = document.getElementById('ai-explanation');

        stepsDiv.innerHTML = '<div style="color:var(--text-muted); padding:20px; text-align:center;">⌛ Simulating execution trace...</div>';
        deepDiveDiv.innerHTML = '<div style="color:var(--text-muted)">Generating complexity meta-analysis...</div>';
        explanationDiv.innerHTML = '<div style="color:var(--text-muted)">Generating explanation...</div>';

        document.getElementById('btn-generate-insights').disabled = true;

        try {
            learnCode(code, tc).then(data => {
                if (data.error) {
                    stepsDiv.innerHTML = `<div class="alert danger">${data.error}</div>`;
                } else {
                    stepsDiv.innerHTML = '';
                    if (data.steps && data.steps.length) {
                        data.steps.forEach((step, idx) => {
                            const stepEl = document.createElement('div');
                            stepEl.style.cssText = 'background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 12px; margin-bottom: 8px;';
                            stepEl.innerHTML = `
                                <div style="font-family: monospace; color: var(--primary); font-size: 0.85rem; margin-bottom: 5px;">Line ${idx + 1}: ${step.line}</div>
                                <div style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.4;">${step.explanation}</div>
                            `;
                            stepsDiv.appendChild(stepEl);
                        });
                    }
                    deepDiveDiv.innerHTML = data.deepDive || "No deep dive available.";
                }
            });

            explainCode(code, tc).then(insights => {
                if (insights.error) {
                    explanationDiv.innerHTML = `<div class="alert warning">${insights.error}</div>`;
                } else {
                    explanationDiv.innerText = insights.explanation || "No explanation provided.";
                    const optContainer = document.getElementById('optimization-container');
                    if(optContainer && insights.refactors && insights.refactors.length > 0) {
                         optContainer.innerHTML = insights.refactors.map(r => `<div class="alert warning" style="margin-bottom:10px">🔧 ${r}</div>`).join('');
                    }
                }
            });

        } catch (e) {
            stepsDiv.innerHTML = '<div class="alert danger">Failed to connect to Learning API.</div>';
        } finally {
            document.getElementById('btn-generate-insights').disabled = false;
        }
    });

    // Login Overlay logic
    checkLoginStatus();

    document.getElementById('btn-unlock').addEventListener('click', async () => {
        const code = loginEditor.getValue();
        const btn = document.getElementById('btn-unlock');
        const errorDiv = document.getElementById('login-error');
        
        btn.disabled = true;
        btn.innerText = 'VERIFYING...';
        errorDiv.style.display = 'none';

        try {
            const data = await loginCode(code);
            if (data.success) {
                sessionStorage.setItem('isLoggedIn', 'true');
                document.getElementById('login-overlay').classList.add('hidden');
                btn.innerText = 'UNLOCK DASHBOARD';
                btn.disabled = false;
                window.dispatchEvent(new Event('triggerExplicitSave'));
            } else {
                errorDiv.innerText = data.error || 'Identity verification failed.';
                errorDiv.style.display = 'block';
                btn.innerText = 'UNLOCK DASHBOARD';
                btn.disabled = false;
            }
        } catch (err) {
            errorDiv.innerText = 'Error connecting to security protocol.';
            errorDiv.style.display = 'block';
            btn.innerText = 'UNLOCK DASHBOARD';
            btn.disabled = false;
        }
    });
}

function checkLoginStatus() {
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    const loginOverlay = document.getElementById('login-overlay');
    if (isLoggedIn === 'true') {
        loginOverlay.classList.add('hidden');
    } else {
        loginOverlay.classList.add('hidden'); // Guest mode
    }
}

async function renderArchitectureDiagram() {
    const element = document.getElementById('mermaid-diagram');
    if(element.getAttribute('data-rendered')) return; // compile only once to save CPU
    
    const mermaidCode = `flowchart TD
    classDef userLayer fill:#f9f9f9,stroke:#333,stroke-width:2px,color:#333
    classDef frontend fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#bae6fd
    classDef backend fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#bbf7d0
    classDef engine fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fed7aa
    classDef database fill:#4a044e,stroke:#a855f7,stroke-width:2px,color:#f3e8ff
    classDef output fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fecaca

    User(("🧑‍💻 User")):::userLayer
    subgraph Frontend["🖥️ FRONTEND LAYER (HTML, CSS, JS)"]
        Browser["Web Browser UI<br />(Monaco, UI routers)"]:::frontend
    end
    subgraph Backend["⚙️ BACKEND LAYER (Django)"]
        API["API Protocol handler"]:::backend
        Processor["Django Request logic"]:::backend
    end
    subgraph Engine["🧠 ANALYSIS ENGINE (Python AST)"]
        Parser["AST Source Parser"]:::engine
        Analyzer["Loop & Condition Detector"]:::engine
        Calculations["Complexity Estimations\\n(O(n), Cyclomatic)"]:::engine
        Comparator["Code Comparator"]:::engine
    end
    subgraph Database["🗄️ DATABASE LAYER (MongoDB)"]
        Mongo[("MongoDB Database\\n- User Inputs\\n- Analysis History\\n- Patterns")]:::database
    end
    subgraph Output["📊 OUTPUT LAYER"]
        Display["Visual Components\\n- Time Complexity\\n- Cyclomatic Complexity\\n- Alerts & Fixes"]:::output
    end

    User -->|Interacts| Browser
    Browser -->|HTTP POST Request| API
    API -->|Validates Data| Processor
    Processor -->|Invokes Python| Parser
    Parser --> Analyzer
    Parser --> Calculations
    Parser --> Comparator
    Analyzer -->|"Stores AST"| Mongo
    Calculations -->|"Logs Metrics"| Mongo
    Comparator -->|"Saves Data"| Mongo
    Mongo -->|"Fetches History"| Processor
    Processor -->|Constructs JSON Response| API
    API -->|Sends JSON Payload| Browser
    Browser -->|Updates Virtual DOM / SPA View| Display
    Display -->|Shows Results natively| User`;

    if (window.mermaid) {
        try {
            const { svg } = await window.mermaid.render('mermaid-architecture-svg', mermaidCode);
            element.innerHTML = svg;
            element.setAttribute('data-rendered', 'true');
        } catch (e) {
            console.error('Mermaid rendering failed', e);
        }
    }
}
