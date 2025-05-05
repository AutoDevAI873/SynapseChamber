import os
import logging
import time
import random
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CAPTCHASolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = {
            "use_tesseract": True,
            "tesseract_path": r"/usr/bin/tesseract",  # Default Linux path
            "delay_min": 1.0,  # Minimum delay for human-like behavior
            "delay_max": 3.0,  # Maximum delay for human-like behavior
            "confidence_threshold": 0.7  # Confidence threshold for image recognition
        }
        
        # Set Tesseract path
        if os.path.exists(self.settings["tesseract_path"]):
            pytesseract.pytesseract.tesseract_cmd = self.settings["tesseract_path"]
        else:
            self.logger.warning(f"Tesseract not found at {self.settings['tesseract_path']}. OCR may not work properly.")
    
    def update_settings(self, settings):
        """Update captcha solver settings"""
        self.settings.update(settings)
        
        # Update Tesseract path if provided
        if "tesseract_path" in settings and os.path.exists(settings["tesseract_path"]):
            pytesseract.pytesseract.tesseract_cmd = settings["tesseract_path"]
        
        self.logger.info(f"Updated captcha solver settings: {self.settings}")
    
    def solve_recaptcha(self, driver):
        """
        Attempt to solve reCAPTCHA
        Returns True if successful, False otherwise
        """
        self.logger.info("Attempting to solve reCAPTCHA...")
        
        try:
            # First, check if there's a checkbox reCAPTCHA
            try:
                # Look for the reCAPTCHA iframe
                recaptcha_frame = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
                )
                
                # Switch to the reCAPTCHA iframe
                driver.switch_to.frame(recaptcha_frame)
                
                # Find and click the checkbox
                checkbox = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox"))
                )
                
                # Add human-like delay before clicking
                self._human_delay()
                checkbox.click()
                
                # Switch back to the main content
                driver.switch_to.default_content()
                
                # Wait to see if the checkbox solved it
                time.sleep(2)
                
                # Check if an image challenge appeared
                image_frames = driver.find_elements(By.CSS_SELECTOR, "iframe[title='recaptcha challenge']")
                if image_frames:
                    # We need to solve the image challenge
                    driver.switch_to.frame(image_frames[0])
                    return self._solve_image_challenge(driver)
                
                return True  # Successfully clicked checkbox with no challenge
                
            except Exception as e:
                self.logger.warning(f"Checkbox reCAPTCHA not found or not clickable: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error solving reCAPTCHA: {str(e)}")
            driver.switch_to.default_content()  # Make sure we're back to the main content
            return False
    
    def _solve_image_challenge(self, driver):
        """Attempt to solve reCAPTCHA image challenge"""
        self.logger.info("Attempting to solve image challenge...")
        
        try:
            # Get the challenge text to know what to look for
            challenge_text = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-imageselect-desc-wrapper"))
            ).text
            
            self.logger.info(f"Challenge text: {challenge_text}")
            
            # Find all image tiles
            image_tiles = driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
            if not image_tiles:
                self.logger.warning("No image tiles found")
                return False
            
            # For now, use a simple heuristic approach
            # For example, if it asks for vehicles, try to identify vehicles in images
            # This is oversimplified and would need actual image recognition in production
            
            # For demonstration, just click a few random tiles
            clicked = False
            for i in range(min(3, len(image_tiles))):
                tile_index = random.randint(0, len(image_tiles) - 1)
                self._human_delay()
                image_tiles[tile_index].click()
                clicked = True
            
            if clicked:
                # Click the Verify button
                verify_button = driver.find_element(By.CSS_SELECTOR, "#recaptcha-verify-button")
                self._human_delay()
                verify_button.click()
                
                # Wait to see if it was accepted
                time.sleep(3)
                
                # Check for new challenge (failure case)
                if driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-incorrect-response"):
                    self.logger.warning("Image challenge failed, incorrect selection")
                    return False
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error solving image challenge: {str(e)}")
            return False
    
    def solve_cloudflare(self, driver):
        """
        Attempt to solve Cloudflare 'Are you human' challenge
        Returns True if successful, False otherwise
        """
        self.logger.info("Attempting to solve Cloudflare challenge...")
        
        try:
            # Look for common Cloudflare elements
            checkbox = driver.find_elements(By.CSS_SELECTOR, ".cf-checkbox")
            if checkbox:
                self._human_delay()
                checkbox[0].click()
                time.sleep(2)
                return True
            
            # Sometimes Cloudflare just requires waiting
            time.sleep(5)
            
            # Check if the challenge is gone
            if not driver.find_elements(By.CSS_SELECTOR, "#cf-please-wait"):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error solving Cloudflare challenge: {str(e)}")
            return False
    
    def solve_text_captcha(self, driver, image_element):
        """
        Attempt to solve a text-based CAPTCHA using OCR
        image_element should be a WebElement containing the CAPTCHA image
        Returns the recognized text, or None if failed
        """
        self.logger.info("Attempting to solve text CAPTCHA...")
        
        if not self.settings.get("use_tesseract", True):
            self.logger.warning("Tesseract OCR is disabled in settings")
            return None
        
        try:
            # Get the image
            image_src = image_element.get_attribute("src")
            
            # Check if it's a data URL
            if image_src.startswith("data:image"):
                # Extract the base64 part
                b64_data = image_src.split(",")[1]
                image_data = base64.b64decode(b64_data)
                img = Image.open(io.BytesIO(image_data))
            else:
                # It's a URL, use requests to get it
                # Note: This is simplified and might not work for all cases
                import requests
                response = requests.get(image_src)
                img = Image.open(io.BytesIO(response.content))
            
            # Convert to OpenCV format for preprocessing
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Preprocess the image to improve OCR accuracy
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get black and white image
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Remove noise
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Convert back to PIL image for Tesseract
            processed_img = Image.fromarray(opening)
            
            # Use Tesseract to get the text
            captcha_text = pytesseract.image_to_string(processed_img, config='--psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            
            # Clean up the result
            captcha_text = captcha_text.strip()
            self.logger.info(f"Recognized CAPTCHA text: {captcha_text}")
            
            return captcha_text if captcha_text else None
            
        except Exception as e:
            self.logger.error(f"Error solving text CAPTCHA: {str(e)}")
            return None
    
    def _human_delay(self):
        """Add a random delay to simulate human behavior"""
        delay_time = random.uniform(
            self.settings.get("delay_min", 1.0),
            self.settings.get("delay_max", 3.0)
        )
        time.sleep(delay_time)
