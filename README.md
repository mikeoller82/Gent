# 🤖 CodeAgent

<div align="center">

<pre>
 ██████╗ ███████╗███╗   ██╗████████╗
██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██║   ██║██╔══╝  ██║╚██╗██║   ██║   
╚██████╔╝███████╗██║ ╚████║   ██║   
 ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
</pre>

**Autonomous AI Coding Assistant - Never Gives Up**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.0-brightgreen)](https://ai.google.dev/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**An AI agent that explores codebases, implements features, fixes bugs, and refactors code autonomously through natural language commands.**

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Examples](#-examples) • [Architecture](#-architecture)

</div>

---

## 🎯 What Makes CodeAgent Different?

Unlike traditional coding assistants that just suggest code, **CodeAgent is truly autonomous**:

- **🔍 Explores First, Acts Second** - Navigates your entire codebase before making changes
- **🔄 Persistent Until Complete** - Won't stop until tests pass and verification succeeds
- **🛠️ Self-Correcting** - Analyzes errors, fixes them, and retries automatically
- **👁️ Real-Time Visibility** - Watch live diffs as it modifies your code
- **🚀 No Babysitting Required** - Give it a task and let it work

---

## ✨ Features

### 🔍 Intelligent Code Exploration
- Recursively explores project structures
- Understands file relationships and dependencies
- Identifies relevant code automatically

### 🛠️ Autonomous Implementation
- Writes production-ready code
- Implements features from natural language descriptions
- Follows existing code patterns and conventions

### 🔄 Self-Verification Loop
```
Implement → Test → Error? → Fix → Test → Success ✓
```

### 🎨 Beautiful Terminal Interface
- Syntax-highlighted diffs showing every change
- Live progress tracking
- Markdown-formatted responses
- Color-coded status indicators

### 🌐 Global CLI Tool
- Works from any directory
- Interactive REPL or single-command mode
- Verbose mode for debugging

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/codeagent.git
cd codeagent

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Configuration

Create a `.env` file:

```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

Or set environment variable:

```bash
export GEMINI_API_KEY='your-api-key-here'
```

### First Run

```bash
# Interactive mode
codeagent

# Single command
codeagent "list all Python files in this directory"
```

---

## 💡 Usage

### Interactive Mode (Recommended)

```bash
$ codeagent

╔══════════════════════════════════════════════════╗
║            AI-Powered Coding Agent               ║
║   Working Directory: /home/user/myproject       ║
╚══════════════════════════════════════════════════╝

You: fix the authentication bug
→ get_files_info
→ get_file_content
→ get_file_content
📝 Modifying auth.py
✓ Successfully wrote to "auth.py"
→ run_python_file
✓ Task Complete

You: exit
```

### Single Command Mode

```bash
# Simple task
codeagent "add logging to all functions"

# Complex task
codeagent "refactor the database layer to use async/await"

# With verbose output
codeagent "implement rate limiting" --verbose
```

### Available Commands in Interactive Mode

- Type your request in natural language
- `exit` or `quit` - Exit the program
- `clear` - Clear the screen
- `--verbose` prefix - Enable detailed output for that request

---

## 🎬 Examples

### Example 1: Bug Fix

```bash
$ codeagent "find and fix the memory leak in the cache manager"

Starting task: find and fix the memory leak in the cache manager

→ get_files_info
→ get_file_content
→ get_file_content
→ get_file_content

📝 Modifying cache_manager.py

Changes:
--- cache_manager.py (before)
+++ cache_manager.py (after)
@@ -23,6 +23,7 @@
     def set(self, key, value):
         self.cache[key] = value
+        self._cleanup_old_entries()
     
+    def _cleanup_old_entries(self):
+        if len(self.cache) > self.max_size:
+            # Remove oldest entries
+            oldest_keys = sorted(self.cache.keys())[:len(self.cache) - self.max_size]
+            for key in oldest_keys:
+                del self.cache[key]

✓ Successfully wrote to "cache_manager.py"

→ run_python_file
→ run_python_file

✓ Task Complete

Summary:
  • Iterations: 12
  • Function calls: 18
  • Files explored: 7
  • Files modified: 1
```

### Example 2: Feature Implementation

```bash
$ codeagent "add a dark mode toggle to the UI"

Starting task: add a dark mode toggle to the UI

→ get_files_info
→ get_file_content
→ get_file_content

📄 Creating theme_toggle.js
📝 Modifying styles.css
📝 Modifying index.html

✓ Task Complete

The dark mode toggle has been successfully implemented with:
- Toggle button in the navigation bar
- CSS variables for theme switching
- LocalStorage persistence
- Smooth transitions between themes

Modified files:
  • index.html
  • styles.css
  • theme_toggle.js
```

### Example 3: Refactoring

```bash
$ codeagent "refactor the API endpoints to use dependency injection"

Starting task: refactor the API endpoints to use dependency injection

→ get_files_info
→ get_file_content (x8 files)

📝 Modifying api/endpoints.py
📝 Modifying api/dependencies.py
📄 Creating api/container.py
📝 Modifying tests/test_api.py

→ run_python_file
→ run_python_file

✓ All tests passing

Summary:
  • Iterations: 15
  • Function calls: 24
  • Files explored: 12
  • Files modified: 4
```

---

## 🏗️ Architecture

### Agent Loop

```
┌─────────────────────────────────────────────────────┐
│  User Input: "enhance the error handling"          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   1. EXPLORE         │
          │   get_files_info()   │
          │   get_file_content() │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   2. ANALYZE         │
          │   Understand code    │
          │   Identify issues    │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   3. IMPLEMENT       │
          │   write_file()       │
          │   Show diffs         │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   4. VERIFY          │
          │   run_python_file()  │
          │   Check output       │
          └──────────┬───────────┘
                     │
                   Error?
                   ┌─┴─┐
                 Yes   No
                   │    │
          ┌────────┘    └─────────┐
          │                       │
          ▼                       ▼
   ┌──────────────┐      ┌───────────────┐
   │   5. FIX     │      │   6. REPORT   │
   │   Analyze    │      │   Success!    │
   │   Fix issue  │      └───────────────┘
   └──────┬───────┘
          │
          └──────────┐
                     │
                     ▼
              Back to step 4
```

### Function Inventory

| Function | Purpose | Example |
|----------|---------|---------|
| `get_files_info(directory)` | List directory contents | Explore project structure |
| `get_file_content(file_path)` | Read file contents | Understand existing code |
| `write_file(file_path, content)` | Create/modify files | Implement changes |
| `run_python_file(file_path, args)` | Execute Python scripts | Run tests, verify changes |

### Security Model

All operations are sandboxed to the working directory:

- ✅ Path validation prevents directory traversal (`../`, absolute paths)
- ✅ No network access from agent functions
- ✅ File operations limited to current project
- ✅ Python execution restricted to project files

---

## 🎨 Terminal Output Examples

### File Modification with Diff

```
📝 Modifying calculator.py

Changes:
--- calculator.py (before)
+++ calculator.py (after)
@@ -15,7 +15,10 @@
 
 def divide(a, b):
-    return a / b
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
+    return a / b

✓ Successfully wrote to "calculator.py" (342 characters written)
```

### New File Creation

```
📄 Creating utils/logger.py

New file content:
  1 │ import logging
  2 │ from datetime import datetime
  3 │ 
  4 │ def setup_logger(name):
  5 │     logger = logging.getLogger(name)
  6 │     logger.setLevel(logging.INFO)
  7 │     return logger

✓ Successfully wrote to "utils/logger.py" (156 characters written)
```

---

## 📊 Comparison with Other Tools

| Feature | CodeAgent | GitHub Copilot | ChatGPT | Cursor |
|---------|-----------|----------------|---------|--------|
| Autonomous exploration | ✅ | ❌ | ❌ | ⚠️ |
| Self-verification | ✅ | ❌ | ❌ | ❌ |
| Persistent until complete | ✅ | ❌ | ❌ | ❌ |
| Live diff display | ✅ | ❌ | ❌ | ✅ |
| CLI interface | ✅ | ❌ | ❌ | ❌ |
| Multi-file changes | ✅ | ⚠️ | ❌ | ✅ |
| Error correction loop | ✅ | ❌ | ❌ | ⚠️ |

---

## ⚙️ Advanced Configuration

### Custom System Prompt

Edit `codeagent/main.py` to customize the agent's behavior:

```python
system_prompt = """
Your custom instructions here...
"""
```

### Iteration Limits

Adjust safety limits in `process_request()`:

```python
max_iterations = 100  # Default: 100
```

### File Size Limits

Configure in `codeagent/config.py`:

```python
MAX_FILE_CHARS = 10000  # Characters before truncation
```

---

## 🛡️ Safety & Best Practices

### What CodeAgent Does

✅ Operates only within the current working directory  
✅ Shows all changes with diffs before applying  
✅ Tracks all file modifications  
✅ Provides detailed summaries  

### What You Should Do

✅ Review changes before committing  
✅ Test in a separate branch first  
✅ Use version control (git)  
✅ Keep backups of important files  
✅ Start with `--verbose` mode to understand behavior  

### What CodeAgent Won't Do

❌ Access files outside working directory  
❌ Make network requests  
❌ Execute arbitrary system commands  
❌ Modify system files  

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests if applicable
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/Gent.git
cd codeagent

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest
```

---

## 📝 Roadmap

- [ ] Support for more programming languages
- [ ] Integration with git for automatic commits
- [ ] Web interface
- [ ] Plugin system for custom functions
- [ ] Multi-agent collaboration
- [ ] Code review mode
- [ ] Performance profiling integration

---

## 🐛 Troubleshooting

**Issue: Agent keeps reading the same files**  
Solution: This is normal during exploration phase. Agent will eventually move to implementation.

**Issue: Agent stops before completing**  
Solution: Check the error message. Often needs more context or has hit an edge case. Try rephrasing your request.

**Issue: API errors**  
Solution: Verify your `GEMINI_API_KEY` is set correctly and has quota remaining.

**Issue: Changes not appearing**  
Solution: Ensure you're in the correct directory. Use `--verbose` to see exactly what's happening.

---

## 📄 License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Powered by [Google Gemini 2.0 Flash](https://ai.google.dev/)
- Terminal UI with [Rich](https://github.com/Textualize/rich)
- Inspired by autonomous agent research and agentic workflows

---

## 📞 Connect

- Report bugs: [Issues](https://github.com/yourusername/codeagent/issues)
- Request features: [Discussions](https://github.com/yourusername/codeagent/discussions)
- Twitter: [@yourhandle](https://twitter.com/yourhandle)

---

<div align="center">

⭐ **Star this repo if you find it useful!**

Made with persistence and AI 🤖

</div>
