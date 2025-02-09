import sys
import json
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QDialog, QFormLayout, QTabWidget, QTextEdit, QCheckBox,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QProgressDialog, QToolBar, QStatusBar,
    QAction, QStyle, QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QIcon

class DownloadHandler:
    def __init__(self, browser):
        self.browser = browser
        self.browser.page().profile().downloadRequested.connect(self.handle_download)
        self.current_download = None

    def handle_download(self, download_item):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            None, "Save File As", download_item.path(), "All Files (*)", options=options
        )

        if save_path:
            download_item.setPath(save_path)
            download_item.accept()

            self.progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 100)
            self.progress_dialog.setWindowTitle("Download Progress")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.canceled.connect(download_item.cancel)

            download_item.downloadProgress.connect(self.show_download_progress)
            download_item.finished.connect(lambda: self.download_finished(save_path))

            self.current_download = download_item
            self.progress_dialog.show()

    def show_download_progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            progress = (bytes_received / bytes_total) * 100
            self.progress_dialog.setValue(int(progress))

    def download_finished(self, save_path):
        self.progress_dialog.close()
        if self.current_download.isFinished() and not self.current_download.isPaused():
            QMessageBox.information(None, "Download Complete", f"File downloaded to: {save_path}")
        else:
            QMessageBox.warning(None, "Download Failed", "The download was canceled or failed.")
        self.current_download = None

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
        profile = self.parent().tabs.currentWidget().page().profile()
        profile.clearHttpCache()
        profile.clearAllVisitedLinks()
        print("Cookies cleared!")

    def clear_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        self.update_cache_size()
        print("Cache cleared!")

    def clear_history(self):
        profile = self.parent().tabs.currentWidget().page().profile()
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
    DEFAULT_HOME_PAGE = "https://search.mojox.org"  # Changed home page

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

        self.create_tool_bar()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)

        self.layout.addWidget(self.tabs)

        self.add_new_tab(QUrl(self.DEFAULT_HOME_PAGE))  # Load default_page.html in the home tab

        self.apply_styles()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_tool_bar(self):
        self.tool_bar = QToolBar("Navigation")
        self.addToolBar(self.tool_bar)
        self.tool_bar.setIconSize(QSize(24, 24))

        # Back button
        self.back_button = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.back_button.setStatusTip("Go to the previous page")
        self.back_button.triggered.connect(self.browser_back)
        self.tool_bar.addAction(self.back_button)

        # Forward button
        self.forward_button = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self.forward_button.setStatusTip("Go to the next page")
        self.forward_button.triggered.connect(self.browser_forward)
        self.tool_bar.addAction(self.forward_button)

        # Reload button
        self.reload_button = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        self.reload_button.setStatusTip("Reload the current page")
        self.reload_button.triggered.connect(self.browser_reload)
        self.tool_bar.addAction(self.reload_button)

        # Home button
        self.home_button = QAction(QIcon.fromTheme("go-home"), "Home", self)
        self.home_button.setStatusTip("Go to the homepage")
        self.home_button.triggered.connect(self.go_home)
        self.tool_bar.addAction(self.home_button)

        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_page)
        self.tool_bar.addWidget(self.address_bar)

        # Go button
        self.go_button = QAction(QIcon.fromTheme("go-jump"), "Go", self)
        self.go_button.setStatusTip("Go to the entered address")
        self.go_button.triggered.connect(self.load_page)
        self.tool_bar.addAction(self.go_button)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tool_bar.addWidget(spacer)

        # New tab button
        self.new_tab_button = QAction(QIcon.fromTheme("document-new"), "New Tab", self)
        self.new_tab_button.setStatusTip("Open a new tab")
        self.new_tab_button.triggered.connect(self.add_new_tab)
        self.tool_bar.addAction(self.new_tab_button)

        # Bookmark button
        self.bookmark_button = QAction(QIcon.fromTheme("emblem-favorite"), "Bookmark", self)
        self.bookmark_button.setStatusTip("Bookmark this page")
        self.bookmark_button.triggered.connect(self.add_bookmark)
        self.tool_bar.addAction(self.bookmark_button)

        # View bookmarks button
        self.view_bookmarks_button = QAction(QIcon.fromTheme("bookmarks"), "View Bookmarks", self)
        self.view_bookmarks_button.setStatusTip("View your bookmarks")
        self.view_bookmarks_button.triggered.connect(self.view_bookmarks)
        self.tool_bar.addAction(self.view_bookmarks_button)

        # History button
        self.history_button = QAction(QIcon.fromTheme("document-open-recent"), "History", self)
        self.history_button.setStatusTip("View your browsing history")
        self.history_button.triggered.connect(self.view_history)
        self.tool_bar.addAction(self.history_button)

        # Settings button
        self.settings_button = QAction(QIcon.fromTheme("preferences-system"), "Settings", self)
        self.settings_button.setStatusTip("Open the settings dialog")
        self.settings_button.triggered.connect(self.open_settings)
        self.tool_bar.addAction(self.settings_button)

    def apply_styles(self):
        # Define styles dictionary for better readability
        styles = {
            "Dark": """
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QToolBar {
                    background-color: #2c2c2c;
                    border: none;
                }
                QToolBar::handle {
                    background: transparent;
                    border: none;
                }
                QLineEdit {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: 1px solid #444;
                    border-radius: 3px;
                    padding: 4px;
                }
                QPushButton, QAction {
                    background-color: #444;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 4px 8px;
                    min-width: 50px;
                }
                QPushButton:hover, QAction:hover {
                    background-color: #555;
                }
                QPushButton:pressed, QAction:pressed {
                    background-color: #333;
                }
                QTabWidget::pane {
                    border: none;
                }
                QTabBar::tab {
                    background: #2c2c2c;
                    color: #ffffff;
                    border: 1px solid #444;
                    border-bottom: none;
                    padding: 4px 12px;
                }
                QTabBar::tab:selected {
                    background: #1e1e1e;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                QStatusBar {
                    background-color: #2c2c2c;
                    color: #ffffff;
                    border: none;
                }
            """,
            "Light": """
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                 QToolBar {
                    background-color: #f0f0f0;
                    border: none;
                }
                QToolBar::handle {
                    background: transparent;
                    border: none;
                }
                QLineEdit {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    padding: 4px;
                }
                QPushButton, QAction {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #bbb;
                    border-radius: 3px;
                    padding: 4px 8px;
                    min-width: 50px;
                }
                QPushButton:hover, QAction:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed, QAction:pressed {
                    background-color: #c0c0c0;
                }
                QTabWidget::pane {
                    border: none;
                }
                QTabBar::tab {
                    background: #e0e0e0;
                    color: #000000;
                    border: 1px solid #bbb;
                    border-bottom: none;
                    padding: 4px 12px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                }
                 QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                QStatusBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: none;
                }
            """
        }
        style = styles.get(self.theme, "")
        self.setStyleSheet(style)

    def add_new_tab(self, url=None):
        browser = QWebEngineView()
        self.apply_webengine_settings(browser)
        if url:
            browser.setUrl(url)
        else:
            browser.setUrl(QUrl(self.DEFAULT_HOME_PAGE))
        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda url, browser=browser: self.update_tab_title(browser, url))
        browser.urlChanged.connect(self.update_history)
        browser.urlChanged.connect(lambda url, browser=browser: self.update_address_bar(self.tabs.currentIndex()))
        browser.loadStarted.connect(self.show_loading)
        browser.loadFinished.connect(self.hide_loading)
        self.download_handler = DownloadHandler(browser)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def update_tab_title(self, browser, url):
        i = self.tabs.indexOf(browser)
        self.tabs.setTabText(i, browser.page().title())

    def update_address_bar(self, index):
        browser = self.tabs.widget(index)
        if browser:
            url = browser.url().toString()
            self.address_bar.setText(url)

    def load_page(self):
        url = self.address_bar.text().strip()
        browser = self.tabs.currentWidget()
        if re.match(r'^(http://|https://)', url) or re.search(r'\.\w{2,}', url):
            browser.setUrl(QUrl(url if url.startswith(('http://', 'https://')) else f"http://{url}"))
        else:
            search_url = self.get_search_url(url)
            browser.setUrl(QUrl(search_url))

    def get_search_url(self, query):
        search_engines = {
            "Google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
            "Bing": f"https://www.bing.com/search?q={query.replace(' ', '+')}",
            "DuckDuckGo": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
            "Yahoo": f"https://search.yahoo.com/search?p={query.replace(' ', '+')}"
        }
        return search_engines.get(self.search_engine, search_engines["Google"])

    def browser_back(self):
        browser = self.tabs.currentWidget()
        if browser.history().canGoBack():
            browser.back()

    def browser_forward(self):
        browser = self.tabs.currentWidget()
        if browser.history().canGoForward():
            browser.forward()

    def browser_reload(self):
        browser = self.tabs.currentWidget()
        browser.reload()

    def go_home(self):
        browser = self.tabs.currentWidget()
        browser.setUrl(QUrl(self.home_page))

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

        self.apply_styles()
        self.save_settings()

        # Apply web engine settings to all existing tabs
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            self.apply_webengine_settings(browser)

    def apply_webengine_settings(self, browser):
        settings = browser.settings()
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(settings.WebAttribute.JavascriptCanOpenWindows, not self.block_popups)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, not self.block_mixed_content)


    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                self.home_page = settings.get("home_page", self.DEFAULT_HOME_PAGE)
                self.search_engine = settings.get("search_engine", "Google")
                self.theme = settings.get("theme", "Dark")
                self.javascript_enabled = settings.get("javascript_enabled", True)
                self.block_popups = settings.get("block_popups", True)
                self.block_mixed_content = settings.get("block_mixed_content", True)
        else:
            self.home_page = self.DEFAULT_HOME_PAGE
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
        try:
            with open(self.bookmarks_file, "r") as file:
                self.bookmarks = json.load(file)
        except FileNotFoundError:
            self.bookmarks = []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as file:
            json.dump(self.bookmarks, file)

    def add_bookmark(self):
        browser = self.tabs.currentWidget()
        current_url = browser.url().toString()
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
        browser = self.tabs.currentWidget()
        browser.setUrl(QUrl(url))

    def load_history(self):
        try:
            with open(self.history_file, "r") as file:
                self.history = json.load(file)
        except FileNotFoundError:
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
        browser = self.tabs.currentWidget()
        browser.setUrl(QUrl(url))

    def clear_history(self):
        self.history = []
        self.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")

    def clear_history_data(self):
        self.history = []
        self.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")

    def show_loading(self):
        self.status_bar.showMessage("Loading...")

    def hide_loading(self):
        self.status_bar.clearMessage()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Set a modern style
    browser = MojoBrowser()
    browser.show()
    sys.exit(app.exec_())