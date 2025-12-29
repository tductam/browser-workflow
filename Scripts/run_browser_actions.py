#!/usr/bin/env python3
"""
Browser Workflow Action Executor
Executes a sequence of browser automation actions using Playwright.
Optimized for Claude's code execution environment with minimal token output.
"""

import sys
import os
import json
import base64
import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

# Fix Windows Unicode encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


# Configuration
MAX_SNAPSHOT_LENGTH = 5000
MAX_REQUESTS = 50
MAX_JS_RESULT_LENGTH = 2000
SCREENSHOT_QUALITY = 70  # JPEG quality for smaller base64
DEFAULT_TIMEOUT = 30000  # 30 seconds


class BrowserWorkflow:
    def __init__(self):
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.captured_requests: List[Dict] = []
        self.capturing_requests = False
        
    def _setup_request_capture(self):
        """Setup network request interception."""
        def on_request(request):
            if self.capturing_requests and len(self.captured_requests) < MAX_REQUESTS:
                self.captured_requests.append({
                    'url': request.url[:200],  # Truncate long URLs
                    'method': request.method,
                    'resource_type': request.resource_type
                })
        
        def on_response(response):
            if self.capturing_requests:
                # Update the corresponding request with response info
                for req in self.captured_requests:
                    if req['url'] == response.url[:200]:
                        req['status'] = response.status
                        break
        
        self.page.on('request', on_request)
        self.page.on('response', on_response)
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single browser action and return result."""
        try:
            result = self._dispatch_action(action, params)
            return {'status': 'success', **result} if result else {'status': 'success'}
        except PlaywrightTimeout as e:
            return {
                'status': 'error',
                'error_type': 'TimeoutError',
                'message': f"Timeout waiting for: {params.get('selector', 'unknown')}. Try increasing timeout or check selector.",
                'suggestion': 'Use wait_for_selector before this action, or verify the selector exists on the page.'
            }
        except Exception as e:
            error_msg = str(e)
            suggestion = self._get_error_suggestion(error_msg, action, params)
            return {
                'status': 'error',
                'error_type': type(e).__name__,
                'message': error_msg[:500],  # Truncate long error messages
                'suggestion': suggestion
            }
    
    def _dispatch_action(self, action: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route action to appropriate handler."""
        handlers = {
            'navigate': self._navigate,
            'fill': self._fill,
            'type': self._type,
            'click': self._click,
            'hover': self._hover,
            'scroll': self._scroll,
            'wait': self._wait,
            'wait_for_selector': self._wait_for_selector,
            'screenshot': self._screenshot,
            'capture_snapshot': self._capture_snapshot,
            'capture_requests': self._capture_requests,
            'evaluate_js': self._evaluate_js,
            'select': self._select,
            'press': self._press,
            'focus': self._focus,
            'clear': self._clear,
            'check': self._check,
            'uncheck': self._uncheck,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: '{action}'. Supported: {list(handlers.keys())}")
        
        return handler(params)
    
    def _navigate(self, params: Dict) -> Optional[Dict]:
        url = params.get('url')
        if not url:
            raise ValueError("'url' parameter is required for navigate action")
        
        wait_until = params.get('wait_until', 'domcontentloaded')
        timeout = params.get('timeout', DEFAULT_TIMEOUT)
        
        self.page.goto(url, wait_until=wait_until, timeout=timeout)
        return {'url': self.page.url, 'title': self.page.title()}
    
    def _fill(self, params: Dict) -> None:
        selector = params.get('selector')
        value = params.get('value', '')
        if not selector:
            raise ValueError("'selector' parameter is required for fill action")
        
        self.page.fill(selector, value, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _type(self, params: Dict) -> None:
        """Type text with keyboard (slower but more realistic)."""
        selector = params.get('selector')
        text = params.get('text', '')
        delay = params.get('delay', 50)  # ms between keystrokes
        
        if not selector:
            raise ValueError("'selector' parameter is required for type action")
        
        self.page.type(selector, text, delay=delay, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _click(self, params: Dict) -> None:
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for click action")
        
        button = params.get('button', 'left')
        click_count = params.get('click_count', 1)
        self.page.click(selector, button=button, click_count=click_count, 
                       timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _hover(self, params: Dict) -> None:
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for hover action")
        
        self.page.hover(selector, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _scroll(self, params: Dict) -> Dict:
        direction = params.get('direction', 'down')
        amount = params.get('amount', 500)
        
        if direction == 'down':
            self.page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == 'up':
            self.page.evaluate(f"window.scrollBy(0, -{amount})")
        elif direction == 'bottom':
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        elif direction == 'top':
            self.page.evaluate("window.scrollTo(0, 0)")
        
        scroll_y = self.page.evaluate("window.scrollY")
        return {'scroll_position': scroll_y}
    
    def _wait(self, params: Dict) -> None:
        timeout = params.get('timeout', 2000)
        self.page.wait_for_timeout(timeout)
    
    def _wait_for_selector(self, params: Dict) -> Dict:
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for wait_for_selector action")
        
        timeout = params.get('timeout', DEFAULT_TIMEOUT)
        state = params.get('state', 'visible')  # visible, hidden, attached, detached
        
        self.page.wait_for_selector(selector, timeout=timeout, state=state)
        return {'found': True, 'selector': selector}
    
    def _screenshot(self, params: Dict) -> Dict:
        """Capture screenshot and return as base64."""
        full_page = params.get('full_page', False)
        
        screenshot_bytes = self.page.screenshot(
            full_page=full_page,
            type='jpeg',
            quality=SCREENSHOT_QUALITY
        )
        
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return {
            'screenshot_base64': screenshot_b64,
            'format': 'jpeg',
            'size_kb': round(len(screenshot_bytes) / 1024, 1)
        }
    
    def _capture_snapshot(self, params: Dict) -> Dict:
        """Capture page HTML content, truncated."""
        max_length = params.get('max_length', MAX_SNAPSHOT_LENGTH)
        
        content = self.page.content()
        
        # Clean up HTML for readability (remove scripts, styles, comments)
        if params.get('clean', True):
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            content = re.sub(r'\s+', ' ', content)  # Collapse whitespace
        
        truncated = len(content) > max_length
        content = content[:max_length]
        
        return {
            'html': content,
            'truncated': truncated,
            'original_length': len(self.page.content()),
            'title': self.page.title(),
            'url': self.page.url
        }
    
    def _capture_requests(self, params: Dict) -> Dict:
        """Start/stop capturing network requests or return captured requests."""
        if params.get('stop', False):
            self.capturing_requests = False
            requests = self.captured_requests.copy()
            
            # Filter if pattern provided
            filter_pattern = params.get('filter', '')
            if filter_pattern:
                requests = [r for r in requests if filter_pattern in r.get('url', '')]
            
            return {
                'requests': requests[:MAX_REQUESTS],
                'count': len(requests),
                'truncated': len(requests) > MAX_REQUESTS
            }
        else:
            # Start capturing
            self.capturing_requests = True
            self.captured_requests = []
            return {'capturing': True}
    
    def _evaluate_js(self, params: Dict) -> Dict:
        """Execute JavaScript and return result."""
        script = params.get('script')
        if not script:
            raise ValueError("'script' parameter is required for evaluate_js action")
        
        result = self.page.evaluate(script)
        
        # Serialize and truncate result
        result_str = json.dumps(result) if result is not None else 'null'
        truncated = len(result_str) > MAX_JS_RESULT_LENGTH
        
        return {
            'result': result_str[:MAX_JS_RESULT_LENGTH] if truncated else result_str,
            'truncated': truncated
        }
    
    def _select(self, params: Dict) -> None:
        """Select dropdown option."""
        selector = params.get('selector')
        value = params.get('value')
        
        if not selector or value is None:
            raise ValueError("'selector' and 'value' parameters are required for select action")
        
        self.page.select_option(selector, value, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _press(self, params: Dict) -> None:
        """Press keyboard key."""
        key = params.get('key')
        if not key:
            raise ValueError("'key' parameter is required for press action")
        
        selector = params.get('selector')
        if selector:
            self.page.press(selector, key, timeout=params.get('timeout', DEFAULT_TIMEOUT))
        else:
            self.page.keyboard.press(key)
    
    def _focus(self, params: Dict) -> None:
        """Focus on element."""
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for focus action")
        
        self.page.focus(selector, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _clear(self, params: Dict) -> None:
        """Clear input field."""
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for clear action")
        
        self.page.fill(selector, '', timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _check(self, params: Dict) -> None:
        """Check checkbox."""
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for check action")
        
        self.page.check(selector, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _uncheck(self, params: Dict) -> None:
        """Uncheck checkbox."""
        selector = params.get('selector')
        if not selector:
            raise ValueError("'selector' parameter is required for uncheck action")
        
        self.page.uncheck(selector, timeout=params.get('timeout', DEFAULT_TIMEOUT))
    
    def _get_error_suggestion(self, error_msg: str, action: str, params: Dict) -> str:
        """Provide helpful suggestions based on error type."""
        error_lower = error_msg.lower()
        
        if 'selector' in error_lower or 'not found' in error_lower:
            return f"Selector '{params.get('selector', '')}' not found. Try: 1) Use capture_snapshot to inspect page structure, 2) Wait for page to load with wait_for_selector, 3) Check if element is inside an iframe."
        
        if 'timeout' in error_lower:
            return "Operation timed out. Try increasing timeout parameter or check if the page loaded correctly."
        
        if 'navigation' in error_lower:
            return "Navigation failed. Verify the URL is correct and accessible."
        
        if 'detached' in error_lower:
            return "Element was removed from page. The page might have reloaded or content changed dynamically."
        
        return "Check action parameters and ensure the page state is correct before this action."
    
    def run(self, steps: List[Dict]) -> Dict[str, Any]:
        """Execute all steps and return results."""
        results = {}
        
        with sync_playwright() as pw:
            # Launch browser in headless mode (required for code execution environment)
            self.browser = pw.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']  # For containerized environments
            )
            
            # Create page with reasonable viewport
            self.page = self.browser.new_page(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Setup request capture listener
            self._setup_request_capture()
            
            # Execute each step
            for i, step in enumerate(steps):
                action = step.get('action', '')
                params = step.get('params', {})
                
                result = self.execute_action(action, params)
                results[f'step_{i}_{action}'] = result
                
                # Stop execution on critical errors (optional, can be configured)
                if result.get('status') == 'error' and params.get('stop_on_error', False):
                    break
            
            # Cleanup
            self.browser.close()
        
        return results


def main():
    """Main entry point for script execution."""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'No input provided',
            'usage': 'python run_browser_actions.py \'{"steps": "[...]"}\' OR \'{"steps_file": "path/to/steps.json"}\''
        }))
        sys.exit(1)
    
    try:
        # Parse input
        input_json = json.loads(sys.argv[1])
        
        # Support reading steps from file
        steps_file = input_json.get('steps_file')
        if steps_file:
            with open(steps_file, 'r', encoding='utf-8') as f:
                steps = json.load(f)
        else:
            steps_str = input_json.get('steps', '[]')
            
            # Handle both string and list input for steps
            if isinstance(steps_str, str):
                steps = json.loads(steps_str)
            else:
                steps = steps_str
        
        if not isinstance(steps, list):
            raise ValueError("'steps' must be a JSON array")
        
        if len(steps) == 0:
            raise ValueError("'steps' array cannot be empty")
        
        # Execute workflow
        workflow = BrowserWorkflow()
        results = workflow.run(steps)
        
        # Output results
        # Use ensure_ascii=True to avoid encoding issues on Windows console
        print(json.dumps(results, ensure_ascii=True))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            'error': 'Invalid JSON input',
            'message': str(e),
            'suggestion': 'Ensure the input is valid JSON format. Check for proper escaping of quotes.'
        }))
        sys.exit(1)
    except FileNotFoundError as e:
        print(json.dumps({
            'error': 'Steps file not found',
            'message': str(e),
            'suggestion': 'Check that the file path is correct'
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            'error': 'Execution failed',
            'error_type': type(e).__name__,
            'message': str(e)[:500]
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()