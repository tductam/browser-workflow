---
name: browser-workflow
description: Execute browser automation tasks (navigate, fill forms, click, login, capture network requests, take screenshots).
version: 2.1.0
author: Anthropic Agent Skills
base_dir: ${SKILL_BASE_DIR}
---

# Browser Workflow Skill

## 📁 Path Configuration

**SKILL_BASE_DIR**: The base directory where this skill is installed. When reading this skill, the system provides the base directory. Use this variable in commands:

```
SKILL_BASE_DIR = <base directory provided when skill is loaded>
SCRIPT_PATH = ${SKILL_BASE_DIR}\scripts\run_browser_actions.py
```

**Example**: If skill is loaded from `path\to\file\.claude\skills\browser-workflow`, then:
- `SKILL_BASE_DIR` = `path\to\file\.claude\skills\browser-workflow`
- `SCRIPT_PATH` = `path\to\file\.claude\skills\browser-workflow\scripts\run_browser_actions.py`

---

## ⚠️ CRITICAL: HOW TO EXECUTE

**DO NOT just create JSON steps. You MUST run the Python script!**

### Command Template:

```cmd
python "${SKILL_BASE_DIR}\scripts\run_browser_actions.py" "{\"steps\": \"<ESCAPED_JSON_ARRAY>\"}"
```

### Example - Navigate to YouTube and capture all requests:

```cmd
python "${SKILL_BASE_DIR}\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{}},{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://youtube.com\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":5000}},{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{\\\"stop\\\":true}}]\"}"
```

### IMPORTANT RULES:
1. Replace `${SKILL_BASE_DIR}` with the actual base directory path provided when skill is loaded
2. **capture_requests must be called TWICE**: First with `{}` to START, then with `{"stop":true}` to GET results
3. **Escape JSON properly**: Use `\\\"` for quotes inside the steps string

---

## Quick Reference

**Supported Actions:**
| Action | Description | Required Params |
|--------|-------------|-----------------|
| `navigate` | Go to URL | `url` |
| `fill` | Fill input field | `selector`, `value` |
| `click` | Click element | `selector` |
| `hover` | Hover over element | `selector` |
| `scroll` | Scroll page | `direction` (up/down), `amount` (pixels) |
| `wait` | Wait fixed time | `timeout` (ms, default 2000) |
| `wait_for_selector` | Wait for element | `selector`, `timeout` (ms, optional) |
| `screenshot` | Capture screenshot | `full_page` (bool, optional) |
| `capture_snapshot` | Get page HTML | `max_length` (optional, default 5000) |
| `capture_requests` | Log network requests | `filter` (optional), `stop` (bool to get results) |
| `evaluate_js` | Run JavaScript | `script` |
| `type` | Type with keyboard | `selector`, `text`, `delay` (ms, optional) |
| `select` | Select dropdown option | `selector`, `value` |
| `press` | Press keyboard key | `key` (e.g., "Enter", "Tab") |

---

## Common Workflows

### 1. Navigate and Capture ALL Network Requests

**Steps JSON:**
```json
[
  {"action": "capture_requests", "params": {}},
  {"action": "navigate", "params": {"url": "https://youtube.com"}},
  {"action": "wait", "params": {"timeout": 5000}},
  {"action": "capture_requests", "params": {"stop": true}}
]
```

**Command:**
```cmd
python "${SKILL_BASE_DIR}\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{}},{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://youtube.com\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":5000}},{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{\\\"stop\\\":true}}]\"}"
```

### 2. Login to a Website

**Steps JSON:**
```json
[
  {"action": "capture_requests", "params": {}},
  {"action": "navigate", "params": {"url": "https://example.com/login"}},
  {"action": "wait_for_selector", "params": {"selector": "input[type=email]", "timeout": 10000}},
  {"action": "fill", "params": {"selector": "input[type=email]", "value": "EMAIL_HERE"}},
  {"action": "fill", "params": {"selector": "input[type=password]", "value": "PASSWORD_HERE"}},
  {"action": "click", "params": {"selector": "button[type=submit]"}},
  {"action": "wait", "params": {"timeout": 5000}},
  {"action": "screenshot", "params": {}},
  {"action": "capture_requests", "params": {"stop": true}}
]
```

### 3. Take Screenshot of a Page

**Steps JSON:**
```json
[
  {"action": "navigate", "params": {"url": "https://example.com"}},
  {"action": "wait", "params": {"timeout": 2000}},
  {"action": "screenshot", "params": {"full_page": true}}
]
```

### 4. Google Search

**Steps JSON:**
```json
[
  {"action": "navigate", "params": {"url": "https://google.com"}},
  {"action": "fill", "params": {"selector": "textarea[name=q]", "value": "SEARCH_QUERY"}},
  {"action": "press", "params": {"key": "Enter"}},
  {"action": "wait", "params": {"timeout": 3000}},
  {"action": "screenshot", "params": {}}
]
```

---

## Step-by-Step Instructions

### Step 1: Get SKILL_BASE_DIR

When you read this skill using `openskills read browser-workflow`, the output includes:
```
Base directory: path\to\file\.claude\skills\browser-workflow
```

Use this path as `SKILL_BASE_DIR`.

### Step 2: Parse User Request → JSON Steps

Convert user's intent to JSON array. For network capture, use this pattern:
```json
[
  {"action": "capture_requests", "params": {}},           // START capture
  {"action": "navigate", "params": {"url": "..."}},       // Do actions
  {"action": "wait", "params": {"timeout": 5000}},        // Wait for requests
  {"action": "capture_requests", "params": {"stop": true}} // GET results
]
```

### Step 3: Build Command

Replace placeholders:
1. `${SKILL_BASE_DIR}` → actual path from Step 1
2. `<ESCAPED_JSON_ARRAY>` → JSON with quotes escaped as `\\\"`

### Step 4: Run Command

Use `run_cmd` tool:
```cmd
python "path\to\file\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"[...]\"}"
```

### Step 5: Parse Output

```json
{
  "step_0_capture_requests": {"status": "success", "capturing": true},
  "step_1_navigate": {"status": "success", "url": "...", "title": "..."},
  "step_3_capture_requests": {"status": "success", "requests": [...], "count": 45}
}
```

---

## Selector Guidelines

| Type | Syntax | Example |
|------|--------|---------|
| By ID | `#id` | `#login-button` |
| By class | `.class` | `.submit-btn` |
| By attribute | `[attr=value]` | `input[name="email"]` |
| By type | `[type=value]` | `input[type="password"]` |
| Combined | `parent child` | `form.login input[type="email"]` |

---

## Error Handling

| Error | Solution |
|-------|----------|
| `Selector not found` | Add `wait_for_selector` before action |
| `Timeout` | Increase timeout value |
| `Navigation failed` | Verify URL is correct |

---

## Mapping from MCP Browser Tools

| MCP Tool | Browser Workflow Action |
|----------|------------------------|
| `browser_navigate` | `navigate` |
| `browser_click` | `click` |
| `browser_fill` | `fill` |
| `browser_take_snapshot` | `capture_snapshot` |
| `browser_list_network_requests` | `capture_requests` with `{"stop": true}` |
| `browser_screenshot` | `screenshot` |