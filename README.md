<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeAgent - Autonomous AI Coding Assistant Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a202c;
            overflow-x: hidden;
        }

        .header {
            background: rgba(26, 32, 44, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff88, transparent);
            animation: scan 3s linear infinite;
        }

        @keyframes scan {
            to { left: 100%; }
        }

        .logo-container {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .ascii-logo {
            font-family: 'Courier New', monospace;
            color: #00ff88;
            font-size: 0.8rem;
            line-height: 1;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
            white-space: pre;
            display: inline-block;
        }

        h1 {
            text-align: center;
            color: #fff;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            background: linear-gradient(90deg, #00ff88, #00a8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { filter: brightness(1); }
            to { filter: brightness(1.2); }
        }

        .tagline {
            text-align: center;
            color: #a0aec0;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }

        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transform: translateY(0);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }

        .feature-card:hover::before {
            transform: scaleX(1);
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            display: inline-block;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .demo-section {
            background: rgba(26, 32, 44, 0.95);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        .terminal {
            background: #0a0e27;
            border-radius: 10px;
            padding: 1.5rem;
            font-family: 'Cascadia Code', 'Fira Code', monospace;
            color: #00ff88;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
            position: relative;
            min-height: 400px;
            overflow: hidden;
        }

        .terminal-header {
            display: flex;
            gap: 8px;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #2d3748;
        }

        .terminal-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .dot-red { background: #ff5f57; }
        .dot-yellow { background: #ffbd2e; }
        .dot-green { background: #28ca42; }

        .terminal-content {
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .command {
            color: #00ff88;
            margin-bottom: 0.5rem;
            display: block;
        }

        .output {
            color: #e2e8f0;
            margin-bottom: 1rem;
            opacity: 0;
            animation: fadeIn 0.5s ease forwards;
        }

        @keyframes fadeIn {
            to { opacity: 1; }
        }

        .action {
            color: #ffd700;
            margin: 0.5rem 0;
        }

        .success {
            color: #48bb78;
            font-weight: bold;
        }

        .modified {
            color: #f687b3;
        }

        .diff {
            background: rgba(0, 255, 136, 0.1);
            border-left: 3px solid #00ff88;
            padding: 0.5rem;
            margin: 0.5rem 0;
            font-size: 0.85rem;
        }

        .diff-add {
            color: #48bb78;
        }

        .diff-remove {
            color: #fc8181;
        }

        .controls {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }

        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.2);
            transition: left 0.3s ease;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
        }

        .stat-card {
            text-align: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #00ff88;
            display: block;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #a0aec0;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .typing-cursor {
            display: inline-block;
            width: 10px;
            height: 20px;
            background: #00ff88;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }

        .progress-bar {
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 1rem;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00a8ff);
            width: 0%;
            transition: width 0.5s ease;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }

        .workflow-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
        }

        .workflow-steps {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .workflow-step {
            flex: 1;
            min-width: 150px;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
            position: relative;
            transition: all 0.3s ease;
        }

        .workflow-step:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .workflow-step.active {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
            70% { box-shadow: 0 0 0 20px rgba(0, 255, 136, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
        }

        .step-number {
            display: block;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .step-title {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }

        .step-description {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .container { padding: 0 1rem; }
            .feature-grid { grid-template-columns: 1fr; }
            .workflow-steps { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-container">
            <div class="ascii-logo">
 ██████╗ ███████╗███╗   ██╗████████╗
██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██║   ██║██╔══╝  ██║╚██╗██║   ██║   
╚██████╔╝███████╗██║ ╚████║   ██║   
 ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
            </div>
        </div>
        <h1>CodeAgent</h1>
        <p class="tagline">Autonomous AI Coding Assistant - Never Gives Up</p>
    </div>

    <div class="container">
        <div class="feature-grid">
            <div class="feature-card">
                <span class="feature-icon">🔍</span>
                <h3>Intelligent Exploration</h3>
                <p>Navigates your entire codebase autonomously, understanding file relationships and dependencies before making changes.</p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔄</span>
                <h3>Self-Correcting Loop</h3>
                <p>Implements, tests, identifies errors, fixes them, and retries until success - completely autonomously.</p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🛠️</span>
                <h3>Production Ready</h3>
                <p>Writes clean, tested code following your project's patterns and conventions. No babysitting required.</p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🎨</span>
                <h3>Beautiful Interface</h3>
                <p>Live syntax-highlighted diffs, progress tracking, and color-coded status indicators in your terminal.</p>
            </div>
        </div>

        <div class="workflow-container">
            <h2 style="text-align: center; margin-bottom: 1rem;">The Autonomous Workflow</h2>
            <div class="workflow-steps">
                <div class="workflow-step" id="step1">
                    <span class="step-number">1</span>
                    <div class="step-title">EXPLORE</div>
                    <div class="step-description">Scan codebase</div>
                </div>
                <div class="workflow-step" id="step2">
                    <span class="step-number">2</span>
                    <div class="step-title">ANALYZE</div>
                    <div class="step-description">Understand context</div>
                </div>
                <div class="workflow-step" id="step3">
                    <span class="step-number">3</span>
                    <div class="step-title">IMPLEMENT</div>
                    <div class="step-description">Write code</div>
                </div>
                <div class="workflow-step" id="step4">
                    <span class="step-number">4</span>
                    <div class="step-title">VERIFY</div>
                    <div class="step-description">Run tests</div>
                </div>
                <div class="workflow-step" id="step5">
                    <span class="step-number">5</span>
                    <div class="step-title">FIX</div>
                    <div class="step-description">Correct errors</div>
                </div>
                <div class="workflow-step" id="step6">
                    <span class="step-number">6</span>
                    <div class="step-title">SUCCESS</div>
                    <div class="step-description">Task complete</div>
                </div>
            </div>
        </div>

        <div class="demo-section">
            <h2 style="color: white; text-align: center; margin-bottom: 1.5rem;">Live Demo: Watch CodeAgent in Action</h2>
            
            <div class="terminal">
                <div class="terminal-header">
                    <span class="terminal-dot dot-red"></span>
                    <span class="terminal-dot dot-yellow"></span>
                    <span class="terminal-dot dot-green"></span>
                </div>
                <div class="terminal-content" id="terminal-output">
                    <span class="command">$ codeagent</span>
                    <span class="output">
╔══════════════════════════════════════════════════╗
║            AI-Powered Coding Agent               ║
║   Working Directory: /home/user/myproject        ║
╚══════════════════════════════════════════════════╝

You: _<span class="typing-cursor"></span></span>
                </div>
            </div>

            <div class="progress-bar">
                <div class="progress-fill" id="progress"></div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-value" id="iterations">0</span>
                    <span class="stat-label">Iterations</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value" id="files-explored">0</span>
                    <span class="stat-label">Files Explored</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value" id="files-modified">0</span>
                    <span class="stat-label">Files Modified</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value" id="functions-called">0</span>
                    <span class="stat-label">Function Calls</span>
                </div>
            </div>

            <div class="controls">
                <button class="btn" onclick="startDemo('bug')">Fix Bug Demo</button>
                <button class="btn" onclick="startDemo('feature')">Add Feature Demo</button>
                <button class="btn" onclick="startDemo('refactor')">Refactor Code Demo</button>
                <button class="btn" onclick="resetDemo()">Reset</button>
            </div>
        </div>
    </div>

    <script>
        let currentDemo = null;
        let demoTimeout = null;
        let stepIndex = 0;

        const demos = {
            bug: {
                command: "fix the memory leak in the cache manager",
                steps: [
                    { type: 'action', text: '→ get_files_info', step: 1 },
                    { type: 'action', text: '→ get_file_content: cache_manager.py', step: 1 },
                    { type: 'action', text: '→ get_file_content: tests/test_cache.py', step: 2 },
                    { type: 'action', text: '→ get_file_content: utils/memory.py', step: 2 },
                    { type: 'modified', text: '\n📝 Modifying cache_manager.py\n', step: 3 },
                    { type: 'diff', text: `Changes:
--- cache_manager.py (before)
+++ cache_manager.py (after)
@@ -23,6 +23,7 @@
     def set(self, key, value):
         self.cache[key] = value
<span class="diff-add">+        self._cleanup_old_entries()</span>
     
<span class="diff-add">+    def _cleanup_old_entries(self):
+        if len(self.cache) > self.max_size:
+            # Remove oldest entries
+            oldest_keys = sorted(self.cache.keys())[:len(self.cache) - self.max_size]
+            for key in oldest_keys:
+                del self.cache[key]</span>`, step: 3 },
                    { type: 'success', text: '\n✓ Successfully wrote to "cache_manager.py"', step: 3 },
                    { type: 'action', text: '→ run_python_file: tests/test_cache.py', step: 4 },
                    { type: 'output', text: '  Running tests...', step: 4 },
                    { type: 'output', text: '  .... ERROR: Test failed', step: 4 },
                    { type: 'action', text: '→ Analyzing error and fixing...', step: 5 },
                    { type: 'modified', text: '📝 Updating fix in cache_manager.py', step: 5 },
                    { type: 'action', text: '→ run_python_file: tests/test_cache.py', step: 5 },
                    { type: 'success', text: '\n✓ All tests passing!', step: 6 },
                    { type: 'success', text: '\n✓ Task Complete\n\nSummary:\n  • Iterations: 12\n  • Function calls: 18\n  • Files explored: 7\n  • Files modified: 1', step: 6 }
                ],
                stats: { iterations: 12, filesExplored: 7, filesModified: 1, functionsCalled: 18 }
            },
            feature: {
                command: "add a dark mode toggle to the UI",
                steps: [
                    { type: 'action', text: '→ get_files_info', step: 1 },
                    { type: 'action', text: '→ get_file_content: index.html', step: 1 },
                    { type: 'action', text: '→ get_file_content: styles.css', step: 1 },
                    { type: 'action', text: '→ get_file_content: js/main.js', step: 2 },
                    { type: 'output', text: '  Analyzing UI structure...', step: 2 },
                    { type: 'modified', text: '\n📄 Creating theme_toggle.js\n', step: 3 },
                    { type: 'diff', text: `New file content:
<span class="diff-add">+ function toggleDarkMode() {
+     const body = document.body;
+     body.classList.toggle('dark-mode');
+     localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
+ }
+ 
+ // Load saved preference
+ if (localStorage.getItem('darkMode') === 'true') {
+     document.body.classList.add('dark-mode');
+ }</span>`, step: 3 },
                    { type: 'modified', text: '\n📝 Modifying styles.css', step: 3 },
                    { type: 'modified', text: '📝 Modifying index.html', step: 3 },
                    { type: 'action', text: '→ run_python_file: ui_test.py', step: 4 },
                    { type: 'success', text: '\n✓ UI tests passing', step: 6 },
                    { type: 'success', text: '\n✓ Task Complete\n\nDark mode toggle successfully implemented!\n  • Toggle button in navigation\n  • CSS variables for theming\n  • LocalStorage persistence\n  • Smooth transitions', step: 6 }
                ],
                stats: { iterations: 8, filesExplored: 5, filesModified: 3, functionsCalled: 12 }
            },
            refactor: {
                command: "refactor the API endpoints to use dependency injection",
                steps: [
                    { type: 'action', text: '→ get_files_info', step: 1 },
                    { type: 'action', text: '→ Exploring api/ directory...', step: 1 },
                    { type: 'action', text: '→ get_file_content: api/endpoints.py', step: 1 },
                    { type: 'action', text: '→ get_file_content: api/dependencies.py', step: 2 },
                    { type: 'action', text: '→ get_file_content: api/services.py', step: 2 },
                    { type: 'output', text: '  Analyzing dependency patterns...', step: 2 },
                    { type: 'modified', text: '\n📄 Creating api/container.py', step: 3 },
                    { type: 'modified', text: '📝 Modifying api/endpoints.py', step: 3 },
                    { type: 'diff', text: `Changes:
<span class="diff-remove">- def get_user(user_id: int):
-     db = Database()
-     return db.query(user_id)</span>
<span class="diff-add">+ def get_user(user_id: int, db: Database = Depends(get_database)):
+     return db.query(user_id)</span>`, step: 3 },
                    { type: 'modified', text: '📝 Modifying api/dependencies.py', step: 3 },
                    { type: 'modified', text: '📝 Updating tests/test_api.py', step: 3 },
                    { type: 'action', text: '→ run_python_file: tests/test_api.py', step: 4 },
                    { type: 'output', text: '  Running API tests...', step: 4 },
                    { type: 'success', text: '  ✓ 45/45 tests passing', step: 6 },
                    { type: 'success', text: '\n✓ Refactoring Complete\n\nAll endpoints now use dependency injection!\n  • Improved testability\n  • Better separation of concerns\n  • Easier mocking for tests', step: 6 }
                ],
                stats: { iterations: 15, filesExplored: 12, filesModified: 4, functionsCalled: 24 }
            }
        };

        function typeText(element, text, callback) {
            let index = 0;
            const interval = setInterval(() => {
                if (index < text.length) {
                    element.innerHTML += text[index];
                    index++;
                } else {
                    clearInterval(interval);
                    if (callback) callback();
                }
            }, 30);
        }

        function updateStats(stats, duration = 2000) {
            const startTime = Date.now();
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                document.getElementById('iterations').textContent = 
                    Math.floor(stats.iterations * progress);
                document.getElementById('files-explored').textContent = 
                    Math.floor(stats.filesExplored * progress);
                document.getElementById('files-modified').textContent = 
                    Math.floor(stats.filesModified * progress);
                document.getElementById('functions-called').textContent = 
                    Math.floor(stats.functionsCalled * progress);
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };
            animate();
        }

        function highlightStep(stepNumber) {
            document.querySelectorAll('.workflow-step').forEach(step => {
                step.classList.remove('active');
            });
            if (stepNumber >= 1 && stepNumber <= 6) {
                document.getElementById(`step${stepNumber}`).classList.add('active');
            }
        }

        function startDemo(type) {
            resetDemo();
            currentDemo = demos[type];
            stepIndex = 0;
            
            const terminal = document.getElementById('terminal-output');
            terminal.innerHTML = `<span class="command">$ codeagent</span>
<span class="output">
╔══════════════════════════════════════════════════╗
║            AI-Powered Coding Agent               ║
║   Working Directory: /home/user/myproject        ║
╚══════════════════════════════════════════════════╝

You: ${currentDemo.command}</span>
<span class="output">Starting task: ${currentDemo.command}</span>

`;
            
            // Disable buttons during demo
            document.querySelectorAll('.btn').forEach(btn => {
                if (btn.textContent !== 'Reset') {
                    btn.disabled = true;
                }
            });
            
            runDemoStep();
        }

        function runDemoStep() {
            if (!currentDemo || stepIndex >= currentDemo.steps.length) {
                // Demo complete
                document.getElementById('progress').style.width = '100%';
                updateStats(currentDemo.stats);
                document.querySelectorAll('.btn').forEach(btn => {
                    btn.disabled = false;
                });
                return;
            }
            
            const step = currentDemo.steps[stepIndex];
            const terminal = document.getElementById('terminal-output');
            
            // Update progress bar
            const progress = ((stepIndex + 1) / currentDemo.steps.length) * 100;
            document.getElementById('progress').style.width = progress + '%';
            
            // Highlight workflow step
            highlightStep(step.step);
            
            // Add step output
            let outputHtml = '';
            switch(step.type) {
                case 'action':
                    outputHtml = `<span class="action">${step.text}</span>\n`;
                    break;
                case 'output':
                    outputHtml = `<span class="output">${step.text}</span>\n`;
                    break;
                case 'modified':
                    outputHtml = `<span class="modified">${step.text}</span>\n`;
                    break;
                case 'diff':
                    outputHtml = `<div class="diff">${step.text}</div>\n`;
                    break;
                case 'success':
                    outputHtml = `<span class="success">${step.text}</span>\n`;
                    break;
            }
            
            terminal.innerHTML += outputHtml;
            terminal.scrollTop = terminal.scrollHeight;
            
            // Update stats gradually
            if (stepIndex === currentDemo.steps.length - 1) {
                updateStats(currentDemo.stats);
            }
            
            stepIndex++;
            
            // Continue to next step
            const delay = step.type === 'diff' ? 2000 : 800;
            demoTimeout = setTimeout(runDemoStep, delay);
        }

        function resetDemo() {
            if (demoTimeout) {
                clearTimeout(demoTimeout);
                demoTimeout = null;
            }
            
            currentDemo = null;
            stepIndex = 0;
            
            // Reset terminal
            document.getElementById('terminal-output').innerHTML = `<span class="command">$ codeagent</span>
<span class="output">
╔══════════════════════════════════════════════════╗
║            AI-Powered Coding Agent               ║
║   Working Directory: /home/user/myproject        ║
╚══════════════════════════════════════════════════╝

You: _<span class="typing-cursor"></span></span>`;
            
            // Reset progress
            document.getElementById('progress').style.width = '0%';
            
            // Reset stats
            document.getElementById('iterations').textContent = '0';
            document.getElementById('files-explored').textContent = '0';
            document.getElementById('files-modified').textContent = '0';
            document.getElementById('functions-called').textContent = '0';
            
            // Reset workflow highlights
            document.querySelectorAll('.workflow-step').forEach(step => {
                step.classList.remove('active');
            });
            
            // Enable all buttons
            document.querySelectorAll('.btn').forEach(btn => {
                btn.disabled = false;
            });
        }

        // Initialize on load
        window.addEventListener('load', () => {
            // Add some initial animation to the workflow steps
            const steps = document.querySelectorAll('.workflow-step');
            steps.forEach((step, index) => {
                setTimeout(() => {
                    step.style.opacity = '0';
                    step.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        step.style.transition = 'all 0.5s ease';
                        step.style.opacity = '1';
                        step.style.transform = 'translateY(0)';
                    }, 50);
                }, index * 100);
            });
        });
    </script>