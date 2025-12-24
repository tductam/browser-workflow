---
name: browser-workflow
description: Execute browser automation tasks (navigate, fill forms, click, login, capture network requests, take screenshots) without loading full MCP tool schemas.
version: 2.0.0
author: Anthropic Agent Skills
---

# Browser Workflow Skill

## ⚠️ CRITICAL: HOW TO EXECUTE (READ THIS FIRST!)

**DO NOT just create JSON steps and show to user. You MUST run the Python script!**

### EXACT Command to Run:

```cmd
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"<ESCAPED_JSON_ARRAY>\"}"
```

### Example - Navigate to YouTube and capture all requests:

```cmd
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{}},{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://youtube.com\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":5000}},{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{\\\"stop\\\":true}}]\"}"
```

### IMPORTANT RULES:
1. **capture_requests must be called TWICE**: First with `{}` to START capturing, then with `{"stop":true}` to GET results
2. **Escape JSON properly**: Use `\\\"` for quotes inside the steps string
3. **Use CMD/PowerShell**: Run via `run_cmd` tool with the exact command above

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

## Common Workflows (COPY-PASTE READY)

### 1. Navigate and Capture ALL Network Requests

```cmd
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{}},{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://youtube.com\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":5000}},{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{\\\"stop\\\":true}}]\"}"
```

### 2. Login to a Website

```cmd
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{}},{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://example.com/login\\\"}},{\\\"action\\\":\\\"wait_for_selector\\\",\\\"params\\\":{\\\"selector\\\":\\\"input[type=email]\\\",\\\"timeout\\\":10000}},{\\\"action\\\":\\\"fill\\\",\\\"params\\\":{\\\"selector\\\":\\\"input[type=email]\\\",\\\"value\\\":\\\"user@example.com\\\"}},{\\\"action\\\":\\\"fill\\\",\\\"params\\\":{\\\"selector\\\":\\\"input[type=password]\\\",\\\"value\\\":\\\"password123\\\"}},{\\\"action\\\":\\\"click\\\",\\\"params\\\":{\\\"selector\\\":\\\"button[type=submit]\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":5000}},{\\\"action\\\":\\\"screenshot\\\",\\\"params\\\":{}},{\\\"action\\\":\\\"capture_requests\\\",\\\"params\\\":{\\\"stop\\\":true}}]\"}"
```

### 3. Take Screenshot of a Page

```cmd
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://example.com\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":2000}},{\\\"action\\\":\\\"screenshot\\\",\\\"params\\\":{\\\"full_page\\\":true}}]\"}"
```

### 4. Google Search

```cmd
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"[{\\\"action\\\":\\\"navigate\\\",\\\"params\\\":{\\\"url\\\":\\\"https://google.com\\\"}},{\\\"action\\\":\\\"fill\\\",\\\"params\\\":{\\\"selector\\\":\\\"textarea[name=q]\\\",\\\"value\\\":\\\"Anthropic Claude\\\"}},{\\\"action\\\":\\\"press\\\",\\\"params\\\":{\\\"key\\\":\\\"Enter\\\"}},{\\\"action\\\":\\\"wait\\\",\\\"params\\\":{\\\"timeout\\\":3000}},{\\\"action\\\":\\\"screenshot\\\",\\\"params\\\":{}}]\"}"
```

---

## Step-by-Step Instructions

### Step 1: Parse User Request → JSON Steps

Convert user's intent to JSON array. **IMPORTANT**: For network capture, ALWAYS use this pattern:
```json
[
  {"action": "capture_requests", "params": {}},           // START capture
  {"action": "navigate", "params": {"url": "..."}},       // Do actions
  {"action": "wait", "params": {"timeout": 5000}},        // Wait for requests
  {"action": "capture_requests", "params": {"stop": true}} // GET results
]
```

### Step 2: Escape JSON for Command Line

Replace `"` with `\\\"` inside the steps string:
- Original: `[{"action":"navigate"}]`
- Escaped: `[{\\\"action\\\":\\\"navigate\\\"}]`

### Step 3: Run the Command

Use your `run_cmd` tool with:
```
python "C:\Users\Tam\.claude\skills\browser-workflow\scripts\run_browser_actions.py" "{\"steps\": \"<ESCAPED_STEPS>\"}"
```

### Step 4: Parse Output

The script returns JSON:
```json
{
  "step_0_capture_requests": {"status": "success", "capturing": true},
  "step_1_navigate": {"status": "success", "url": "https://youtube.com", "title": "YouTube"},
  "step_3_capture_requests": {
    "status": "success",
    "requests": [
      {"url": "https://www.youtube.com/", "method": "GET", "status": 200, "resource_type": "document"},
      {"url": "https://www.youtube.com/s/desktop/...", "method": "GET", "status": 200, "resource_type": "script"}
    ],
    "count": 45,
    "truncated": false
  }
}
```

---

## Selector Guidelines

Use CSS selectors:
- By ID: `#login-button`
- By class: `.submit-btn`
- By attribute: `input[name="email"]`, `button[type="submit"]`
- By type: `input[type="email"]`, `input[type="password"]`
- Combine: `form.login input[type="password"]`

---

## Error Handling

| Error | Solution |
|-------|----------|
| `Selector not found` | Add `wait_for_selector` before action |
| `Timeout` | Increase timeout value or check network |
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