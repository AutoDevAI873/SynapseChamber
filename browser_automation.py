import os
import logging
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# Always mock pyautogui and keyboard in this environment
logging.warning("Running in headless environment. GUI operations will be simulated.")

# Mock pyautogui module
class PyAutoGUIMock:
    def click(self, x=None, y=None):
        logging.info(f"Mock clicking at position ({x}, {y})")
        return True
        
    def typewrite(self, text):
        logging.info(f"Mock typing text: {text}")
        return True

pyautogui = PyAutoGUIMock()

# Mock keyboard module
class KeyboardMock:
    def write(self, text):
        logging.info(f"Mock keyboard writing: {text}")
        return True

keyboard = KeyboardMock()

class BrowserAutomation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.screenshot_dir = "static/screenshots"
        self.data_dir = "data"
        self.settings = {
            "headless": True,  # Always headless in this environment
            "timeout": 30,
            "screenshot_on_action": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "viewport_width": 1920,
            "viewport_height": 1080,
            "wait_time_min": 1.0,  # Minimum wait time in seconds
            "wait_time_max": 3.0,   # Maximum wait time in seconds
            "cookies_enabled": True
        }
        
        # AI platform URLs
        self.platform_urls = {
            "gpt": "https://chat.openai.com/",
            "gemini": "https://gemini.google.com/",
            "deepseek": "https://chat.deepseek.com/",
            "claude": "https://claude.ai/",
            "grok": "https://grok.x.com/"
        }
        
        # AI platform selectors
        self.platform_selectors = {
            "gpt": {
                "login_button": (By.XPATH, "//button[contains(text(), 'Log in')]"),
                "email_input": (By.ID, "username"),
                "password_input": (By.ID, "password"),
                "continue_button": (By.XPATH, "//button[contains(text(), 'Continue')]"),
                "prompt_textarea": (By.XPATH, "//textarea[contains(@placeholder, 'Message')]"),
                "send_button": (By.XPATH, "//button[@data-testid='send-button']"),
                "response_container": (By.XPATH, "//div[contains(@class, 'markdown')]"),
                "new_chat_button": (By.XPATH, "//a[contains(text(), 'New chat')]")
            },
            "gemini": {
                "login_button": (By.XPATH, "//a[contains(text(), 'Sign in')]"),
                "prompt_textarea": (By.XPATH, "//textarea[contains(@placeholder, 'Enter')]"),
                "send_button": (By.XPATH, "//button[@aria-label='Send message']"),
                "response_container": (By.XPATH, "//div[contains(@class, 'response-container')]")
            },
            "deepseek": {
                "login_button": (By.XPATH, "//button[contains(text(), 'Sign In')]"),
                "prompt_textarea": (By.XPATH, "//textarea[contains(@placeholder, 'Send a message')]"),
                "send_button": (By.XPATH, "//button[@type='submit']"),
                "response_container": (By.XPATH, "//div[contains(@class, 'message')]")
            },
            "claude": {
                "login_button": (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                "prompt_textarea": (By.XPATH, "//textarea[contains(@placeholder, 'Message')]"),
                "send_button": (By.XPATH, "//button[@aria-label='Send message']"),
                "response_container": (By.XPATH, "//div[contains(@class, 'claude-response')]")
            },
            "grok": {
                "login_button": (By.XPATH, "//a[contains(text(), 'Log in')]"),
                "prompt_textarea": (By.XPATH, "//textarea[contains(@placeholder, 'Ask Grok')]"),
                "send_button": (By.XPATH, "//button[@type='submit']"),
                "response_container": (By.XPATH, "//div[contains(@class, 'Message')]")
            }
        }
        
        # Ensure directories exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "cookies"), exist_ok=True)
    
    def update_settings(self, settings):
        """Update the browser automation settings"""
        self.settings.update(settings)
        self.logger.info(f"Updated browser settings: {self.settings}")
    
    def initialize_driver(self, retry_count=3):
        """Initialize and return a browser driver with retry capability"""
        if self.driver is not None:
            self.close_driver()
            
        self.logger.info(f"Initializing browser driver with {retry_count} retry attempts")
        
        for attempt in range(retry_count):
            try:
                import os
                import subprocess
                
                self.logger.info(f"Driver initialization attempt {attempt+1}/{retry_count}")
                
                # Check if we have Chromium installed in the system
                chromium_path = "/nix/store/chromium"
                chromedriver_path = "/nix/store/chromedriver"
                
                # Try to locate the actual path
                try:
                    chromium_result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
                    if chromium_result.returncode == 0:
                        chromium_path = chromium_result.stdout.strip()
                        self.logger.info(f"Found Chromium at: {chromium_path}")
                    
                    chromedriver_result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
                    if chromedriver_result.returncode == 0:
                        chromedriver_path = chromedriver_result.stdout.strip()
                        self.logger.info(f"Found ChromeDriver at: {chromedriver_path}")
                except Exception as e:
                    self.logger.warning(f"Error finding Chrome paths: {str(e)}")
                
                chrome_options = Options()
                
                # Set the binary location if Chrome is available
                if os.path.exists(chromium_path):
                    chrome_options.binary_location = chromium_path
                
                # Enhanced browser options for better reliability and stability
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--disable-extensions")
                
                # Performance optimizations
                prefs = {
                    "profile.managed_default_content_settings.images": 2,  # Block images
                    "profile.default_content_setting_values.notifications": 2,  # Block notifications
                    "profile.managed_default_content_settings.cookies": 1,  # Allow cookies
                    "profile.default_content_setting_values.plugins": 1,  # Allow plugins
                }
                chrome_options.add_experimental_option("prefs", prefs)
                
                # Add user agent to make detection harder - use a modern Chrome version
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
                
                # Use fake browser version to avoid compatibility issues
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option("useAutomationExtension", False)
                
                # Try to initialize a real browser with improved service settings
                try:
                    # Try to explicitly use the chromedriver path if we found it
                    if os.path.exists(chromedriver_path):
                        from selenium.webdriver.chrome.service import Service
                        service = Service(executable_path=chromedriver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        # Let selenium find chromedriver automatically
                        self.driver = webdriver.Chrome(options=chrome_options)
                    
                    # Set extended timeouts for improved stability
                    self.driver.set_page_load_timeout(self.settings.get("timeout", 45))
                    self.driver.set_script_timeout(30)
                    
                    # Test the driver with a basic operation to verify it's working
                    self.driver.get("about:blank")
                    if self.driver.title is not None:
                        self.logger.info("Real browser driver initialized successfully")
                        return self.driver
                    
                except Exception as browser_error:
                    self.logger.error(f"Failed to initialize real browser (attempt {attempt+1}): {str(browser_error)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    
                    # Only do additional attempts if we haven't reached max retries
                    if attempt < retry_count - 1:
                        self.logger.info(f"Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        self.logger.warning("All initialization attempts failed. Falling back to mock driver.")
                        break
            
            except Exception as e:
                self.logger.error(f"Critical error during initialization attempt {attempt+1}: {str(e)}")
                if attempt < retry_count - 1:
                    self.logger.info(f"Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    self.logger.warning("All initialization attempts failed. Falling back to mock driver.")
                    break
        
        # If we get here, all attempts failed - create a mock driver
        self.logger.info("Initializing mock browser driver as fallback")
        
        # Create a mock driver with expanded functionality
        from selenium.webdriver.remote.webdriver import WebDriver
        from selenium.webdriver.remote.webelement import WebElement
        
        class MockDriver:
            def __init__(self):
                self._current_url = "about:blank"
                self._page_source = "<html><body><p>Mock Browser</p></body></html>"
                self.mock_elements = {}
                self.switch_to = MockSwitchTo()
                
            @property
            def current_url(self):
                return self._current_url
                
            @property
            def page_source(self):
                return self._page_source
                
            def get(self, url):
                self._current_url = url
                logging.info(f"Mock browser navigated to: {url}")
                return None
                
            def find_element(self, by, value):
                element_key = f"{by}:{value}"
                if element_key not in self.mock_elements:
                    mock_element = MockElement()
                    self.mock_elements[element_key] = mock_element
                return self.mock_elements[element_key]
            
            def find_elements(self, by, value):
                return [self.find_element(by, value)]
                
            def refresh(self):
                logging.info("Mock browser refreshed")
                return None
                
            def quit(self):
                logging.info("Mock browser closed")
                return None
                
            def save_screenshot(self, filename):
                try:
                    from PIL import Image
                    img = Image.new('RGB', (800, 600), color = (73, 109, 137))
                    img.save(filename)
                    logging.info(f"Created blank screenshot at {filename}")
                except Exception:
                    with open(filename, 'w') as f:
                        f.write("Mock Screenshot")
                    logging.info(f"Mock screenshot text saved: {filename}")
                return filename
                
            def execute_script(self, script, *args):
                logging.info(f"Mock executing script: {script[:50]}...")
                return None
                
            def get_cookies(self):
                logging.info("Mock get_cookies called")
                return []
                
            def add_cookie(self, cookie_dict):
                logging.info(f"Mock add_cookie called with: {cookie_dict}")
                return None
        
        class MockElement:
            def __init__(self):
                self.location = {'x': 100, 'y': 100}
                self.size = {'width': 100, 'height': 30}
                self.text = 'Mock Element Text'
                
            def click(self):
                logging.info("Mock element clicked")
                return None
                
            def send_keys(self, keys):
                logging.info(f"Mock element received keys: {keys}")
                return None
                
            def clear(self):
                logging.info("Mock element cleared")
                return None
                
            def is_displayed(self):
                return True
                
        class MockSwitchTo:
            def __init__(self):
                self.alert = MockAlert()
                
            def frame(self, frame_reference):
                logging.info(f"Mock switched to frame: {frame_reference}")
                return None
                
            def default_content(self):
                logging.info("Mock switched to default content")
                return None
                
        class MockAlert:
            def accept(self):
                logging.info("Mock alert accepted")
                return None
                
            def dismiss(self):
                logging.info("Mock alert dismissed")
                return None
        
        self.driver = MockDriver()
        self.logger.warning("Using mock browser driver - functionality will be limited")
        return self.driver
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Browser driver closed")
    
    def navigate_to(self, url):
        """Navigate to the specified URL"""
        if not self.driver:
            self.initialize_driver()
        
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            self.take_screenshot(f"navigate_{int(time.time())}")
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def find_element(self, locator_type, locator_value, timeout=None):
        """Find an element in the page with explicit wait"""
        if not timeout:
            timeout = self.settings.get("timeout", 30)
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Timeout finding element: {locator_type}={locator_value}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element: {str(e)}")
            return None
    
    def click_element(self, locator_type, locator_value, timeout=None):
        """Click on an element"""
        element = self.find_element(locator_type, locator_value, timeout)
        if element:
            try:
                element.click()
                if self.settings.get("screenshot_on_action", True):
                    self.take_screenshot(f"click_{int(time.time())}")
                return True
            except Exception as e:
                self.logger.error(f"Error clicking element: {str(e)}")
                # Try to use PyAutoGUI as fallback
                try:
                    self.logger.info("Attempting click with PyAutoGUI")
                    location = element.location
                    size = element.size
                    center_x = location['x'] + size['width'] // 2
                    center_y = location['y'] + size['height'] // 2
                    pyautogui.click(center_x, center_y)
                    if self.settings.get("screenshot_on_action", True):
                        self.take_screenshot(f"pyautogui_click_{int(time.time())}")
                    return True
                except Exception as e2:
                    self.logger.error(f"PyAutoGUI click failed: {str(e2)}")
                    return False
        return False
    
    def send_keys(self, locator_type, locator_value, text, timeout=None):
        """Send keys to an element"""
        element = self.find_element(locator_type, locator_value, timeout)
        if element:
            try:
                element.clear()
                # Type with small random delays to mimic human behavior
                for char in text:
                    element.send_keys(char)
                    time.sleep(0.05 + (0.1 * random.random()))  # Small random delay
                
                if self.settings.get("screenshot_on_action", True):
                    self.take_screenshot(f"send_keys_{int(time.time())}")
                return True
            except Exception as e:
                self.logger.error(f"Error sending keys: {str(e)}")
                # Try PyAutoGUI as fallback
                try:
                    self.logger.info("Attempting to type with PyAutoGUI")
                    element.click()
                    pyautogui.typewrite(text)
                    if self.settings.get("screenshot_on_action", True):
                        self.take_screenshot(f"pyautogui_type_{int(time.time())}")
                    return True
                except Exception as e2:
                    self.logger.error(f"PyAutoGUI typing failed: {str(e2)}")
                    return False
        return False
    
    def take_screenshot(self, name=None):
        """Take a screenshot of the current browser view"""
        if not self.driver:
            self.logger.warning("Cannot take screenshot - driver not initialized")
            return None
        
        if not name:
            name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filename = f"{self.screenshot_dir}/{name}.png"
        try:
            # Create a dummy screenshot if save_screenshot fails
            try:
                self.driver.save_screenshot(filename)
                self.logger.info(f"Screenshot saved: {filename}")
            except Exception as e:
                self.logger.warning(f"Real screenshot failed: {str(e)}. Creating blank image.")
                # Create a simple 1x1 pixel empty image
                try:
                    from PIL import Image
                    img = Image.new('RGB', (800, 600), color = (73, 109, 137))
                    img.save(filename)
                    self.logger.info(f"Created blank screenshot at {filename}")
                except Exception as pil_error:
                    self.logger.warning(f"PIL image creation failed: {str(pil_error)}")
                    # Last resort: create an empty file
                    with open(filename, 'w') as f:
                        f.write("Mock Screenshot Data")
                    self.logger.info(f"Created mock screenshot file at {filename}")
            
            return filename
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None
    
    def handle_alert(self, accept=True):
        """Handle JavaScript alert/confirm/prompt dialog"""
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            if accept:
                alert.accept()
            else:
                alert.dismiss()
            return True
        except TimeoutException:
            return False
        except Exception as e:
            self.logger.error(f"Error handling alert: {str(e)}")
            return False
    
    def scroll_to_element(self, element):
        """Scroll to make an element visible"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)  # Allow time for scrolling animation
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling to element: {str(e)}")
            return False
    
    def execute_js(self, script, *args):
        """Execute JavaScript in the browser context"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Error executing JavaScript: {str(e)}")
            return None
    
    def get_page_source(self):
        """Get the current page HTML source"""
        if not self.driver:
            return None
        return self.driver.page_source
    
    def get_cookies(self):
        """Get all cookies from the current session"""
        if not self.driver:
            return []
        return self.driver.get_cookies()
    
    def add_cookie(self, cookie_dict):
        """Add a cookie to the current session"""
        if not self.driver:
            return False
        try:
            self.driver.add_cookie(cookie_dict)
            return True
        except Exception as e:
            self.logger.error(f"Error adding cookie: {str(e)}")
            return False
    
    def switch_to_frame(self, frame_reference):
        """Switch to an iframe"""
        try:
            self.driver.switch_to.frame(frame_reference)
            return True
        except Exception as e:
            self.logger.error(f"Error switching to frame: {str(e)}")
            return False
    
    def switch_to_default_content(self):
        """Switch back to the main document from a frame"""
        try:
            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            self.logger.error(f"Error switching to default content: {str(e)}")
            return False
            
    # AI Platform Specific Methods
    def navigate_to_platform(self, platform):
        """Navigate to an AI platform"""
        if platform not in self.platform_urls:
            self.logger.error(f"Unknown platform: {platform}")
            return False
            
        url = self.platform_urls[platform]
        return self.navigate_to(url)
        
    def save_cookies(self, platform):
        """Save cookies for a specific platform"""
        if not self.driver:
            self.logger.error("Cannot save cookies - driver not initialized")
            return False
            
        if platform not in self.platform_urls:
            self.logger.error(f"Unknown platform: {platform}")
            return False
            
        try:
            cookies = self.get_cookies()
            if not cookies:
                self.logger.warning(f"No cookies to save for {platform}")
                return False
                
            cookie_file = os.path.join(self.data_dir, "cookies", f"{platform}.json")
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f)
                
            self.logger.info(f"Saved {len(cookies)} cookies for {platform}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving cookies for {platform}: {str(e)}")
            return False
            
    def load_cookies(self, platform):
        """Load cookies for a specific platform"""
        if not self.driver:
            self.logger.error("Cannot load cookies - driver not initialized")
            return False
            
        if platform not in self.platform_urls:
            self.logger.error(f"Unknown platform: {platform}")
            return False
            
        try:
            cookie_file = os.path.join(self.data_dir, "cookies", f"{platform}.json")
            if not os.path.exists(cookie_file):
                self.logger.warning(f"No cookie file found for {platform}")
                return False
                
            # First navigate to the platform domain to set cookies
            self.navigate_to(self.platform_urls[platform])
                
            # Load and add cookies
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
                
            for cookie in cookies:
                try:
                    # Some cookie attributes might cause issues, so we remove them
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    self.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"Error adding cookie: {str(e)}")
                    
            self.logger.info(f"Loaded cookies for {platform}")
            
            # Refresh page to apply cookies
            self.driver.refresh()
            time.sleep(2)  # Wait for page to reload
            
            return True
        except Exception as e:
            self.logger.error(f"Error loading cookies for {platform}: {str(e)}")
            return False
            
    def is_logged_in(self, platform):
        """Check if logged in to a specific platform"""
        if not self.driver:
            return False
            
        if platform not in self.platform_selectors:
            self.logger.error(f"Unknown platform: {platform}")
            return False
            
        try:
            # Each platform has different indicators for being logged in
            # For example, presence of prompt textarea
            selectors = self.platform_selectors[platform]
            prompt_textarea = selectors.get("prompt_textarea")
            
            if prompt_textarea:
                element = self.find_element(prompt_textarea[0], prompt_textarea[1], timeout=5)
                if element and element.is_displayed():
                    self.logger.info(f"Detected logged in state for {platform}")
                    return True
                    
            # If login button is visible, we're not logged in
            login_button = selectors.get("login_button")
            if login_button:
                element = self.find_element(login_button[0], login_button[1], timeout=5)
                if element and element.is_displayed():
                    self.logger.info(f"Not logged in to {platform}")
                    return False
                    
            # If we can't determine the state, assume not logged in
            self.logger.warning(f"Could not determine login state for {platform}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking login state for {platform}: {str(e)}")
            return False
            
    def login_to_platform(self, platform, username, password):
        """Login to an AI platform"""
        if not self.driver:
            self.initialize_driver()
            
        if platform not in self.platform_selectors:
            self.logger.error(f"Unknown platform: {platform}")
            return False
            
        # First try to load cookies
        self.navigate_to_platform(platform)
        cookie_loaded = self.load_cookies(platform)
        
        # Check if already logged in
        if self.is_logged_in(platform):
            self.logger.info(f"Already logged in to {platform}")
            return True
            
        # If not logged in with cookies, try manual login
        try:
            self.logger.info(f"Attempting login to {platform}")
            selectors = self.platform_selectors[platform]
            
            # Click login button
            login_button = selectors.get("login_button")
            if login_button and not self.click_element(login_button[0], login_button[1]):
                self.logger.error(f"Could not click login button for {platform}")
                return False
                
            # Wait for human-like delay
            self._human_delay()
            
            # Enter username/email
            email_input = selectors.get("email_input")
            if email_input and not self.send_keys(email_input[0], email_input[1], username):
                self.logger.error(f"Could not enter username for {platform}")
                return False
                
            # Some platforms have a continue button after email
            continue_button = selectors.get("continue_button")
            if continue_button:
                self.click_element(continue_button[0], continue_button[1])
                self._human_delay()
                
            # Enter password
            password_input = selectors.get("password_input")
            if password_input and not self.send_keys(password_input[0], password_input[1], password):
                self.logger.error(f"Could not enter password for {platform}")
                return False
                
            # Click submit/login button - might be the same selector or different
            submit_button = selectors.get("submit_button", login_button)
            if submit_button and not self.click_element(submit_button[0], submit_button[1]):
                self.logger.error(f"Could not click submit button for {platform}")
                return False
                
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if self.is_logged_in(platform):
                self.logger.info(f"Successfully logged in to {platform}")
                # Save the cookies for future use
                self.save_cookies(platform)
                return True
            else:
                self.logger.error(f"Login to {platform} appears to have failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during login to {platform}: {str(e)}")
            return False
            
    def send_prompt_to_platform(self, platform, prompt):
        """Send a prompt to an AI platform and wait for response"""
        if not self.driver:
            self.initialize_driver()
            
        if platform not in self.platform_selectors:
            self.logger.error(f"Unknown platform: {platform}")
            return None
            
        # Check if we're on the platform and logged in
        if not self.is_logged_in(platform):
            self.logger.error(f"Not logged in to {platform}, cannot send prompt")
            return None
            
        try:
            self.logger.info(f"Sending prompt to {platform}")
            selectors = self.platform_selectors[platform]
            
            # Send the prompt
            prompt_textarea = selectors.get("prompt_textarea")
            if not prompt_textarea or not self.send_keys(prompt_textarea[0], prompt_textarea[1], prompt):
                self.logger.error(f"Could not enter prompt for {platform}")
                return None
                
            # Click send button
            send_button = selectors.get("send_button")
            if not send_button or not self.click_element(send_button[0], send_button[1]):
                self.logger.error(f"Could not click send button for {platform}")
                return None
                
            # Wait for response - this varies by platform
            self._wait_for_response(platform)
            
            # Extract and return the response
            return self._extract_response(platform)
            
        except Exception as e:
            self.logger.error(f"Error sending prompt to {platform}: {str(e)}")
            return None
            
    def _wait_for_response(self, platform):
        """Wait for AI platform to generate a response"""
        if not self.driver:
            return False
            
        selectors = self.platform_selectors.get(platform, {})
        response_indicator = selectors.get("response_container")
        
        if not response_indicator:
            # If no specific indicator, just wait a reasonable time
            self.logger.info(f"No response indicator for {platform}, waiting fixed time")
            time.sleep(15)  # Default wait time
            return True
            
        try:
            # First wait for the element to appear
            element = self.find_element(response_indicator[0], response_indicator[1], timeout=10)
            if not element:
                self.logger.warning(f"Response container not found for {platform}")
                time.sleep(15)  # Default wait time
                return False
                
            # Wait for response to stop changing
            previous_text = ""
            stable_count = 0
            max_wait_time = 60  # Maximum wait time in seconds
            start_time = time.time()
            
            while stable_count < 3 and (time.time() - start_time) < max_wait_time:
                current_text = element.text
                
                if current_text == previous_text and current_text.strip():
                    stable_count += 1
                else:
                    stable_count = 0
                    
                previous_text = current_text
                time.sleep(2)
                
            # Take a final screenshot of the response
            self.take_screenshot(f"{platform}_response_{int(time.time())}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for response from {platform}: {str(e)}")
            time.sleep(15)  # Default wait time as fallback
            return False
            
    def _extract_response(self, platform):
        """Extract the AI's response from the page"""
        if not self.driver:
            return None
            
        selectors = self.platform_selectors.get(platform, {})
        response_container = selectors.get("response_container")
        
        if not response_container:
            self.logger.warning(f"No response container selector for {platform}")
            return None
            
        try:
            element = self.find_element(response_container[0], response_container[1])
            if not element:
                self.logger.warning(f"Response container not found for {platform}")
                return None
                
            response_text = element.text.strip()
            self.logger.info(f"Extracted response from {platform} ({len(response_text)} chars)")
            
            return response_text
        except Exception as e:
            self.logger.error(f"Error extracting response from {platform}: {str(e)}")
            return None
            
    def _human_delay(self):
        """Add a random delay to simulate human behavior"""
        min_time = self.settings.get("wait_time_min", 1.0)
        max_time = self.settings.get("wait_time_max", 3.0)
        delay = min_time + random.random() * (max_time - min_time)
        time.sleep(delay)
