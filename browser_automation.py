import os
import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# In headless environment, we mock pyautogui and keyboard functionality
HEADLESS_ENV = os.environ.get('DISPLAY') is None
if HEADLESS_ENV:
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
else:
    # In non-headless environments, use actual modules
    import pyautogui
    import keyboard

class BrowserAutomation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.screenshot_dir = "static/screenshots"
        self.settings = {
            "headless": False,
            "timeout": 30,
            "screenshot_on_action": True
        }
        
        # Ensure screenshot directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def update_settings(self, settings):
        """Update the browser automation settings"""
        self.settings.update(settings)
        self.logger.info(f"Updated browser settings: {self.settings}")
    
    def initialize_driver(self):
        """Initialize and return a browser driver"""
        if self.driver is not None:
            self.close_driver()
        
        chrome_options = Options()
        # Always run headless in this environment
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Add user agent to make detection harder
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(self.settings.get("timeout", 30))
        self.logger.info("Browser driver initialized")
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
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
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
