// Global Editor Initialization — uses locally bundled Monaco
function initEditors() {
    return new Promise((resolve) => {
        // Monaco is loaded via loader.js in index.html; just use require()
        require(['vs/editor/editor.main'], function() {
            window.editor = monaco.editor.create(document.getElementById('editor-container'), {
                value: `# Code Complexity Analyser\n# Real-time analysis using Python AST & AI\n\n# Let's inspect some code quality!\n\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    \n    # Performance Warning: Exponential logic\n    # O(2^n) time complexity detected\n    return fibonacci(n - 1) + fibonacci(n - 2)\n\ndef process_array(items):\n    result = []\n    \n    # Performance Warning: Nested Loop detected via AST Analyzer\n    for i in range(len(items)):\n        for j in range(len(items)):\n            if items[i] == items[j]:\n                result.append(items[i])\n                \n    return result`,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 15,
                fontFamily: "'Fira Code', 'Monaco', monospace",
                padding: { top: 20 },
                scrollBeyondLastLine: false,
                lineHeight: 24,
                folding: true
            });

            window.editor2 = monaco.editor.create(document.getElementById('editor-container-2'), {
                value: `# Code 2 (Optimization attempt)\ndef process_optimized(items):\n    seen = set()\n    result = []\n    \n    for item in items:\n        if item in seen:\n            result.append(item)\n        seen.add(item)\n        \n    return result`,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 15,
                fontFamily: "'Fira Code', 'Monaco', monospace",
                padding: { top: 20 },
                scrollBeyondLastLine: false,
                lineHeight: 24,
                folding: true
            });

            window.loginEditor = monaco.editor.create(document.getElementById('login-editor-container'), {
                value: `def unlock(a, b):\n    # Write your logic here\n    return a + b`,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "'Fira Code', monospace",
                scrollBeyondLastLine: false,
                lineHeight: 20
            });

            resolve({
                editor: window.editor,
                editor2: window.editor2,
                loginEditor: window.loginEditor
            });
        });
    });
}

window.applyMonacoMarkers = function(editor, alerts) {
    if (!window.monaco) return;
    const model = editor.getModel();
    
    const markers = alerts.map(alert => {
        let lineNum = 1;
        // The Python engine usually says e.g., "at line 8"
        const match = alert.text.match(/line (\d+)/i);
        if (match && match[1]) {
            lineNum = parseInt(match[1], 10);
        }
        
        let severity = monaco.MarkerSeverity.Warning;
        if (alert.type === 'danger') severity = monaco.MarkerSeverity.Error;
        
        return {
            severity: severity,
            message: `${alert.title}: ${alert.text}`,
            startLineNumber: lineNum,
            startColumn: 1,
            endLineNumber: lineNum,
            endColumn: 100
        };
    });
    
    monaco.editor.setModelMarkers(model, 'analyzer', markers);
};
