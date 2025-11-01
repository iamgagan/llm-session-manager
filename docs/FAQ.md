# ❓ Frequently Asked Questions

## General Questions

### What is LLM Session Manager?
LLM Session Manager is a free, open-source monitoring and collaboration platform for AI coding assistants. It provides unified monitoring across Claude Code, Cursor, and GitHub Copilot with health scoring, token tracking, and team analytics.

### Which AI coding tools are supported?
- ✅ Claude Code (Anthropic)
- ✅ Cursor IDE
- ✅ GitHub Copilot
- 🔜 More coming soon!

### Is it really free?
Yes! 100% free and open-source (MIT License). No hidden costs, no paid tiers, no limitations.

### Does it work on my operating system?
- ✅ macOS
- ✅ Linux
- ✅ Windows (WSL recommended)

---

## Privacy & Security

### Where is my data stored?
100% locally on your machine. Your code and session data never leave your computer unless you explicitly use the team collaboration features.

### Is my code sent to any servers?
No. LLM Session Manager only monitors your AI coding sessions locally. It doesn't access your code or send data to external servers.

### Can I use this in a corporate environment?
Yes! Since everything runs locally, it's safe for corporate/enterprise use. Your company's code stays private.

---

## Comparison Questions

### How is this different from Claude Code Analytics?
| Feature | Claude Analytics | LLM Session Manager |
|---------|-----------------|---------------------|
| **Price** | $30-60/user/month | Free |
| **Multi-tool** | Claude only | Claude + Cursor + Copilot |
| **Health scoring** | No | Yes |
| **Local/private** | Cloud-based | 100% local |
| **Team collaboration** | Limited | Full-featured |

### How is this different from AWS AgentCore?
Completely different use cases:
- **AWS AgentCore:** Production AI agent infrastructure (for deploying customer-facing agents)
- **LLM Session Manager:** Development monitoring (for developers using AI coding tools)

See [AWS AgentCore Comparison](../AWS_AGENTCORE_COMPARISON.md) for details.

### Why not just use the built-in analytics?
Most AI coding tools don't have built-in analytics, and if they do:
- ❌ They're tool-specific (can't see Cursor + Copilot together)
- ❌ They require expensive enterprise plans
- ❌ They don't have health scoring
- ❌ They don't warn you before sessions degrade

---

## Technical Questions

### What are the system requirements?
- Python 3.10+
- 2GB RAM minimum
- 500MB disk space
- Active AI coding assistant (Claude/Cursor/Copilot)

### Can I use this without an AI coding assistant?
The tool is designed to monitor AI coding sessions. Without an active Claude Code, Cursor, or Copilot session, there's nothing to monitor.

### How does session discovery work?
LLM Session Manager uses a hybrid detection system:
1. Process inspection (finds running AI tool processes)
2. Registry-based detection (checks known AI tool signatures)
3. Zero configuration required - it just works!

### Does it slow down my AI coding tools?
No. LLM Session Manager uses minimal resources (< 1% CPU) and doesn't interfere with your AI tools.

---

## Usage Questions

### How do I know when to restart a session?
The health score tells you! When it drops below 70%, you'll get recommendations:
- 🟢 90-100: Session is healthy
- 🟡 70-89: Minor issues, monitor closely
- 🟠 40-69: Consider restarting soon
- 🔴 0-39: Restart recommended

### Can I use this with multiple AI tools at once?
Yes! That's the point. Track Claude Code, Cursor, and Copilot all in one dashboard.

### How accurate is the token tracking?
Token counts are estimated using tiktoken (same library Claude uses). Accuracy: ~95-98%.

### Can I export my session data?
Yes! Export to:
- JSON (for integrations)
- YAML (for configs)
- Markdown (for reports)

---

## Team Collaboration

### How does team collaboration work?
1. Start the collaboration backend server
2. Share a session using `llm-session share <session-id>`
3. Teammates can view sessions via web dashboard
4. Real-time updates via WebSocket

### Is team collaboration also free?
Yes! Self-hosted collaboration is 100% free.

### Do teammates need to install anything?
For viewing: Just a web browser (access the dashboard URL)
For full features: Install LLM Session Manager

---

## Troubleshooting

### "No sessions found" - What do I do?
1. Make sure you have Claude Code, Cursor, or Copilot running
2. Try running: `llm-session discover`
3. Check if processes are running: `ps aux | grep -i "claude\|cursor\|copilot"`

### Sessions not persisting?
Run `llm-session list` first - this discovers and saves sessions to the database.

### Health scores seem wrong?
Health scores are based on:
- Token usage (higher usage = lower score)
- Session duration (very long = lower score)
- Activity level (idle = lower score)
- Error count (more errors = lower score)

### Import errors when running commands?
Make sure you installed with: `poetry install`
If issues persist: `poetry install --no-cache`

---

## Contributing

### How can I contribute?
See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Setting up development environment
- Running tests
- Code style guidelines
- Pull request process

### I found a bug. Where do I report it?
GitHub Issues: https://github.com/iamgagan/llm-session-manager/issues

### Can I request a feature?
Absolutely! Open a GitHub Issue with the "feature request" label.

---

## Roadmap

### What's planned for future releases?
- 🔜 VS Code extension
- 🔜 Web dashboard (alternative to CLI)
- 🔜 Slack/Discord notifications
- 🔜 Custom health metrics
- 🔜 More AI tool integrations

### When will feature X be released?
Check our [GitHub Projects](https://github.com/iamgagan/llm-session-manager/projects) for roadmap and timelines.

---

## Still have questions?

- 📖 Read the [User Guide](../USER_GUIDE.md)
- 💬 Open a [GitHub Discussion](https://github.com/iamgagan/llm-session-manager/discussions)
- 🐛 Report a [GitHub Issue](https://github.com/iamgagan/llm-session-manager/issues)
- ⭐ Star us on [GitHub](https://github.com/iamgagan/llm-session-manager)
