import os
import json
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, data_file="config.json"):
        self.data_file = data_file
        self.data = {
            "extensions": {
                "status": {},
                "cache": {}
            },
            "privacy": {
                "settings": {
                    "https_only": True,
                    "permissions": {},
                    "anti_fingerprinting_enabled": True
                },
                "proxy_cache": {}
            },
            "browser": {
                "settings": {
                    "home_page": "https://mojox.org/search",
                    "search_engine": "Google",
                    "theme": "Dark",
                    "javascript_enabled": True,
                    "block_popups": True,
                    "block_mixed_content": True,
                    "new_tab_behavior": "Home Page",
                    "hardware_acceleration": True,
                    "preload_pages": False,
                    "cache_size_limit": "250 MB",
                    "privacy_settings": {
                        "do_not_track": True,
                        "block_third_party_cookies": True,
                        "block_trackers": False,
                        "clear_data_on_exit": False,
                        "private_browsing": False,
                        "fingerprint_protection": False
                    }
                },
                "bookmarks": [],
                "history": []
            }
        }
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    self._merge_data(self.data, loaded_data)
                logger.info("Loaded data from %s", self.data_file)
        except Exception as e:
            logger.error("Failed to load data: %s", str(e))
            self.save_data()  

    def _merge_data(self, default, loaded):
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_data(default[key], value)
                else:
                    default[key] = value

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            logger.info("Saved data to %s", self.data_file)
        except Exception as e:
            logger.error("Failed to save data: %s", str(e))

    def get_extension_status(self):
        return self.data["extensions"]["status"]

    def set_extension_status(self, status):
        self.data["extensions"]["status"] = status
        self.save_data()

    def get_extension_cache(self):
        return self.data["extensions"]["cache"]

    def set_extension_cache(self, cache):
        self.data["extensions"]["cache"] = cache
        self.save_data()

    def get_privacy_settings(self):
        return self.data["privacy"]["settings"]

    def set_privacy_settings(self, settings):
        self.data["privacy"]["settings"] = settings
        self.save_data()

    def get_proxy_cache(self):
        return self.data["privacy"]["proxy_cache"]

    def set_proxy_cache(self, proxy_cache):
        self.data["privacy"]["proxy_cache"] = proxy_cache
        self.save_data()

    def get_browser_settings(self):
        return self.data["browser"]["settings"]

    def set_browser_settings(self, settings):
        self.data["browser"]["settings"] = settings
        self.save_data()

    def get_bookmarks(self):
        return self.data["browser"]["bookmarks"]

    def set_bookmarks(self, bookmarks):
        self.data["browser"]["bookmarks"] = bookmarks
        self.save_data()

    def get_history(self):
        return self.data["browser"]["history"]

    def set_history(self, history):
        self.data["browser"]["history"] = history
        self.save_data()

    def clear_all_private_data(self):
        self.data["browser"]["history"] = []
        self.data["browser"]["bookmarks"] = []
        self.save_data()