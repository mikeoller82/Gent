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
[![MCP Enabled](https://img.shields.io/badge/MCP-Enabled-orange)](https://modelcontextprotocol.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**An AI agent that explores codebases, implements features, fixes bugs, and refactors code autonomously through natural language commands. Now with Model Context Protocol (MCP) for enhanced capabilities.**

[Features](#-features) • [Quick Start](#-quick-start) • [MCP Integration](#-mcp-integration) • [Usage](#-usage) • [Examples](#-examples)

</div>

---

## 🎯 What Makes CodeAgent Different?

Unlike traditional coding assistants that just suggest code, **CodeAgent is truly autonomous**:

- **🔍 Explores First, Acts Second** - Navigates your entire codebase before making changes
- **🔄 Persistent Until Complete** - Won't stop until tests pass and verification succeeds
- **🛠️ Self-Correcting** - Analyzes errors, fixes them, and retries automatically
- **👁️ Real-Time Visibility** - Watch live diffs as it modifies your code
- **📚 Access to Current Documentation** - Uses MCP to fetch up-to-date library docs instead of outdated training data
- **🌐 Browser Automation** - Can test web apps, scrape data, and automate browser tasks
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
- **NEW:** Uses current library documentation via Context7 MCP

### 🔄 Self-Verification Loop
```
Implement → Test → Error? → Fix → Test → Success ✓
```

### 🎨 Beautiful Terminal Interface
- Syntax-highlighted diffs showing every change
- Live progress tracking
- Markdown-formatted responses
- Color-coded status indicators

### 🌐 Model Context Protocol (MCP) Integration
- **Context7**: Access up-to-date documentation for any library
- **Playwright**: Browser automation and web testing
- **Markitdown**: Convert PDFs, Word docs, Excel to Markdown
- **Filesystem**: Enhanced file operations
- **Brave Search**: Web search capabilities
- **GitHub**: Repository integration

### 🌐 Global CLI Tool
- Works from any directory
- Interactive REPL or single-command mode
- Verbose mode for debugging

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Node.js 18+ (for MCP servers via NPX)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Gent.git
cd Gent

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Install MCP dependencies
pip install mcp httpx
```

### Configuration

Create a `.env` file:

```bash
# Required
GEMINI_API_KEY=your-api-key-here

# Optional: Enable MCP servers (defaults to context7)
MCP_ENABLED_SERVERS=context7,playwright,markitdown

# Optional: Disable MCP entirely
# DISABLE_MCP=true
```

### First Run

```bash
# Interactive mode
codeagent

# Single command
codeagent "list all Python files in this directory"

# Use MCP features
codeagent "How do I use Next.js 15 server actions? Use the latest docs."
```

---

## 🔌 MCP Integration

CodeAgent integrates with the Model Context Protocol to provide enhanced capabilities beyond its core functionality.

### Available MCP Servers

| Server | Purpose | Status | Setup |
|--------|---------|--------|-------|
| **context7** | Up-to-date library documentation | ✅ Default | No setup needed |
| **playwright** | Browser automation & testing | ⚙️ Optional | Installs on first use |
| **markitdown** | Convert documents to Markdown | ⚙️ Optional | Installs on first use |
| **filesystem** | Enhanced file operations | ⚙️ Optional | Installs on first use |
| **github** | GitHub API integration | ⚙️ Optional | Requires API token |
| **brave-search** | Web search | ⚙️ Optional | Requires API key |

### Quick MCP Setup

**Enable specific servers:**
```bash
# In .env file
MCP_ENABLED_SERVERS=context7,playwright,markitdown
```

**Disable MCP:**
```bash
# In .env file
DISABLE_MCP=true
```

### MCP Use Cases

**Get current documentation:**
```bash
You: How do I use React 19 hooks? Use the latest documentation.
→ mcp_context7_resolve_library_id
→ mcp_context7_get_library_docs
✓ Returns current React 19 docs
```

**Automate browser testing:**
```bash
You: Test the login form on staging.myapp.com
→ mcp_playwright_navigate
→ mcp_playwright_fill
→ mcp_playwright_click
→ mcp_playwright_screenshot
✓ Automated test complete
```

**Convert documents:**
```bash
You: Convert this PDF to markdown: report.pdf
→ mcp_markitdown_convert_to_markdown
✓ PDF converted to Markdown
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
🔌 MCP Servers: context7, playwright

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

# Complex task with MCP
codeagent "refactor to use the latest Next.js 15 patterns"

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

### Example 1: Using Current Documentation (MCP)

```bash
$ codeagent "Build a Next.js 15 app with server actions using latest best practices"

Starting task: Build a Next.js 15 app with server actions

→ mcp_context7_resolve_library_id
→ mcp_context7_get_library_docs

📄 Creating app/page.tsx
📄 Creating app/actions.ts
📄 Creating app/layout.tsx

✓ Task Complete

Built Next.js 15 app using current server actions patterns:
- App router with React Server Components
- Server actions for data mutations
- TypeScript with proper typing
- Latest Next.js 15 features

Modified files:
  • app/page.tsx
  • app/actions.ts
  • app/layout.tsx
```

### Example 2: Bug Fix

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

✓ Successfully wrote to "cache_manager.py"

→ run_python_file
✓ Task Complete
```

### Example 3: Browser Automation (MCP)

```bash
$ codeagent "Test the signup flow on staging.example.com"

Starting task: Test the signup flow

→ mcp_playwright_navigate
→ mcp_playwright_fill
→ mcp_playwright_click
→ mcp_playwright_wait_for
→ mcp_playwright_screenshot

✓ Task Complete

Signup flow tested successfully:
- Navigated to staging.example.com/signup
- Filled email and password fields
- Clicked submit button
- Verified redirect to dashboard
- Screenshot saved: signup-test.png

All assertions passed ✓
```

### Example 4: Document Processing (MCP)

```bash
$ codeagent "Convert the project requirements PDF to markdown"

Starting task: Convert requirements PDF

→ get_files_info
→ mcp_markitdown_convert_to_markdown

📄 Creating requirements.md

✓ Task Complete

Converted requirements.pdf to Markdown:
- Preserved document structure
- Extracted all sections
- Formatted tables correctly
- Maintained heading hierarchy

Output: requirements.md
```

---

## 🏗️ Architecture

### Agent Loop with MCP

```
┌─────────────────────────────────────────────────────┐
│  User Input: "Use latest React patterns"           │
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
          │   2. RESEARCH (NEW)  │
          │   MCP: context7      │
          │   Get current docs   │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   3. ANALYZE         │
          │   Understand code    │
          │   Identify updates   │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   4. IMPLEMENT       │
          │   write_file()       │
          │   Show diffs         │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   5. VERIFY          │
          │   run_python_file()  │
          │   MCP: playwright    │
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
   │   6. FIX     │      │   7. REPORT   │
   │   Analyze    │      │   Success!    │
   │   Fix issue  │      └───────────────┘
   └──────┬───────┘
          │
          └──────────┐
                     │
                     ▼
              Back to step 5
```

### Function Inventory

| Function | Purpose | Type |
|----------|---------|------|
| `get_files_info(directory)` | List directory contents | Native |
| `get_file_content(file_path)` | Read file contents | Native |
| `write_file(file_path, content)` | Create/modify files | Native |
| `run_python_file(file_path, args)` | Execute Python scripts | Native |
| `mcp_context7_get_library_docs` | Get current documentation | MCP |
| `mcp_playwright_navigate` | Navigate browser | MCP |
| `mcp_markitdown_convert` | Convert documents | MCP |

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
| **Current documentation (MCP)** | ✅ | ❌ | ❌ | ⚠️ |
| **Browser automation (MCP)** | ✅ | ❌ | ❌ | ❌ |
| **Document processing (MCP)** | ✅ | ❌ | ❌ | ❌ |

---

## ⚙️ Advanced Configuration

### MCP Server Configuration

Edit `.env` to enable/disable servers:

```bash
# Enable multiple servers
MCP_ENABLED_SERVERS=context7,playwright,markitdown,filesystem

# Context7 only (default)
MCP_ENABLED_SERVERS=context7

# Disable MCP completely
DISABLE_MCP=true
```

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

---

## 🛡️ Safety & Best Practices

### What CodeAgent Does

✅ Operates only within the current working directory  
✅ Shows all changes with diffs before applying  
✅ Tracks all file modifications  
✅ Provides detailed summaries  
✅ Uses MCP servers safely (sandboxed)  

### What You Should Do

✅ Review changes before committing  
✅ Test in a separate branch first  
✅ Use version control (git)  
✅ Keep backups of important files  
✅ Start with `--verbose` mode to understand behavior  
✅ Review MCP server configurations before enabling  

### What CodeAgent Won't Do

❌ Access files outside working directory  
❌ Make unauthorized network requests  
❌ Execute arbitrary system commands  
❌ Modify system files  
❌ Share data without permission  

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
cd Gent

# Install in development mode
uv pip install -e ".[dev]"

# Install MCP dependencies
pip install mcp httpx

# Run tests
pytest
```

---

## 📝 Roadmap

- [x] Model Context Protocol (MCP) integration
- [x] Access to current library documentation
- [x] Browser automation capabilities
- [ ] Support for more programming languages
- [ ] Integration with git for automatic commits
- [ ] Web interface
- [ ] Plugin system for custom functions
- [ ] Multi-agent collaboration
- [ ] Additional MCP servers (Slack, Gmail, etc.)
- [ ] Code review mode

---

## 🐛 Troubleshooting

### General Issues

**Issue: Agent keeps reading the same files**  
Solution: This is normal during exploration phase. Agent will eventually move to implementation.

**Issue: Agent stops before completing**  
Solution: Check the error message. Often needs more context or has hit an edge case. Try rephrasing your request.

**Issue: API errors**  
Solution: Verify your `GEMINI_API_KEY` is set correctly and has quota remaining.

### MCP-Specific Issues

**Issue: "MCP SDK not installed"**  
Solution: Run `pip install mcp httpx`

**Issue: MCP servers not connecting**  
Solution: Ensure Node.js 18+ is installed. First run downloads dependencies automatically.

**Issue: "Unknown server" error**  
Solution: Check server name spelling in `MCP_ENABLED_SERVERS`. Available: context7, playwright, markitdown, filesystem, github, brave-search

**Issue: Playwright fails to start**  
Solution: First run downloads browser binaries (~300MB). Requires internet connection.

**Issue: Want to disable MCP**  
Solution: Set `DISABLE_MCP=true` in `.env` file. All native functions continue to work.

---

## 📄 License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Powered by [Google Gemini 2.0 Flash](https://ai.google.dev/)
- Terminal UI with [Rich](https://github.com/Textualize/rich)
- MCP integration via [Model Context Protocol](https://modelcontextprotocol.io/)
- Context7 for up-to-date documentation via [Upstash Context7](https://github.com/upstash/context7)
- Browser automation via [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- Inspired by autonomous agent research and agentic workflows

---

## 📞 Connect

- Report bugs: [Issues](https://github.com/mikeoller82/Gent/issues)
- Request features: [Discussions](https://github.com/mikeoller82/Gent/discussions)
- MCP Servers: [MCP Registry](https://github.com/modelcontextprotocol/servers)
- Twitter: [@mikeoller1982](https://x.com/@mikeoller1982)

---

<div align="center">

⭐ **Star this repo if you find it useful!**

Made with persistence and AI 🤖

**Now enhanced with MCP for up-to-date knowledge and automation** 🔌

</div>
