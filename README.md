# Browser Workflow Skill

A lightweight Anthropic Agent Skill for browser automation using Playwright. Execute navigation, form filling, clicking, screenshots, and network request capture without loading full MCP tool schemas.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Basic Usage

```bash
python scripts/run_browser_actions.py '{"steps": "[{\"action\":\"navigate\",\"params\":{\"url\":\"https://example.com\"}},{\"action\":\"screenshot\",\"params\":{}}]"}'
```

## 📋 Supported Actions

| Action | Description | Example |
|--------|-------------|---------|
| `navigate` | Go to URL | `{"action": "navigate", "params": {"url": "https://example.com"}}` |
| `fill` | Fill input field | `{"action": "fill", "params": {"selector": "#email", "value": "test@example.com"}}` |
| `click` | Click element | `{"action": "click", "params": {"selector": "button[type=submit]"}}` |
| `wait` | Wait (ms) | `{"action": "wait", "params": {"timeout": 2000}}` |
| `wait_for_selector` | Wait for element | `{"action": "wait_for_selector", "params": {"selector": ".loaded"}}` |
| `screenshot` | Capture screenshot | `{"action": "screenshot", "params": {"full_page": true}}` |
| `capture_snapshot` | Get page HTML | `{"action": "capture_snapshot", "params": {"max_length": 5000}}` |
| `capture_requests` | Log network requests | `{"action": "capture_requests", "params": {"stop": true}}` |
| `evaluate_js` | Run JavaScript | `{"action": "evaluate_js", "params": {"script": "return document.title"}}` |
| `type` | Type with keyboard | `{"action": "type", "params": {"selector": "#search", "text": "hello"}}` |
| `press` | Press key | `{"action": "press", "params": {"key": "Enter"}}` |
| `scroll` | Scroll page | `{"action": "scroll", "params": {"direction": "down", "amount": 500}}` |
| `hover` | Hover element | `{"action": "hover", "params": {"selector": ".menu"}}` |
| `select` | Select dropdown | `{"action": "select", "params": {"selector": "#country", "value": "US"}}` |

## 📝 Examples

### Capture Network Requests

```json
[
  {"action": "capture_requests", "params": {}},
  {"action": "navigate", "params": {"url": "https://youtube.com"}},
  {"action": "wait", "params": {"timeout": 5000}},
  {"action": "capture_requests", "params": {"stop": true}}
]
```

### Login Flow

```json
[
  {"action": "navigate", "params": {"url": "https://example.com/login"}},
  {"action": "wait_for_selector", "params": {"selector": "input[type=email]"}},
  {"action": "fill", "params": {"selector": "input[type=email]", "value": "user@example.com"}},
  {"action": "fill", "params": {"selector": "input[type=password]", "value": "password123"}},
  {"action": "click", "params": {"selector": "button[type=submit]"}},
  {"action": "wait", "params": {"timeout": 3000}},
  {"action": "screenshot", "params": {}}
]
```

### Google Search

```json
[
  {"action": "navigate", "params": {"url": "https://google.com"}},
  {"action": "fill", "params": {"selector": "textarea[name=q]", "value": "Anthropic Claude"}},
  {"action": "press", "params": {"key": "Enter"}},
  {"action": "wait", "params": {"timeout": 3000}},
  {"action": "screenshot", "params": {}}
]
```

## 📁 Project Structure

```
browser-workflow/
├── SKILL.md                      # Skill definition (for Claude)
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── scripts/
    └── run_browser_actions.py    # Main execution script
```

## ⚙️ Configuration

Default settings in `run_browser_actions.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_SNAPSHOT_LENGTH` | 5000 | Max HTML chars returned |
| `MAX_REQUESTS` | 50 | Max network requests logged |
| `SCREENSHOT_QUALITY` | 70 | JPEG quality (1-100) |
| `DEFAULT_TIMEOUT` | 30000 | Default timeout in ms |

## 🔧 Output Format

```json
{
  "step_0_navigate": {"status": "success", "url": "https://example.com", "title": "Example"},
  "step_1_screenshot": {"status": "success", "screenshot_base64": "iVBORw0...", "format": "jpeg", "size_kb": 45.2}
}
```

## 📄 License

MIT
