import os
import json
import glob
import requests
import logging
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

logging.basicConfig(filename='mojo_browser.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtensionManager:
    def __init__(self, browser):
        self.browser = browser
        self.extensions = {}
        self.extension_status = {}
        self.extensions_dir = "extensions"
        self.store_url = "https://mojox.org/MojoBrowser/Assets/js/"
        self.cache_file = "extension_cache.json"
        try:
            os.makedirs(self.extensions_dir, exist_ok=True)
            self.load_extension_status()
            self.load_extensions()
            self.update_extension_cache()
        except Exception as e:
            logger.error(f"Failed to initialize ExtensionManager: {str(e)}")
            self.browser.statusBar().showMessage(f"Extension init failed: {str(e)}", 5000)

    def load_extensions(self):
        try:
            ext_files = glob.glob(f"{self.extensions_dir}/*.js")
            self.extensions.clear()
            for ext_file in ext_files:
                ext_name = os.path.splitext(os.path.basename(ext_file))[0]
                self.extensions[ext_name] = ext_file
                logger.info(f"Loaded extension: {ext_name}")
            self.validate_extensions()
        except Exception as e:
            logger.error(f"Failed to load extensions: {str(e)}")

    def validate_extensions(self):
        for ext_name, ext_path in list(self.extensions.items()):
            try:
                with open(ext_path, "r", encoding="utf-8") as f:
                    js_code = f.read()
                    if not js_code.strip() or "malicious" in js_code.lower():
                        del self.extensions[ext_name]
                        os.remove(ext_path)
                        logger.warning(f"Removed invalid or potentially malicious extension: {ext_name}")
            except Exception as e:
                logger.error(f"Failed to validate extension {ext_name}: {str(e)}")
                del self.extensions[ext_name]

    def enable_extension(self, ext_name):
        try:
            if ext_name in self.extensions and self.extension_status.get(ext_name) != 'enabled':
                self.extension_status[ext_name] = 'enabled'
                self.save_extension_status()
                self.inject_extension(ext_name)
                logger.info(f"Enabled extension: {ext_name}")
        except Exception as e:
            logger.error(f"Failed to enable extension {ext_name}: {str(e)}")

    def disable_extension(self, ext_name):
        try:
            if ext_name in self.extension_status:
                self.extension_status[ext_name] = 'disabled'
                self.save_extension_status()
                logger.info(f"Disabled extension: {ext_name}")
        except Exception as e:
            logger.error(f"Failed to disable extension {ext_name}: {str(e)}")

    def save_extension_status(self):
        try:
            with open("extension_status.json", "w", encoding="utf-8") as f:
                json.dump(self.extension_status, f, indent=4)
            logger.info("Saved extension status")
        except Exception as e:
            logger.error(f"Failed to save extension status: {str(e)}")

    def load_extension_status(self):
        try:
            if os.path.exists("extension_status.json"):
                with open("extension_status.json", "r", encoding="utf-8") as f:
                    self.extension_status = json.load(f)
                logger.info("Loaded extension status")
        except Exception as e:
            logger.error(f"Failed to load extension status: {str(e)}")

    def download_extension(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            ext_name = os.path.splitext(os.path.basename(url.split('?')[0]))[0]
            ext_path = os.path.join(self.extensions_dir, f"{ext_name}.js")
            with open(ext_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            self.extensions[ext_name] = ext_path
            self.load_extensions()
            self.update_extension_cache()
            logger.info(f"Downloaded extension: {ext_name}")
            return ext_name
        except Exception as e:
            logger.error(f"Failed to download extension from {url}: {str(e)}")
            return None

    def fetch_store_extensions(self):
        try:
            response = requests.get(f"{self.store_url}scripts.js", timeout=10)
            response.raise_for_status()
            extensions = response.json()
            self.cache_extensions(extensions)
            return extensions
        except Exception as e:
            logger.error(f"Failed to fetch store extensions: {str(e)}")
            return self.load_cached_extensions()

    def inject_extensions(self, browser):
        try:
            if not browser.settings().testAttribute(QWebEngineSettings.JavascriptEnabled):
                logger.warning("JavaScript disabled, skipping extension injection")
                return
            for ext_name, ext_path in self.extensions.items():
                if self.extension_status.get(ext_name) == 'enabled':
                    self.inject_extension(ext_name, browser)
        except Exception as e:
            logger.error(f"Failed to inject extensions: {str(e)}")

    def inject_extension(self, ext_name, browser=None):
        try:
            browser = browser or self.browser.tabs.currentWidget()
            with open(self.extensions[ext_name], "r", encoding="utf-8") as f:
                js_code = f.read()
                browser.page().runJavaScript(js_code)
                logger.info(f"Injected extension: {ext_name}")
        except Exception as e:
            logger.error(f"Failed to inject extension {ext_name}: {str(e)}")

    def update_extension_cache(self):
        try:
            cache = {name: os.path.getmtime(path) for name, path in self.extensions.items()}
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f)
            logger.info("Updated extension cache")
        except Exception as e:
            logger.error(f"Failed to update extension cache: {str(e)}")

    def cache_extensions(self, extensions):
        try:
            with open(self.cache_file, "r+", encoding="utf-8") as f:
                cache = json.load(f)
                cache["store"] = extensions
                f.seek(0)
                json.dump(cache, f, indent=4)
            logger.info("Cached store extensions")
        except Exception as e:
            logger.error(f"Failed to cache store extensions: {str(e)}")

    def load_cached_extensions(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                    return cache.get("store", [])
            return []
        except Exception as e:
            logger.error(f"Failed to load cached extensions: {str(e)}")
            return []