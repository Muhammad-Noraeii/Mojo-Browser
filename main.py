import sys
import json
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QDialog, QFormLayout, QTabWidget, QTextEdit, QCheckBox,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QProgressDialog, QToolBar, QStatusBar,
    QAction, QStyle, QSizePolicy, QSpacerItem, QScrollArea
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

# Constants for styling
PRIMARY_COLOR = "#1e3a8a"  # Dark Blue
SECONDARY_COLOR = "#2c3e50"
TEXT_COLOR = "#ffffff"  # White
ACCENT_COLOR = "#f39c12"
BACKGROUND_COLOR = "#ecf0f1"
DARK_MODE_BACKGROUND = "#000000"  # Black Background
DARK_MODE_TEXT = "#ffffff"  # White Text
BORDER_RADIUS = "8px"
BUTTON_BORDER_RADIUS = "5px"
BUTTON_HOVER_COLOR = "#374151"  # Darker Gray for Hover
BUTTON_PRESSED_COLOR = "#4b5563"  # Even Darker Gray for Pressed

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
        self.setGeometry(300, 300, 600, 500)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self.get_tab_widget_style())
        self.general_tab = QWidget()
        self.security_tab = QWidget()
        self.data_management_tab = QWidget()
        self.about_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.security_tab, "Security")
        self.tabs.addTab(self.data_management_tab, "Data Management")
        self.tabs.addTab(self.about_tab, "About Us")

        self.setup_general_tab()
        self.setup_security_tab()
        self.setup_data_management_tab()
        self.setup_about_tab()

        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet(self.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        self.save_button.clicked.connect(self.save_settings)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        self.update_cache_size()
        self.apply_theme()

    def get_tab_widget_style(self):
        return f"""
            QTabWidget::pane {{
                border-top: 2px solid #C2C7CB;
                border-radius: {BORDER_RADIUS};
            }}
            QTabWidget::tab-bar {{
                left: 5px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                            stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                border: 2px solid #C4C4C3;
                border-bottom-color: #C2C7CB;
                border-top-left-radius: {BORDER_RADIUS};
                border-top-right-radius: {BORDER_RADIUS};
                min-width: 8ex;
                padding: 2px;
                color: #333;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #FAFAFA, stop: 0.4 #F4F4F4,
                                            stop: 0.5 #E2E2E2, stop: 1.0 #D8D8D8);
            }}
            QTabBar::tab:selected {{
                border-color: #9B9B9B;
                border-bottom-color: #C2C7CB;
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """

    def get_button_style(self, background_color, hover_color, pressed_color):
        return f"""
            QPushButton {{
                background-color: {background_color};
                color: {TEXT_COLOR};
                border: none;
                border-radius: {BUTTON_BORDER_RADIUS};
                padding: 10px 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

    def setup_general_tab(self):
        self.general_layout = QFormLayout()
        self.general_tab.setLayout(self.general_layout)

        self.home_page_label = QLabel("Home Page:")
        self.home_page_label.setStyleSheet("font-weight: bold;")
        self.home_page_input = QLineEdit()
        self.home_page_input.setStyleSheet(f"border-radius: {BORDER_RADIUS};")
        self.home_page_input.setPlaceholderText("Enter your home page URL...")
        self.general_layout.addRow(self.home_page_label, self.home_page_input)

        self.search_engine_label = QLabel("Search Engine:")
        self.search_engine_label.setStyleSheet("font-weight: bold;")
        self.search_engine_dropdown = QComboBox()
        self.search_engine_dropdown.setStyleSheet(f"border-radius: {BORDER_RADIUS};")
        self.search_engine_dropdown.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo"])
        self.general_layout.addRow(self.search_engine_label, self.search_engine_dropdown)

        self.theme_label = QLabel("Theme:")
        self.theme_label.setStyleSheet("font-weight: bold;")
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setStyleSheet(f"border-radius: {BORDER_RADIUS};")
        self.theme_dropdown.addItems(["Dark", "Light"])
        self.general_layout.addRow(self.theme_label, self.theme_dropdown)

    def setup_security_tab(self):
        self.security_layout = QFormLayout()
        self.security_tab.setLayout(self.security_layout)

        self.javascript_checkbox = QCheckBox("Enable JavaScript")
        self.javascript_checkbox.setStyleSheet("font-weight: bold;")
        self.javascript_checkbox.setChecked(True)
        self.security_layout.addRow(self.javascript_checkbox)

        self.popup_checkbox = QCheckBox("Block Pop-ups")
        self.popup_checkbox.setStyleSheet("font-weight: bold;")
        self.popup_checkbox.setChecked(True)
        self.security_layout.addRow(self.popup_checkbox)

        self.mixed_content_checkbox = QCheckBox("Block Mixed Content (HTTP in HTTPS)")
        self.mixed_content_checkbox.setStyleSheet("font-weight: bold;")
        self.mixed_content_checkbox.setChecked(True)
        self.security_layout.addRow(self.mixed_content_checkbox)

        self.clear_cookies_button = QPushButton("Clear Cookies")
        self.clear_cookies_button.setStyleSheet(self.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_cookies_button.clicked.connect(self.clear_cookies)
        self.security_layout.addWidget(self.clear_cookies_button)

    def setup_data_management_tab(self):
        self.data_management_layout = QVBoxLayout()
        self.data_management_tab.setLayout(self.data_management_layout)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.setStyleSheet(self.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.data_management_layout.addWidget(self.clear_cache_button)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.setStyleSheet(self.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_history_button.clicked.connect(self.clear_history)
        self.data_management_layout.addWidget(self.clear_history_button)

        self.cache_size_label = QLabel("Cache Size: Calculating...")
        self.cache_size_label.setStyleSheet("font-weight: bold;")
        self.data_management_layout.addWidget(self.cache_size_label)

    def setup_about_tab(self):
        self.about_layout = QVBoxLayout()
        self.about_tab.setLayout(self.about_layout)
        self.about_text = QTextEdit()
        self.about_text.setReadOnly(True)
        self.about_text.setStyleSheet(f"background-color: #f0f0f0; color: #333; border-radius: {BORDER_RADIUS};")
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

    def apply_theme(self):
        theme = self.parent().theme
        if theme == "Dark":
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {DARK_MODE_BACKGROUND};
                    color: {DARK_MODE_TEXT};
                    border-radius: {BORDER_RADIUS};
                }}
                QLabel {{
                    color: {DARK_MODE_TEXT};
                }}
                QLineEdit {{
                    background-color: #3a3a3a;
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #444;
                    border-radius: {BORDER_RADIUS};
                    padding: 4px;
                }}
                QComboBox {{
                    background-color: #3a3a3a;
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #444;
                    border-radius: {BORDER_RADIUS};
                    padding: 4px;
                }}
                QCheckBox {{
                    color: {DARK_MODE_TEXT};
                }}
                QTextEdit {{
                    background-color: #3a3a3a;
                    color: {DARK_MODE_TEXT};
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #444;
                    border-radius: {BORDER_RADIUS};
                    padding: 4px;
                }}
                QPushButton {{
                    background-color: {PRIMARY_COLOR};
                    color: {DARK_MODE_TEXT};
                    border: none;
                    border-radius: {BUTTON_BORDER_RADIUS};
                    padding: 5px 10px;
                }}
                QPushButton:hover {{
                    background-color: {BUTTON_HOVER_COLOR};
                }}
                QPushButton:pressed {{
                    background-color: {BUTTON_PRESSED_COLOR};
                }}
            """)
        else:
            self.setStyleSheet("")  # Revert to default stylesheet

class MojoBrowser(QMainWindow):
    DEFAULT_HOME_PAGE = "https://search.mojox.org"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mojo Browser")
        self.setGeometry(100, 100, 1024, 768)

        self.settings_persistence = SettingsPersistence(self)

        self.bookmarks = []
        self.history = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.create_tool_bar()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)
        self.tabs.setStyleSheet(self.get_tab_style())

        self.layout.addWidget(self.tabs)

        self.settings_persistence.load_settings()
        self.add_new_tab(QUrl(self.home_page))

        self.apply_styles()

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(self.get_statusbar_style())
        self.setStatusBar(self.status_bar)

    def get_tab_style(self):
        return f"""
            QTabWidget::pane {{
                border: none;
                border-radius: {BORDER_RADIUS};
            }}
            QTabBar::tab {{
                background: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                border-bottom: none;
                padding: 8px 20px;
                font-size: 14px;
                border-top-left-radius: {BORDER_RADIUS};
                border-top-right-radius: {BORDER_RADIUS};
            }}
            QTabBar::tab:selected {{
                background: #fff;
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
            QTabBar::tab:hover {{
                background: #e0e0e0;
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
        """

    def get_statusbar_style(self):
        return f"""
            QStatusBar {{
                background-color: #f0f0f0;
                color: #333;
                border: none;
                border-radius: {BORDER_RADIUS};
            }}
        """

    def create_tool_bar(self):
        self.tool_bar = QToolBar("Navigation")
        self.addToolBar(self.tool_bar)
        self.tool_bar.setIconSize(QSize(24, 24))
        self.tool_bar.setStyleSheet(self.get_toolbar_style())

        self.back_button = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.back_button.setStatusTip("Go to the previous page")
        self.back_button.triggered.connect(self.browser_back)
        self.tool_bar.addAction(self.back_button)

        self.forward_button = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self.forward_button.setStatusTip("Go to the next page")
        self.forward_button.triggered.connect(self.browser_forward)
        self.tool_bar.addAction(self.forward_button)

        self.reload_button = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        self.reload_button.setStatusTip("Reload the current page")
        self.reload_button.triggered.connect(self.browser_reload)
        self.tool_bar.addAction(self.reload_button)

        self.home_button = QAction(QIcon.fromTheme("go-home"), "Home", self)
        self.home_button.setStatusTip("Go to the homepage")
        self.home_button.triggered.connect(self.go_home)
        self.tool_bar.addAction(self.home_button)

        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet(self.get_addressbar_style())
        self.address_bar.returnPressed.connect(self.load_page)
        self.tool_bar.addWidget(self.address_bar)

        self.go_button = QAction(QIcon.fromTheme("go-jump"), "Go", self)
        self.go_button.setStatusTip("Go to the entered address")
        self.go_button.triggered.connect(self.load_page)
        self.tool_bar.addAction(self.go_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tool_bar.addWidget(spacer)

        self.new_tab_button = QAction(QIcon.fromTheme("document-new"), "New Tab", self)
        self.new_tab_button.setStatusTip("Open a new tab")
        self.new_tab_button.triggered.connect(self.add_new_tab)
        self.tool_bar.addAction(self.new_tab_button)

        self.bookmark_button = QAction(QIcon.fromTheme("emblem-favorite"), "Bookmark", self)
        self.bookmark_button.setStatusTip("Bookmark this page")
        self.bookmark_button.triggered.connect(self.settings_persistence.add_bookmark)
        self.tool_bar.addAction(self.bookmark_button)

        self.view_bookmarks_button = QAction(QIcon.fromTheme("bookmarks"), "View Bookmarks", self)
        self.view_bookmarks_button.setStatusTip("View your bookmarks")
        self.view_bookmarks_button.triggered.connect(self.settings_persistence.view_bookmarks)
        self.tool_bar.addAction(self.view_bookmarks_button)

        self.history_button = QAction(QIcon.fromTheme("document-open-recent"), "History", self)
        self.history_button.setStatusTip("View your browsing history")
        self.history_button.triggered.connect(self.settings_persistence.view_history)
        self.tool_bar.addAction(self.history_button)

        self.settings_button = QAction(QIcon.fromTheme("preferences-system"), "Settings", self)
        self.settings_button.setStatusTip("Open the settings dialog")
        self.settings_button.triggered.connect(self.open_settings)
        self.tool_bar.addAction(self.settings_button)

    def get_toolbar_style(self):
        button_style = f"""
            QToolButton {{
                background-color: {PRIMARY_COLOR};
                color: {TEXT_COLOR};
                border: none;
                margin: 2px;
                border-radius: {BUTTON_BORDER_RADIUS};
                padding: 5px;
            }}
            QToolButton:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
            QToolButton:pressed {{
                background-color: {BUTTON_PRESSED_COLOR};
            }}
        """

        return f"""
            QToolBar {{
                background-color: {DARK_MODE_BACKGROUND};
                color: {DARK_MODE_TEXT};
                border: none;
                padding: 5px;
                border-radius: {BORDER_RADIUS};
            }}

           {button_style}
        """

    def get_addressbar_style(self):
        return f"""
            QLineEdit {{
                background-color: #3a3a3a;
                color: {DARK_MODE_TEXT};
                border: 1px solid #444;
                border-radius: {BORDER_RADIUS};
                padding: 6px;
                font-size: 14px;
            }}
        """

    def apply_styles(self):
        styles = {
            "Dark": f"""
                QMainWindow {{
                    background-color: {DARK_MODE_BACKGROUND};
                    color: {DARK_MODE_TEXT};
                    border-radius: {BORDER_RADIUS};
                }}
                QToolBar {{
                    background-color: {DARK_MODE_BACKGROUND};
                    color: {DARK_MODE_TEXT};
                    border: none;
                    border-radius: {BORDER_RADIUS};
                }}
                QToolBar::handle {{
                    background: transparent;
                    border: none;
                }}
                QLineEdit {{
                    background-color: #3a3a3a;
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #444;
                    border-radius: {BORDER_RADIUS};
                    padding: 4px;
                }}
                QPushButton, QAction {{
                    background-color: {PRIMARY_COLOR};
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #555;
                    border-radius: {BUTTON_BORDER_RADIUS};
                    padding: 4px 8px;
                    min-width: 50px;
                }}
                QPushButton:hover, QAction:hover {{
                    background-color: {BUTTON_HOVER_COLOR};
                }}
                QPushButton:pressed, QAction:pressed {{
                    background-color: {BUTTON_PRESSED_COLOR};
                }}
                QTabWidget::pane {{
                    border: none;
                    border-radius: {BORDER_RADIUS};
                    background-color: {DARK_MODE_BACKGROUND};
                }}
                QTabBar::tab {{
                    background-color: #2c2c2c;
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #444;
                    border-bottom: none;
                    padding: 4px 12px;
                    border-top-left-radius: {BORDER_RADIUS};
                    border-top-right-radius: {BORDER_RADIUS};
                }}
                QTabBar::tab:selected {{
                    background: {DARK_MODE_BACKGROUND};
                }}
                QTabBar::tab:!selected {{
                    margin-top: 2px;
                }}
                QStatusBar {{
                    background-color: {DARK_MODE_BACKGROUND};
                    color: {DARK_MODE_TEXT};
                    border: none;
                    border-radius: {BORDER_RADIUS};
                }}
                QListWidget {{
                    background-color: #3a3a3a;
                    color: {DARK_MODE_TEXT};
                    border: 1px solid #444;
                    border-radius: {BORDER_RADIUS};
                    padding: 5px;
                    font-size: 14px;
                }}
                QListWidget::item {{
                    padding: 5px;
                }}
                QListWidget::item:selected {{
                    background-color: #555;
                }}
            """,
            "Light": f"""
                QMainWindow {{
                    background-color: {BACKGROUND_COLOR};
                    color: {TEXT_COLOR};
                    border-radius: {BORDER_RADIUS};
                }}
                QToolBar {{
                    background-color: #f0f0f0;
                    border: none;
                    border-radius: {BORDER_RADIUS};
                }}
                QToolBar::handle {{
                    background: transparent;
                    border: none;
                }}
                QLineEdit {{
                    background-color: #f0f0f0;
                    color: {TEXT_COLOR};
                    border: 1px solid #ccc;
                    border-radius: {BORDER_RADIUS};
                    padding: 4px;
                }}
                QPushButton, QAction {{
                    background-color: #e0e0e0;
                    color: {TEXT_COLOR};
                    border: 1px solid #bbb;
                    border-radius: {BUTTON_BORDER_RADIUS};
                    padding: 4px 8px;
                    min-width: 50px;
                }}
                QPushButton:hover, QAction:hover {{
                    background-color: #d0d0d0;
                }}
                QPushButton:pressed, QAction:pressed {{
                    background-color: #c0c0c0;
                }}
                QTabWidget::pane {{
                    border: none;
                    border-radius: {BORDER_RADIUS};
                }}
                QTabBar::tab {{
                    background: #e0e0e0;
                    color: {TEXT_COLOR};
                    border: 1px solid #bbb;
                    border-bottom: none;
                    padding: 4px 12px;
                    border-top-left-radius: {BORDER_RADIUS};
                    border-top-right-radius: {BORDER_RADIUS};
                }}
                QTabBar::tab:selected {{
                    background: {BACKGROUND_COLOR};
                }}
                QTabBar::tab:!selected {{
                    margin-top: 2px;
                }}
                QStatusBar {{
                    background-color: #f0f0f0;
                    color: {TEXT_COLOR};
                    border: none;
                    border-radius: {BORDER_RADIUS};
                }}
                QListWidget {{
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: {BORDER_RADIUS};
                    padding: 5px;
                    font-size: 14px;
                }}
                QListWidget::item {{
                    padding: 5px;
                }}
                QListWidget::item:selected {{
                    background-color: #e0e0e0;
                }}
            """
        }
        style = styles.get(self.theme, "Dark")  # Default to Dark theme if not found
        self.setStyleSheet(style)

        if hasattr(self, 'settings_dialog') and self.settings_dialog is not None:
            self.settings_dialog.apply_theme()

    def add_new_tab(self, url=None):
        browser = QWebEngineView()
        self.apply_webengine_settings(browser)
        if url:
            browser.setUrl(url)
        else:
            browser.setUrl(QUrl(self.home_page))
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
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.setParent(self)
        self.settings_dialog.home_page_input.setText(self.home_page)
        self.settings_dialog.search_engine_dropdown.setCurrentText(self.search_engine)
        self.settings_dialog.theme_dropdown.setCurrentText(self.theme)
        self.settings_dialog.javascript_checkbox.setChecked(self.javascript_enabled)
        self.settings_dialog.popup_checkbox.setChecked(self.block_popups)
        self.settings_dialog.mixed_content_checkbox.setChecked(self.block_mixed_content)
        self.settings_dialog.exec_()

    def apply_settings(self, home_page, search_engine, theme, javascript_enabled, block_mixed_content, block_popups):
        self.home_page = home_page or self.home_page
        self.search_engine = search_engine
        self.theme = theme
        self.javascript_enabled = javascript_enabled
        self.block_popups = block_popups
        self.block_mixed_content = block_mixed_content

        self.apply_styles()
        self.settings_persistence.save_settings()

        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            self.apply_webengine_settings(browser)

    def apply_webengine_settings(self, browser):
        settings = browser.settings()
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(settings.WebAttribute.JavascriptCanOpenWindows, not self.block_popups)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, not self.block_mixed_content)

    def update_history(self, url):
        self.settings_persistence.update_history(url)

    def clear_history_data(self):
        self.history = []
        self.settings_persistence.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")

    def show_loading(self):
        self.status_bar.showMessage("Loading...")

    def hide_loading(self):
        self.status_bar.clearMessage()

class SettingsPersistence:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"
        self.bookmarks_file = "bookmarks.json"
        self.history_file = "history.json"
        self.load_settings()
        self.load_bookmarks()
        self.load_history()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                self.parent.home_page = settings.get("home_page", self.parent.DEFAULT_HOME_PAGE)
                self.parent.search_engine = settings.get("search_engine", "Google")
                self.parent.theme = settings.get("theme", "Dark")
                self.parent.javascript_enabled = settings.get("javascript_enabled", True)
                self.parent.block_popups = settings.get("block_popups", True)
                self.parent.block_mixed_content = settings.get("block_mixed_content", True)
        else:
            self.parent.home_page = self.parent.DEFAULT_HOME_PAGE
            self.parent.search_engine = "Google"
            self.parent.theme = "Dark"
            self.parent.javascript_enabled = True
            self.parent.block_popups = True
            self.parent.block_mixed_content = True

    def save_settings(self):
        settings = {
            "home_page": self.parent.home_page,
            "search_engine": self.parent.search_engine,
            "theme": self.parent.theme,
            "javascript_enabled": self.parent.javascript_enabled,
            "block_popups": self.parent.block_popups,
            "block_mixed_content": self.parent.block_mixed_content
        }
        with open(self.settings_file, "w") as file:
            json.dump(settings, file)

    def load_bookmarks(self):
        try:
            with open(self.bookmarks_file, "r") as file:
                self.parent.bookmarks = json.load(file)
        except FileNotFoundError:
            self.parent.bookmarks = []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as file:
            json.dump(self.parent.bookmarks, file)

    def add_bookmark(self):
        browser = self.parent.tabs.currentWidget()
        current_url = browser.url().toString()
        if current_url not in self.parent.bookmarks:
            self.parent.bookmarks.append(current_url)
            self.save_bookmarks()
            QMessageBox.information(self.parent, "Bookmark Added", f"Bookmarked: {current_url}")
        else:
            QMessageBox.information(self.parent, "Bookmark Exists", "This URL is already bookmarked.")

    def view_bookmarks(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Bookmarks")
        dialog.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        bookmark_list = QListWidget()
        bookmark_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #fff;
                color: #333;
                border: 1px solid #ccc;
                border-radius: {BORDER_RADIUS};
                padding: 5px;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: #e0e0e0;
            }}
        """)
        for bookmark in self.parent.bookmarks:
            item = QListWidgetItem(bookmark)
            bookmark_list.addItem(item)
        bookmark_list.itemDoubleClicked.connect(lambda item: self.load_bookmarked_page(item.text()))
        layout.addWidget(bookmark_list)
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #555;
                color: #fff;
                border: none;
                border-radius: {BUTTON_BORDER_RADIUS};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #777;
            }}
        """)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def load_bookmarked_page(self, url):
        browser = self.parent.tabs.currentWidget()
        browser.setUrl(QUrl(url))

    def load_history(self):
        try:
            with open(self.history_file, "r") as file:
                self.parent.history = json.load(file)
        except FileNotFoundError:
            self.parent.history = []

    def save_history(self):
        with open(self.history_file, "w") as file:
            json.dump(self.parent.history, file)

    def update_history(self, url):
        url_str = url.toString()
        if url_str not in self.parent.history:
            self.parent.history.append(url_str)
            self.save_history()

    def view_history(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("History")
        dialog.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        history_list = QListWidget()
        history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #fff;
                color: #333;
                border: 1px solid #ccc;
                border-radius: {BORDER_RADIUS};
                padding: 5px;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: #e0e0e0;
            }}
        """)
        for history_item in self.parent.history:
            item = QListWidgetItem(history_item)
            history_list.addItem(item)
        history_list.itemDoubleClicked.connect(lambda item: self.load_history_page(item.text()))
        layout.addWidget(history_list)
        clear_history_button = QPushButton("Clear History")
        clear_history_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #555;
                color: #fff;
                border: none;
                border-radius: {BUTTON_BORDER_RADIUS};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #777;
            }}
        """)
        clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_button)
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #555;
                color: #fff;
                border: none;
                border-radius: {BUTTON_BORDER_RADIUS};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #777;
            }}
        """)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def load_history_page(self, url):
        browser = self.parent.tabs.currentWidget()
        browser.setUrl(QUrl(url))

    def clear_history(self):
        self.parent.history = []
        self.save_history()
        QMessageBox.information(self.parent, "History Cleared", "Browsing history has been cleared.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    browser = MojoBrowser()
    browser.show()
    sys.exit(app.exec_())
