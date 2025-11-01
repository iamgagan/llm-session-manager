# 🧪 Manual Testing Guide - All Features

Complete guide to test all 29 CLI commands individually.

**Date:** October 27, 2025
**Status:** 100% Feature Complete (29/29 commands)

---

## 📋 Table of Contents

1. [Setup & Installation](#1-setup--installation)
2. [Session Discovery](#2-session-discovery)
3. [Session Management](#3-session-management)
4. [Health Monitoring](#4-health-monitoring)
5. [Export Features](#5-export-features)
6. [Tagging System](#6-tagging-system)
7. [Memory System (Cognee)](#7-memory-system-cognee)
8. [Project Management](#8-project-management)
9. [Advanced Features](#9-advanced-features)
10. [MCP Integration](#10-mcp-integration)

---

## 1. Setup & Installation

### Test 1: Installation
```bash
# Clone the repository
git clone https://github.com/iamgagan/llm-session-manager.git
cd llm-session-manager

# Install dependencies
poetry install
```

**Expected Output:**
- Dependencies installed successfully
- No errors

### Test 2: CLI Access
```bash
# Verify CLI is accessible
poetry run python -m llm_session_manager.cli --help

# Or use the short alias
llm-session --help
```

**Expected Output:**
```
Usage: llm-session [OPTIONS] COMMAND [ARGS]...

🤖 LLM Session Manager - Monitor and manage your AI coding sessions

Commands:
  list        📋 List all recorded sessions
  info        ℹ️  Show detailed information about a session
  monitor     📊 Monitor active sessions in real-time
  ...
```

---

## 2. Session Discovery

### Test 3: Auto-Discovery
```bash
# Discover active AI coding sessions
poetry run python -m llm_session_manager.cli list --active
```

**Expected Output:**
- Lists currently running Claude Code/Cursor/Copilot sessions
- Shows session IDs, tool names, start times
- If no active sessions: "No active sessions found"

### Test 4: Discovery with Details
```bash
# Show detailed discovery info
poetry run python -m llm_session_manager.cli discover
```

**Expected Output:**
```
🔍 Discovering AI coding sessions...

Active Sessions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 claude_code_12345
    Tool: Claude Code
    Started: 2025-10-27 10:30:00
    Duration: 2h 15m
    Status: Active
```

---

## 3. Session Management

### Test 5: List All Sessions
```bash
# List all sessions (active + historical)
poetry run python -m llm_session_manager.cli list
```

**Expected Output:**
- Table showing all sessions
- Columns: ID, Tool, Project, Started, Duration, Status

### Test 6: List Only Active Sessions
```bash
poetry run python -m llm_session_manager.cli list --active
```

**Expected Output:**
- Only currently running sessions
- Real-time status indicators

### Test 7: Session Info
```bash
# Get detailed info about a specific session
# Replace <session-id> with actual ID from list command
poetry run python -m llm_session_manager.cli info <session-id>
```

**Expected Output:**
```
📊 Session Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session ID:     claude_code_12345
Tool:           Claude Code
Project:        llm-session-manager
Status:         Active
Started:        2025-10-27 10:30:00
Duration:       2h 15m

💬 Conversation Stats:
   Messages:    42
   Tokens:      15,234
   Cost:        $0.23

🏥 Health Score: 92/100
   ✅ Token usage healthy
   ✅ Activity level good
   ⚠️  2 minor errors detected
```

### Test 8: Initialize New Session
```bash
# Manually initialize a session (if auto-discovery fails)
poetry run python -m llm_session_manager.cli init --tool claude_code --project my-project
```

**Expected Output:**
```
✅ Session initialized: claude_code_67890
```

---

## 4. Health Monitoring

### Test 9: Real-Time Monitor
```bash
# Launch real-time monitoring dashboard
poetry run python -m llm_session_manager.cli monitor
```

**Expected Output:**
- Live updating dashboard
- Health scores, token counts, activity metrics
- **Exit:** Press `Ctrl+C` (keyboard shortcuts q/r/h are best-effort)

### Test 10: Health Check (Single)
```bash
# Check health of specific session
poetry run python -m llm_session_manager.cli health <session-id>
```

**Expected Output:**
```
🏥 Health Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 92/100 (🟢 Healthy)

Factors:
✅ Token Usage:    45/100 (Good)
✅ Duration:       20/100 (Normal)
✅ Activity:       25/100 (Active)
⚠️  Error Rate:    2/100 (Minor issues)

Recommendations:
💡 Session is healthy, continue current workflow
```

### Test 11: Health Stats Summary
```bash
# View health statistics across all sessions
poetry run python -m llm_session_manager.cli health-stats
```

**Expected Output:**
- Average health scores
- Common issues detected
- Overall system health

---

## 5. Export Features

### Test 12: Export as JSON
```bash
# Export session to JSON format
poetry run python -m llm_session_manager.cli export <session-id> --format json --output session.json
```

**Expected Output:**
```
✅ Session exported to: session.json
```

**Verify:**
```bash
cat session.json
```

### Test 13: Export as YAML
```bash
# Export session to YAML format
poetry run python -m llm_session_manager.cli export <session-id> --format yaml --output session.yaml
```

**Expected Output:**
```
✅ Session exported to: session.yaml
```

### Test 14: Export as Markdown
```bash
# Export session to Markdown report
poetry run python -m llm_session_manager.cli export <session-id> --format markdown --output session.md
```

**Expected Output:**
- Creates formatted markdown file
- Includes session details, conversation, health analysis

**Verify:**
```bash
cat session.md
```

### Test 15: Export with Custom Template
```bash
# Export using custom template (if you have one)
poetry run python -m llm_session_manager.cli export <session-id> --template custom.jinja2
```

---

## 6. Tagging System

### Test 16: Add Tags to Session
```bash
# Tag a session with keywords
poetry run python -m llm_session_manager.cli tag <session-id> bugfix authentication urgent
```

**Expected Output:**
```
✅ Tagged session <session-id> with: bugfix, authentication, urgent
```

### Test 17: List Tags
```bash
# View all tags used across sessions
poetry run python -m llm_session_manager.cli list-tags
```

**Expected Output:**
```
📌 Available Tags
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bugfix          (12 sessions)
feature         (8 sessions)
authentication  (5 sessions)
urgent          (3 sessions)
refactoring     (7 sessions)
```

### Test 18: Filter Sessions by Tag
```bash
# Find sessions with specific tag
poetry run python -m llm_session_manager.cli list --tag bugfix
```

**Expected Output:**
- Lists only sessions tagged with "bugfix"

### Test 19: Remove Tags
```bash
# Remove tag from session
poetry run python -m llm_session_manager.cli untag <session-id> urgent
```

**Expected Output:**
```
✅ Removed tag 'urgent' from session <session-id>
```

### Test 20: Auto-Tag (AI-Powered)
```bash
# Let AI suggest tags based on session content
poetry run python -m llm_session_manager.cli auto-tag <session-id>
```

**Expected Output:**
```
🤖 Suggested tags for session <session-id>:
   - bugfix
   - database-migration
   - testing

Apply these tags? [y/N]:
```

**Note:** Requires OpenAI API key in environment

---

## 7. Memory System (Cognee)

### Test 21: Memory Stats
```bash
# View memory system statistics
poetry run python -m llm_session_manager.cli memory-stats
```

**Expected Output:**
```
🧠 Memory System Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Sessions Indexed:  15
Total Chunks:            342
Total Embeddings:        1,024
Memory Size:             2.3 MB
Last Updated:            2025-10-27 14:30:00
```

### Test 22: List Memories
```bash
# View all indexed memories
poetry run python -m llm_session_manager.cli memory-list
```

**Expected Output:**
- Lists all sessions with memory indices
- Shows chunk counts and metadata

### Test 23: Search Sessions by Content
```bash
# Semantic search across all sessions
poetry run python -m llm_session_manager.cli search "database migration fix"
```

**Expected Output:**
```
🔍 Search Results for: "database migration fix"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. claude_code_60420 (95% match)
   "Fixed database schema by adding tags column..."
   Tags: bugfix, database
   Date: 2025-10-26

2. cursor_12345 (87% match)
   "Migrated sessions table to include new fields..."
   Tags: migration, database
   Date: 2025-10-25
```

### Test 24: Recommend Related Sessions
```bash
# Get AI recommendations for similar sessions
poetry run python -m llm_session_manager.cli recommend <session-id>
```

**Expected Output:**
```
💡 Related Sessions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Based on: claude_code_60420 (database migration)

Similar sessions:
1. cursor_12345 - Database schema updates (92% similar)
2. copilot_67890 - Migration scripts (85% similar)
3. claude_code_11111 - SQL fixes (78% similar)
```

---

## 8. Project Management

### Test 25: Set Project Name
```bash
# Associate session with project
poetry run python -m llm_session_manager.cli project <session-id> llm-session-manager
```

**Expected Output:**
```
✅ Set project 'llm-session-manager' for session <session-id>
```

### Test 26: List Projects
```bash
# View all projects
poetry run python -m llm_session_manager.cli list-projects
```

**Expected Output:**
```
📁 Projects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
llm-session-manager     (12 sessions)
my-web-app              (5 sessions)
api-backend             (8 sessions)
```

### Test 27: Filter by Project
```bash
# List sessions for specific project
poetry run python -m llm_session_manager.cli list --project llm-session-manager
```

**Expected Output:**
- Only sessions from llm-session-manager project

---

## 9. Advanced Features

### Test 28: Set Description
```bash
# Add human-readable description
poetry run python -m llm_session_manager.cli describe <session-id> "Fixed database migration issue with tagging system"
```

**Expected Output:**
```
✅ Description set for session <session-id>
```

### Test 29: View Description
```bash
# View current description
poetry run python -m llm_session_manager.cli describe <session-id> --show
```

**Expected Output:**
```
📝 Description for <session-id>:
Fixed database migration issue with tagging system
```

---

## 10. MCP Integration

### Test 30: MCP Configuration
```bash
# View MCP server configuration
poetry run python -m llm_session_manager.cli mcp-config
```

**Expected Output:**
```json
{
  "mcpServers": {
    "llm-session-manager": {
      "command": "poetry",
      "args": ["run", "python", "-m", "llm_session_manager.mcp_server"],
      "env": {
        "PYTHONPATH": "/Users/gagan/llm-session-manager"
      }
    }
  }
}
```

### Test 31: MCP Server Status
```bash
# Check if MCP server is running (if you've configured it in Claude Desktop)
# This is tested through Claude Desktop app, not CLI
```

**To test MCP integration:**
1. Add MCP config to `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Restart Claude Desktop
3. Ask Claude: "What sessions do I have?"
4. Claude should use the MCP server to retrieve your sessions

---

## 📊 Quick Test Suite

Run all basic tests in sequence:

```bash
# 1. Installation check
poetry run python -m llm_session_manager.cli --help

# 2. Discover sessions
poetry run python -m llm_session_manager.cli list

# 3. View session details (replace with your session ID)
SESSION_ID=$(poetry run python -m llm_session_manager.cli list | grep claude_code | head -1 | awk '{print $1}')
poetry run python -m llm_session_manager.cli info $SESSION_ID

# 4. Check health
poetry run python -m llm_session_manager.cli health $SESSION_ID

# 5. Export to JSON
poetry run python -m llm_session_manager.cli export $SESSION_ID --format json --output /tmp/test.json

# 6. Add tags
poetry run python -m llm_session_manager.cli tag $SESSION_ID testing manual-test

# 7. View memory stats
poetry run python -m llm_session_manager.cli memory-stats

# 8. Search
poetry run python -m llm_session_manager.cli search "testing"

# 9. Set description
poetry run python -m llm_session_manager.cli describe $SESSION_ID "Manual testing session"

# 10. View MCP config
poetry run python -m llm_session_manager.cli mcp-config

echo "✅ All basic tests complete!"
```

---

## 🔍 Troubleshooting

### No sessions found?
- Make sure you have an active Claude Code/Cursor/Copilot session
- Try running the discovery manually: `poetry run python -m llm_session_manager.cli discover`

### Database errors?
- Run migration: `poetry run python migrate_database.py`
- Check database exists: `ls -la data/sessions.db`

### Import errors?
- Reinstall: `poetry install`
- Clear cache: `rm -rf __pycache__`

### Monitor not working?
- Use `Ctrl+C` to exit (keyboard shortcuts are best-effort)
- Check terminal supports ANSI colors

---

## ✅ Testing Checklist

Use this checklist to track your testing:

- [ ] Installation & CLI access
- [ ] Session discovery
- [ ] List sessions (all & active)
- [ ] Session info
- [ ] Initialize new session
- [ ] Real-time monitor
- [ ] Health check
- [ ] Export JSON
- [ ] Export YAML
- [ ] Export Markdown
- [ ] Add tags
- [ ] List tags
- [ ] Filter by tag
- [ ] Remove tags
- [ ] Auto-tag (AI)
- [ ] Memory stats
- [ ] Memory list
- [ ] Search sessions
- [ ] Recommend sessions
- [ ] Set project
- [ ] List projects
- [ ] Filter by project
- [ ] Set description
- [ ] View description
- [ ] MCP configuration
- [ ] MCP server integration

---

## 📈 Success Criteria

All features pass if:
- ✅ No errors during execution
- ✅ Output matches expected format
- ✅ Data persists across commands
- ✅ Search and filtering work correctly
- ✅ Export files are valid and readable

---

**Last Updated:** October 27, 2025
**Version:** 1.0.0
**Feature Coverage:** 100% (29/29 commands)
