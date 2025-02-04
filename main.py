import sys
import json
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QDialog, QFormLayout, QTabWidget, QTextEdit, QCheckBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl

from PyQt5.QtWidgets import QFileDialog, QMessageBox

class DownloadHandler:
    def __init__(self, browser):
        """
        Initialize the download handler with a reference to the browser.
        :param browser: The QWebEngineView instance.
        """
        self.browser = browser
        self.browser.page().profile().downloadRequested.connect(self.handle_download)

    def handle_download(self, download_item):
        """
        Handle download requests from the browser.
        :param download_item: The download item provided by QWebEngineView.
        """
        # Ask the user where to save the file
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            None, "Save File As", download_item.path(), "All Files (*)", options=options
        )

        if save_path:
            # Set the path and start the download
            download_item.setPath(save_path)
            download_item.accept()

            # Show download started message
            QMessageBox.information(None, "Download Started", f"Downloading: {download_item.url().toString()}")

            # Connect signals for download progress and completion
            download_item.downloadProgress.connect(self.show_download_progress)
            download_item.finished.connect(lambda: self.download_finished(save_path))

    def show_download_progress(self, bytes_received, bytes_total):
        """
        Display download progress in the console.
        :param bytes_received: Number of bytes received so far.
        :param bytes_total: Total number of bytes to download.
        """
        if bytes_total > 0:
            progress = (bytes_received / bytes_total) * 100
            print(f"Download Progress: {progress:.2f}%")

    def download_finished(self, save_path):
        """
        Notify the user when the download is finished.
        :param save_path: The path where the file was saved.
        """
        QMessageBox.information(None, "Download Complete", f"File downloaded to: {save_path}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 500, 600)

        # Tab widget for settings
        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.security_tab = QWidget()
        self.data_management_tab = QWidget()
        self.about_tab = QWidget()

        # Add tabs
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.security_tab, "Security")
        self.tabs.addTab(self.data_management_tab, "Data Management")
        self.tabs.addTab(self.about_tab, "About Us")

        # General Settings Layout
        self.general_layout = QFormLayout()
        self.general_tab.setLayout(self.general_layout)

        # Home page setting
        self.home_page_label = QLabel("Home Page:")
        self.home_page_input = QLineEdit()
        self.home_page_input.setPlaceholderText("Enter your home page URL...")
        self.general_layout.addRow(self.home_page_label, self.home_page_input)

        # Search engine setting
        self.search_engine_label = QLabel("Search Engine:")
        self.search_engine_dropdown = QComboBox()
        self.search_engine_dropdown.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo"])
        self.general_layout.addRow(self.search_engine_label, self.search_engine_dropdown)

        # Theme setting
        self.theme_label = QLabel("Theme:")
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Dark", "Light"])
        self.general_layout.addRow(self.theme_label, self.theme_dropdown)

        # Security Settings Layout
        self.security_layout = QFormLayout()
        self.security_tab.setLayout(self.security_layout)

        # JavaScript toggle
        self.javascript_checkbox = QCheckBox("Enable JavaScript")
        self.javascript_checkbox.setChecked(True)
        self.security_layout.addRow(self.javascript_checkbox)

        # Block pop-ups
        self.popup_checkbox = QCheckBox("Block Pop-ups")
        self.popup_checkbox.setChecked(True)
        self.security_layout.addRow(self.popup_checkbox)

        # Block mixed content
        self.mixed_content_checkbox = QCheckBox("Block Mixed Content (HTTP in HTTPS)")
        self.mixed_content_checkbox.setChecked(True)
        self.security_layout.addRow(self.mixed_content_checkbox)

        # Clear cookies button
        self.clear_cookies_button = QPushButton("Clear Cookies")
        self.clear_cookies_button.clicked.connect(self.clear_cookies)
        self.security_layout.addWidget(self.clear_cookies_button)

        # Data Management Layout
        self.data_management_layout = QVBoxLayout()
        self.data_management_tab.setLayout(self.data_management_layout)

        # Cache management
        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.data_management_layout.addWidget(self.clear_cache_button)

        # History management
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        self.data_management_layout.addWidget(self.clear_history_button)

        # Cache size display
        self.cache_size_label = QLabel("Cache Size: Calculating...")
        self.data_management_layout.addWidget(self.cache_size_label)

        # About Us Tab
        self.about_layout = QVBoxLayout()
        self.about_tab.setLayout(self.about_layout)
        self.about_text = QTextEdit()
        self.about_text.setReadOnly(True)
        self.about_text.setText(
            "Mojo Browser | v0.1 Alpha\n\n"
            "Developed using PyQt5 & Python.\n"
            "Features:\n"
            "- Dark and Light themes.\n"
            "- Multiple search engines.\n"
            "- Advanced security settings.\n"
            "- Data management tools.\n\n"
            "- Downloading Files.\n\n"
            "For more information, visit our GitHub repository!\n\n"
            "https://Github.com/Muhammad-Noraeii"
            "https://Github.com/Guguss-31/"
        )
        self.about_layout.addWidget(self.about_text)

        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)

        # Main Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        # Update cache size
        self.update_cache_size()

    def update_cache_size(self):
        # Calculate cache size manually
        profile = QWebEngineProfile.defaultProfile()
        cache_path = profile.cachePath()
        total_size = self.get_directory_size(cache_path)
        self.cache_size_label.setText(f"Cache Size: {total_size / (1024 * 1024):.2f} MB")

    def get_directory_size(self, directory):
        total = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total

    def clear_cookies(self):
        profile = self.parent().browser.page().profile()
        profile.clearHttpCache()
        profile.clearAllVisitedLinks()
        print("Cookies cleared!")

    def clear_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        self.update_cache_size()
        print("Cache cleared!")

    def clear_history(self):
        profile = self.parent().browser.page().profile()
        profile.clearAllVisitedLinks()
        print("History cleared!")

    def save_settings(self):
        # Save the settings
        home_page = self.home_page_input.text()
        search_engine = self.search_engine_dropdown.currentText()
        theme = self.theme_dropdown.currentText()
        javascript_enabled = self.javascript_checkbox.isChecked()
        block_popups = self.popup_checkbox.isChecked()
        block_mixed_content = self.mixed_content_checkbox.isChecked()
        self.parent().apply_settings(
            home_page, search_engine, theme, javascript_enabled, block_popups, block_mixed_content
        )
        self.accept()


class MojoBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mojo Browser")
        self.setGeometry(100, 100, 1024, 768)

        # Load settings from file
        self.settings_file = "settings.json"
        self.load_settings()

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout for the central widget
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create a horizontal layout for the navigation bar
        self.nav_bar = QHBoxLayout()

        # Create navigation buttons with text
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.browser_back)

        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.browser_forward)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.browser_reload)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        # Create the address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL or search term...")
        self.address_bar.returnPressed.connect(self.load_page)

        # Create a button to load the URL
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.load_page)

        # Add buttons and address bar to the navigation bar
        self.nav_bar.addWidget(self.back_button)
        self.nav_bar.addWidget(self.forward_button)
        self.nav_bar.addWidget(self.reload_button)
        self.nav_bar.addWidget(self.address_bar)
        self.nav_bar.addWidget(self.go_button)
        self.nav_bar.addWidget(self.settings_button)

        # Create the web engine view
        self.browser = QWebEngineView()

        # Initialize Download Handler
        self.download_handler = DownloadHandler(self.browser)  # Add download handler

        # Add the navigation bar and the browser to the main layout
        self.layout.addLayout(self.nav_bar)
        self.layout.addWidget(self.browser)

        # Load the default home page
        self.browser.setUrl(QUrl(self.home_page))

        # Apply styles
        self.apply_styles()

    def load_page(self):
        url = self.address_bar.text().strip()
        # Check if the input is a valid URL
        if re.match(r'^(http://|https://)', url) or re.search(r'\.\w{2,}', url):  # Check for domain-like patterns
            # Load the URL directly
            self.browser.setUrl(QUrl(url if url.startswith(('http://', 'https://')) else f"http://{url}"))
        else:
            # Assume it's a search term and search with the selected search engine
            search_url = self.get_search_url(url)
            self.browser.setUrl(QUrl(search_url))

    def get_search_url(self, query):
        # Return the search URL based on the selected search engine
        if self.search_engine == "Google":
            return f"https://www.google.com/search?q={query.replace(' ', '+')}"
        elif self.search_engine == "Bing":
            return f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        elif self.search_engine == "DuckDuckGo":
            return f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
        elif self.search_engine == "Yahoo":
            return f"https://search.yahoo.com/search?p={query.replace(' ', '+')}"

    def browser_back(self):
        if self.browser.history().canGoBack():
            self.browser.back()

    def browser_forward(self):
        if self.browser.history().canGoForward():
            self.browser.forward()

    def browser_reload(self):
        self.browser.reload()

    def open_settings(self):
        # Open the settings dialog
        dialog = SettingsDialog(self)
        dialog.setParent(self)
        dialog.home_page_input.setText(self.home_page)
        dialog.search_engine_dropdown.setCurrentText(self.search_engine)
        dialog.theme_dropdown.setCurrentText(self.theme)
        dialog.javascript_checkbox.setChecked(self.javascript_enabled)
        dialog.popup_checkbox.setChecked(self.block_popups)
        dialog.mixed_content_checkbox.setChecked(self.block_mixed_content)
        dialog.exec_()

    def apply_settings(self, home_page, search_engine, theme, javascript_enabled, block_popups, block_mixed_content):
        # Apply the new settings
        self.home_page = home_page or self.home_page
        self.search_engine = search_engine
        self.theme = theme
        self.javascript_enabled = javascript_enabled
        self.block_popups = block_popups
        self.block_mixed_content = block_mixed_content
        self.browser.setUrl(QUrl(self.home_page))
        self.apply_styles()
        self.save_settings()

    def load_settings(self):
        # Load settings from the JSON file
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                self.home_page = settings.get("home_page", "https://www.google.com")
                self.search_engine = settings.get("search_engine", "Google")
                self.theme = settings.get("theme", "Dark")
                self.javascript_enabled = settings.get("javascript_enabled", True)
                self.block_popups = settings.get("block_popups", True)
                self.block_mixed_content = settings.get("block_mixed_content", True)
        else:
            # Default settings
            self.home_page = "https://www.google.com"
            self.search_engine = "Google"
            self.theme = "Dark"
            self.javascript_enabled = True
            self.block_popups = True
            self.block_mixed_content = True

    def save_settings(self):
        # Save settings to the JSON file
        settings = {
            "home_page": self.home_page,
            "search_engine": self.search_engine,
            "theme": self.theme,
            "javascript_enabled": self.javascript_enabled,
            "block_popups": self.block_popups,
            "block_mixed_content": self.block_mixed_content
        }
        with open(self.settings_file, "w") as file:
            json.dump(settings, file)

    def apply_styles(self):
        if self.theme == "Dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QLineEdit {
                    background-color: #2c2c2c;
                    color: #ffffff;
                    border: 1px solid #444;
                    border-radius: 5px;
                    padding: 6px;
                }
                QPushButton {
                    background-color: #444;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QPushButton:pressed {
                    background-color: #333;
                }
            """)
        elif self.theme == "Light":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                }
                QLineEdit {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 6px;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #bbb;
                    border-radius: 5px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = MojoBrowser()
    browser.show()
    sys.exit(app.exec_())