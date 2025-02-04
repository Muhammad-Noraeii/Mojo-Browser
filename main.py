import sys
import json
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QDialog, QFormLayout, QTabWidget, QTextEdit, QCheckBox,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl

class DownloadHandler:
    def __init__(self, browser):
        self.browser = browser
        self.browser.page().profile().downloadRequested.connect(self.handle_download)

    def handle_download(self, download_item):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            None, "Save File As", download_item.path(), "All Files (*)", options=options
        )

        if save_path:
            download_item.setPath(save_path)
            download_item.accept()

            QMessageBox.information(None, "Download Started", f"Downloading: {download_item.url().toString()}")

            download_item.downloadProgress.connect(self.show_download_progress)
            download_item.finished.connect(lambda: self.download_finished(save_path))

    def show_download_progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            progress = (bytes_received / bytes_total) * 100
            print(f"Download Progress: {progress:.2f}%")

    def download_finished(self, save_path):
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

        # Set up tabs
        self.setup_general_tab()
        self.setup_security_tab()
        self.setup_data_management_tab()
        self.setup_about_tab()

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

    def setup_general_tab(self):
        self.general_layout = QFormLayout()
        self.general_tab.setLayout(self.general_layout)

        self.home_page_label = QLabel("Home Page:")
        self.home_page_input = QLineEdit()
        self.home_page_input.setPlaceholderText("Enter your home page URL...")
        self.general_layout.addRow(self.home_page_label, self.home_page_input)

        self.search_engine_label = QLabel("Search Engine:")
        self.search_engine_dropdown = QComboBox()
        self.search_engine_dropdown.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo"])
        self.general_layout.addRow(self.search_engine_label, self.search_engine_dropdown)

        self.theme_label = QLabel("Theme:")
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Dark", "Light"])
        self.general_layout.addRow(self.theme_label, self.theme_dropdown)

    def setup_security_tab(self):
        self.security_layout = QFormLayout()
        self.security_tab.setLayout(self.security_layout)

        self.javascript_checkbox = QCheckBox("Enable JavaScript")
        self.javascript_checkbox.setChecked(True)
        self.security_layout.addRow(self.javascript_checkbox)

        self.popup_checkbox = QCheckBox("Block Pop-ups")
        self.popup_checkbox.setChecked(True)
        self.security_layout.addRow(self.popup_checkbox)

        self.mixed_content_checkbox = QCheckBox("Block Mixed Content (HTTP in HTTPS)")
        self.mixed_content_checkbox.setChecked(True)
        self.security_layout.addRow(self.mixed_content_checkbox)

        self.clear_cookies_button = QPushButton("Clear Cookies")
        self.clear_cookies_button.clicked.connect(self.clear_cookies)
        self.security_layout.addWidget(self.clear_cookies_button)

    def setup_data_management_tab(self):
        self.data_management_layout = QVBoxLayout()
        self.data_management_tab.setLayout(self.data_management_layout)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.data_management_layout.addWidget(self.clear_cache_button)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        self.data_management_layout.addWidget(self.clear_history_button)

        self.cache_size_label = QLabel("Cache Size: Calculating...")
        self.data_management_layout.addWidget(self.cache_size_label)

    def setup_about_tab(self):
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
            "https://Github.com/Muhammad-Noraeii\n"
            "https://Github.com/Guguss-31/"
        )
        self.about_layout.addWidget(self.about_text)

    def update_cache_size(self):
        profile = QWebEngineProfile.defaultProfile()
        cache_path = profile.cachePath()
        total_size = self.get_directory_size(cache_path)
        self.cache_size_label.setText(f"Cache Size: {total_size / (1024 * 1024):.2f} MB")

    def get_directory_size(self, directory):
        total = 0
        for dirpath, _, filenames in os.walk(directory):
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
        self.parent().clear_history_data()
        print("History cleared!")

    def save_settings(self):
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

        self.settings_file = "settings.json"
        self.bookmarks_file = "bookmarks.json"
        self.history_file = "history.json"
        self.load_settings()
        self.load_bookmarks()
        self.load_history()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.nav_bar = QHBoxLayout()

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.browser_back)

        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.browser_forward)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.browser_reload)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        self.bookmark_button = QPushButton("Bookmark")
        self.bookmark_button.clicked.connect(self.add_bookmark)

        self.view_bookmarks_button = QPushButton("View Bookmarks")
        self.view_bookmarks_button.clicked.connect(self.view_bookmarks)

        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(self.view_history)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL or search term...")
        self.address_bar.returnPressed.connect(self.load_page)

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.load_page)

        self.nav_bar.addWidget(self.back_button)
        self.nav_bar.addWidget(self.forward_button)
        self.nav_bar.addWidget(self.reload_button)
        self.nav_bar.addWidget(self.address_bar)
        self.nav_bar.addWidget(self.go_button)
        self.nav_bar.addWidget(self.bookmark_button)
        self.nav_bar.addWidget(self.view_bookmarks_button)
        self.nav_bar.addWidget(self.history_button)
        self.nav_bar.addWidget(self.settings_button)

        self.browser = QWebEngineView()

        self.download_handler = DownloadHandler(self.browser)

        self.layout.addLayout(self.nav_bar)
        self.layout.addWidget(self.browser)

        self.browser.setUrl(QUrl(self.home_page))
        self.browser.urlChanged.connect(self.update_history)

        self.apply_styles()

    def load_page(self):
        url = self.address_bar.text().strip()
        if re.match(r'^(http://|https://)', url) or re.search(r'\.\w{2,}', url):
            self.browser.setUrl(QUrl(url if url.startswith(('http://', 'https://')) else f"http://{url}"))
        else:
            search_url = self.get_search_url(url)
            self.browser.setUrl(QUrl(search_url))

    def get_search_url(self, query):
        search_engines = {
            "Google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
            "Bing": f"https://www.bing.com/search?q={query.replace(' ', '+')}",
            "DuckDuckGo": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
            "Yahoo": f"https://search.yahoo.com/search?p={query.replace(' ', '+')}"
        }
        return search_engines.get(self.search_engine, search_engines["Google"])

    def browser_back(self):
        if self.browser.history().canGoBack():
            self.browser.back()

    def browser_forward(self):
        if self.browser.history().canGoForward():
            self.browser.forward()

    def browser_reload(self):
        self.browser.reload()

    def open_settings(self):
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
            self.home_page = "https://www.google.com"
            self.search_engine = "Google"
            self.theme = "Dark"
            self.javascript_enabled = True
            self.block_popups = True
            self.block_mixed_content = True

    def save_settings(self):
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

    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, "r") as file:
                self.bookmarks = json.load(file)
        else:
            self.bookmarks = []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as file:
            json.dump(self.bookmarks, file)

    def add_bookmark(self):
        current_url = self.browser.url().toString()
        if current_url not in self.bookmarks:
            self.bookmarks.append(current_url)
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmark Added", f"Bookmarked: {current_url}")
        else:
            QMessageBox.information(self, "Bookmark Exists", "This URL is already bookmarked.")

    def view_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Bookmarks")
        dialog.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        bookmark_list = QListWidget()
        for bookmark in self.bookmarks:
            item = QListWidgetItem(bookmark)
            bookmark_list.addItem(item)
        bookmark_list.itemDoubleClicked.connect(lambda item: self.load_bookmarked_page(item.text()))
        layout.addWidget(bookmark_list)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def load_bookmarked_page(self, url):
        self.browser.setUrl(QUrl(url))

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                self.history = json.load(file)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, "w") as file:
            json.dump(self.history, file)

    def update_history(self, url):
        url_str = url.toString()
        if url_str not in self.history:
            self.history.append(url_str)
            self.save_history()

    def view_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("History")
        dialog.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        history_list = QListWidget()
        for history_item in self.history:
            item = QListWidgetItem(history_item)
            history_list.addItem(item)
        history_list.itemDoubleClicked.connect(lambda item: self.load_history_page(item.text()))
        layout.addWidget(history_list)
        clear_history_button = QPushButton("Clear History")
        clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_button)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def load_history_page(self, url):
        self.browser.setUrl(QUrl(url))

    def clear_history(self):
        self.history = []
        self.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")

    def clear_history_data(self):
        self.history = []
        self.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")

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
