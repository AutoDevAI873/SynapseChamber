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
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "viewport_width": 1920,
            "viewport_height": 1080,
            "wait_time_min": 1.0,  # Minimum wait time in seconds
            "wait_time_max": 3.0,  # Maximum wait time in seconds
        }
        
        # URLs for AI platforms
        self.platform_urls = {
            "chatgpt": "https://chat.openai.com/",
            "claude": "https://claude.ai/",
            "gemini": "https://gemini.google.com/app",
            "grok": "https://grok.x.ai/",
            "deepseek": "https://chat.deepseek.com/"
        }
        
        # Platform-specific selectors for common elements
        self.platform_selectors = {
            "chatgpt": {
                "login_button": (By.XPATH, "//button[contains(text(), 'Log in')]"),
                "new_chat": (By.XPATH, "//a[contains(text(), 'New chat')]"),
                "chat_input": (By.XPATH, "//textarea[@id='prompt-textarea']"),
                "response_loading": (By.XPATH, "//div[contains(@class, 'result-streaming')]"),
                "response_content": (By.XPATH, "//div[contains(@class, 'markdown')]"),
                "username_field": (By.ID, "username"),
                "password_field": (By.ID, "password"),
                "logged_in_check": (By.XPATH, "//img[contains(@alt, 'User')]")
            },
            "claude": {
                "login_button": (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                "new_chat": (By.XPATH, "//button[contains(text(), 'New chat')]"),
                "chat_input": (By.XPATH, "//div[@role='textbox']"),
                "response_loading": (By.XPATH, "//div[contains(@class, 'streaming')]"),
                "response_content": (By.XPATH, "//div[contains(@class, 'prose')]"),
                "email_field": (By.ID, "email"),
                "password_field": (By.ID, "password"),
                "logged_in_check": (By.XPATH, "//button[contains(@aria-label, 'User menu')]")
            },
            "gemini": {
                "login_button": (By.XPATH, "//a[contains(text(), 'Sign in')]"),
                "new_chat": (By.XPATH, "//div[contains(text(), 'New chat')]"),
                "chat_input": (By.XPATH, "//textarea[@aria-label='Input box']"),
                "response_loading": (By.XPATH, "//div[contains(@aria-label, 'Loading response')]"),
                "response_content": (By.XPATH, "//div[contains(@aria-label, 'Gemini')]"),
                "email_field": (By.ID, "identifierId"),
                "password_field": (By.XPATH, "//input[@type='password']"),
                "logged_in_check": (By.XPATH, "//img[contains(@alt, 'profile')]")
            },
            "grok": {
                "login_button": (By.XPATH, "//a[contains(@href, 'login')]"),
                "new_chat": (By.XPATH, "//button[contains(text(), 'New Chat')]"),
                "chat_input": (By.XPATH, "//textarea"),
                "response_loading": (By.XPATH, "//div[contains(@class, 'typing-indicator')]"),
                "response_content": (By.XPATH, "//div[contains(@class, 'message-content')]"),
                "username_field": (By.ID, "username"),
                "password_field": (By.ID, "password"),
                "logged_in_check": (By.XPATH, "//div[contains(@class, 'user-profile')]")
            },
            "deepseek": {
                "login_button": (By.XPATH, "//button[contains(text(), 'Sign In')]"),
                "new_chat": (By.XPATH, "//button[contains(text(), 'New Chat')]"),
                "chat_input": (By.XPATH, "//textarea"),
                "response_loading": (By.XPATH, "//div[contains(@class, 'loading')]"),
                "response_content": (By.XPATH, "//div[contains(@class, 'message-content')]"),
                "email_field": (By.ID, "email"),
                "password_field": (By.ID, "password"),
                "logged_in_check": (By.XPATH, "//div[contains(@class, 'avatar')]")
            }
        }
        
        # Create necessary directories
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "cookies"), exist_ok=True)
        
        # Set up logging
        self.logger.setLevel(logging.INFO)
        
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
                chrome_options.add_argument(f"--user-agent={self.settings['user_agent']}")
                
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
        class MockDriver:
            def __init__(self):
                self._current_url = "about:blank"
                self._page_source = "<html><body><p>Mock Browser</p></body></html>"
                self._title = "Mock Browser"
                self.mock_elements = {}
                self.switch_to = MockSwitchTo()
                self.logger = logging.getLogger("MockDriver")
                
            @property
            def current_url(self):
                return self._current_url
                
            @property
            def page_source(self):
                return self._page_source
                
            @property
            def title(self):
                return self._title
                
            def get(self, url):
                self._current_url = url
                self.logger.info(f"Mock browser navigated to: {url}")
                # Generate dynamic response for AI platform URLs
                for platform, platform_url in self.platform_urls.items():
                    if platform_url in url:
                        self._page_source = f"<html><body><h1>Mock {platform.capitalize()} Platform</h1><p>This is a simulated page for {platform}</p></body></html>"
                        self._title = f"{platform.capitalize()} - Mock Browser"
                return None
                
            def find_element(self, by, value):
                element_key = f"{by}:{value}"
                self.logger.info(f"Mock finding element: {by}={value}")
                if element_key not in self.mock_elements:
                    mock_element = MockElement()
                    self.mock_elements[element_key] = mock_element
                return self.mock_elements[element_key]
            
            def find_elements(self, by, value):
                return [self.find_element(by, value)]
                
            def refresh(self):
                self.logger.info("Mock browser refreshed")
                return None
                
            def quit(self):
                self.logger.info("Mock browser closed")
                return None
                
            def set_page_load_timeout(self, timeout):
                self.logger.info(f"Mock set page load timeout: {timeout}s")
                
            def set_script_timeout(self, timeout):
                self.logger.info(f"Mock set script timeout: {timeout}s")
                
            def save_screenshot(self, filename):
                try:
                    from PIL import Image
                    img = Image.new('RGB', (800, 600), color = (73, 109, 137))
                    img.save(filename)
                    self.logger.info(f"Created blank screenshot at {filename}")
                except Exception:
                    with open(filename, 'w') as f:
                        f.write("Mock Screenshot")
                    self.logger.info(f"Mock screenshot text saved: {filename}")
                return filename
                
            def execute_script(self, script, *args):
                self.logger.info(f"Mock executing script: {script[:50]}...")
                # Return different mocked results based on script
                if "return document.title" in script:
                    return self._title
                elif "return window.location.href" in script:
                    return self._current_url
                return None
                
            def get_cookies(self):
                self.logger.info("Mock get_cookies called")
                return []
                
            def add_cookie(self, cookie_dict):
                self.logger.info(f"Mock add_cookie called with: {cookie_dict}")
                return None
        
        class MockElement:
            def __init__(self):
                self.location = {'x': 100, 'y': 100}
                self.size = {'width': 100, 'height': 30}
                self.text = 'Mock Element Text'
                self.is_enabled_status = True
                self.logger = logging.getLogger("MockElement")
                
            def click(self):
                self.logger.info("Mock element clicked")
                return None
                
            def send_keys(self, keys):
                self.logger.info(f"Mock element received keys: {keys}")
                return None
                
            def clear(self):
                self.logger.info("Mock element cleared")
                return None
                
            def is_displayed(self):
                return True
                
            def is_enabled(self):
                return self.is_enabled_status
                
            def get_attribute(self, name):
                self.logger.info(f"Mock get_attribute called: {name}")
                if name == "href":
                    return "https://example.com"
                elif name == "class":
                    return "mock-class"
                return None
                
        class MockSwitchTo:
            def __init__(self):
                self.alert = MockAlert()
                self.logger = logging.getLogger("MockSwitchTo")
                
            def frame(self, frame_reference):
                self.logger.info(f"Mock switched to frame: {frame_reference}")
                return None
                
            def default_content(self):
                self.logger.info("Mock switched to default content")
                return None
                
        class MockAlert:
            def __init__(self):
                self.text = "Mock Alert Text"
                self.logger = logging.getLogger("MockAlert")
                
            def accept(self):
                self.logger.info("Mock alert accepted")
                return None
                
            def dismiss(self):
                self.logger.info("Mock alert dismissed")
                return None
                
            def send_keys(self, keys):
                self.logger.info(f"Mock alert received keys: {keys}")
                return None
                
        # Initialize mock driver with improved mock functionality
        mock_driver = MockDriver()
        mock_driver.platform_urls = self.platform_urls  # Share platform URLs with mock
        self.driver = mock_driver
        self.logger.warning("Using mock browser driver - functionality will be limited")
        return self.driver
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error closing driver: {str(e)}")
            finally:
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
        
        if not self.driver:
            self.logger.error("Driver not initialized, cannot find element")
            return None
            
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
        if not self.driver:
            self.logger.warning("Cannot handle alert - driver not initialized")
            return False
            
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
        if not self.driver or not element:
            self.logger.warning("Cannot scroll - driver not initialized or element is None")
            return False
            
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)  # Allow time for scrolling animation
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling to element: {str(e)}")
            return False
    
    def execute_js(self, script, *args):
        """Execute JavaScript in the browser context"""
        if not self.driver:
            self.logger.warning("Cannot execute JavaScript - driver not initialized")
            return None
            
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
        try:
            return self.driver.get_cookies()
        except Exception as e:
            self.logger.error(f"Error getting cookies: {str(e)}")
            return []
    
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
        if not self.driver:
            self.logger.warning("Cannot switch to frame - driver not initialized")
            return False
            
        try:
            self.driver.switch_to.frame(frame_reference)
            return True
        except Exception as e:
            self.logger.error(f"Error switching to frame: {str(e)}")
            return False
    
    def switch_to_default_content(self):
        """Switch back to the main document from a frame"""
        if not self.driver:
            self.logger.warning("Cannot switch to default content - driver not initialized")
            return False
            
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
            # First navigate to platform if not already there
            current_url = self.driver.current_url
            platform_url = self.platform_urls[platform]
            
            if platform_url not in current_url:
                self.navigate_to(platform_url)
                time.sleep(2)  # Give time to load
                
            # Check for logged in indicator
            logged_in_check = self.platform_selectors[platform]["logged_in_check"]
            element = None
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(logged_in_check)
                )
            except:
                # If we don't see the logged in element, let's check if login button is present
                login_button = self.platform_selectors[platform]["login_button"]
                try:
                    login_elem = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located(login_button)
                    )
                    # If we found the login button, we're not logged in
                    self.logger.info(f"Login button found for {platform}, not logged in")
                    return False
                except:
                    # If neither element found, let's assume the site is having issues
                    self.logger.warning(f"Neither logged in nor login elements found for {platform}")
                    # Check if we've got a mostly empty page or error page
                    page_source = self.driver.page_source.lower()
                    if "error" in page_source or "404" in page_source or "not found" in page_source:
                        self.logger.warning(f"Error page detected for {platform}")
                        return False
                    
            if element:
                self.logger.info(f"Logged in to {platform}")
                return True
            else:
                self.logger.info(f"Not logged in to {platform}")
                return False
        except Exception as e:
            self.logger.error(f"Error checking login for {platform}: {str(e)}")
            return False
            
    def login_to_platform(self, platform, username, password):
        """Login to an AI platform"""
        if not self.driver:
            self.initialize_driver()
            
        if platform not in self.platform_selectors:
            self.logger.error(f"Unknown platform: {platform}")
            return False
            
        try:
            # First check if already logged in
            if self.is_logged_in(platform):
                self.logger.info(f"Already logged in to {platform}")
                return True
                
            # Navigate to platform
            self.navigate_to(self.platform_urls[platform])
            
            # Click login button
            self.click_element(*self.platform_selectors[platform]["login_button"])
            time.sleep(2)  # Wait for login form
            
            # Platform-specific login process
            if platform == "chatgpt" or platform == "grok":
                # Enter username/email
                self.send_keys(*self.platform_selectors[platform]["username_field"], username)
                # Submit username (usually a button or enter key)
                self.click_element(By.XPATH, "//button[@type='submit']")
                time.sleep(1)
                # Enter password
                self.send_keys(*self.platform_selectors[platform]["password_field"], password)
                # Submit password
                self.click_element(By.XPATH, "//button[@type='submit']")
            elif platform == "claude" or platform == "deepseek":
                # Enter email/username
                self.send_keys(*self.platform_selectors[platform]["email_field"], username)
                # Enter password
                self.send_keys(*self.platform_selectors[platform]["password_field"], password)
                # Submit form
                self.click_element(By.XPATH, "//button[@type='submit']")
            elif platform == "gemini":
                # Enter email/username
                self.send_keys(*self.platform_selectors[platform]["email_field"], username)
                # Submit email
                self.click_element(By.XPATH, "//button[contains(text(), 'Next')]")
                time.sleep(2)
                # Enter password
                self.send_keys(*self.platform_selectors[platform]["password_field"], password)
                # Submit password
                self.click_element(By.XPATH, "//button[contains(text(), 'Next')]")
                
            # Wait for login process to complete
            time.sleep(5)
            
            # Save cookies for future sessions
            self.save_cookies(platform)
            
            # Verify login
            if self.is_logged_in(platform):
                self.logger.info(f"Successfully logged in to {platform}")
                return True
            else:
                self.logger.warning(f"Login to {platform} may have failed")
                return False
        except Exception as e:
            self.logger.error(f"Error logging in to {platform}: {str(e)}")
            return False
            
    def send_prompt_to_platform(self, platform, prompt):
        """Send a prompt to an AI platform and wait for response"""
        if not self.driver:
            self.initialize_driver()
            
        if platform not in self.platform_selectors:
            self.logger.error(f"Unknown platform: {platform}")
            return None
            
        try:
            # Navigate to platform if not already there
            current_url = self.driver.current_url
            platform_url = self.platform_urls[platform]
            
            if platform_url not in current_url:
                self.navigate_to(platform_url)
                
            # Check if logged in
            if not self.is_logged_in(platform):
                self.logger.error(f"Not logged in to {platform}")
                return None
                
            # For some platforms, click new chat if available
            try:
                self.click_element(*self.platform_selectors[platform]["new_chat"])
                time.sleep(2)  # Wait for new chat to initialize
            except:
                self.logger.info(f"No new chat button found for {platform} or already in chat")
                
            # Enter prompt in chat input
            chat_input_success = self.send_keys(*self.platform_selectors[platform]["chat_input"], prompt)
            
            if not chat_input_success:
                self.logger.error(f"Failed to enter prompt for {platform}")
                return None
                
            # Submit prompt - platform specific
            if platform == "chatgpt":
                # ChatGPT uses the Enter key or a send button
                self.click_element(By.XPATH, "//button[contains(@class, 'send')]")
            elif platform == "claude":
                # Claude usually has a send button
                self.click_element(By.XPATH, "//button[contains(@aria-label, 'Send')]")
            elif platform == "gemini":
                # Gemini has a send button
                self.click_element(By.XPATH, "//button[contains(@aria-label, 'Send')]")
            elif platform == "grok":
                # Grok usually has a send icon
                self.click_element(By.XPATH, "//button[contains(@aria-label, 'Send message')]")
            elif platform == "deepseek":
                # DeepSeek has a send button
                self.click_element(By.XPATH, "//button[contains(@aria-label, 'Send message')]")
                
            # Wait for response
            response_text = self._wait_for_response(platform)
            
            # Take screenshot of the response
            self.take_screenshot(f"{platform}_response_{int(time.time())}")
            
            return response_text
        except Exception as e:
            self.logger.error(f"Error sending prompt to {platform}: {str(e)}")
            return None
            
    def _wait_for_response(self, platform):
        """Wait for AI platform to generate a response"""
        if not self.driver or platform not in self.platform_selectors:
            return None
            
        try:
            # First wait for loading indicator to appear
            loading_selector = self.platform_selectors[platform]["response_loading"]
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(loading_selector)
                )
                self.logger.info(f"Response generation started for {platform}")
            except TimeoutException:
                self.logger.warning(f"No loading indicator appeared for {platform}")
                # Some platforms may not show loading indicator or it appeared and disappeared quickly
                pass
                
            # Then wait for it to disappear (response complete)
            max_wait_time = 120  # Max 2 minutes for response
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    loading_present = len(self.driver.find_elements(*loading_selector)) > 0
                    if not loading_present:
                        # Give a small delay to ensure response is fully rendered
                        time.sleep(1)
                        break
                except:
                    # If we can't find loading element, assume it's done
                    break
                    
                time.sleep(1)
                
            # Extract response
            return self._extract_response(platform)
        except Exception as e:
            self.logger.error(f"Error waiting for response from {platform}: {str(e)}")
            return None
            
    def _extract_response(self, platform):
        """Extract the AI's response from the page"""
        if not self.driver or platform not in self.platform_selectors:
            return None
            
        try:
            # Get the response content based on platform's selector
            response_selector = self.platform_selectors[platform]["response_content"]
            
            # Wait a bit for content to be fully rendered
            time.sleep(2)
            
            try:
                response_elements = self.driver.find_elements(*response_selector)
                if not response_elements:
                    self.logger.warning(f"No response elements found for {platform}")
                    return None
                    
                # Usually the last element contains the most recent response
                response_element = response_elements[-1]
                response_text = response_element.text
                
                if not response_text:
                    self.logger.warning(f"Empty response from {platform}")
                    # Try to get innerHTML as fallback
                    response_text = self.driver.execute_script("return arguments[0].innerHTML;", response_element)
                    
                return response_text
            except NoSuchElementException:
                self.logger.error(f"Response element not found for {platform}")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting response from {platform}: {str(e)}")
            return None
    
    def _human_delay(self):
        """Add a random delay to simulate human behavior"""
        min_time = self.settings.get("wait_time_min", 1.0)
        max_time = self.settings.get("wait_time_max", 3.0)
        delay = min_time + ((max_time - min_time) * random.random())
        time.sleep(delay)