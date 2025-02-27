import sys
import json
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QDialog, QFormLayout, QTabWidget, QTextEdit, QCheckBox,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QProgressDialog, QToolBar, QStatusBar,
    QAction, QStyle, QSizePolicy, QSpacerItem, QScrollArea, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QFont

from MojoPrivacy import PrivacyEngine, PrivacyPage, initialize_privacy

PRIMARY_COLOR = "#4CAF50"
TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#ecf0f1"
DARK_MODE_BACKGROUND = "#1a1a1a"
DARK_MODE_TEXT = "#e0e0e0"
DARK_MODE_ACCENT = "#2c2c2c"
LIGHT_MODE_BACKGROUND = "#ffffff"
LIGHT_MODE_TEXT = "#000000"
LIGHT_MODE_ACCENT = "#f0f0f0"
BORDER_RADIUS = "8px"
BUTTON_BORDER_RADIUS = "5px"
BUTTON_HOVER_COLOR = "#999999"
BUTTON_PRESSED_COLOR = "#666666"

UI_FONT = QFont("Nunito", 10)
FALLBACK_FONT = QFont("Arial", 10)

class DownloadWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(str, bool)
    
    def __init__(self, download_item):
        super().__init__()
        self.download_item = download_item
        
    def run(self):
        self.download_item.downloadProgress.connect(self.progress.emit)
        self.download_item.finished.connect(lambda: self.finished.emit(
            self.download_item.path(), 
            self.download_item.isFinished() and not self.download_item.isPaused()
        ))


PRIMARY_COLOR = "#1e3a8a"  
SECONDARY_COLOR = "#2c3e50"
TEXT_COLOR = "#ffffff"  
ACCENT_COLOR = "#f39c12"
BACKGROUND_COLOR = "#ecf0f1"
DARK_MODE_BACKGROUND = "#000000"  
DARK_MODE_TEXT = "#ffffff"  
BORDER_RADIUS = "8px"
BUTTON_BORDER_RADIUS = "5px"
BUTTON_HOVER_COLOR = "#374151"  
BUTTON_PRESSED_COLOR = "#4b5563"  

class DownloadHandler:
    def __init__(self, browser):
        self.browser = browser
        self.current_downloads = []
        self.browser.page().profile().downloadRequested.connect(self.handle_download)

    def handle_download(self, download_item):
        save_path, _ = QFileDialog.getSaveFileName(None, "Save File As", download_item.path(), "All Files (*)")
        if save_path:
            download_item.setPath(save_path)
            download_item.accept()
            progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 100)
            progress_dialog.setWindowTitle(f"Download Progress ({len(self.current_downloads) + 1})")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.canceled.connect(download_item.cancel)
            progress_dialog.setFont(UI_FONT)
            
            worker = DownloadWorker(download_item)
            worker.progress.connect(lambda br, bt: self.show_download_progress(progress_dialog, br, bt))
            worker.finished.connect(lambda sp, s: self.download_finished(progress_dialog, sp, s))
            self.current_downloads.append((download_item, worker, progress_dialog))
            worker.start()
            progress_dialog.show()

    def show_download_progress(self, dialog, bytes_received, bytes_total):
        if bytes_total > 0:
            dialog.setValue(int((bytes_received / bytes_total) * 100))

    def download_finished(self, dialog, save_path, success):
        dialog.close()
        if success:
            QMessageBox.information(None, "Download Complete", f"File downloaded to: {save_path}", QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.warning(None, "Download Failed", "The download was canceled or failed.", QMessageBox.Ok, QMessageBox.Ok)
        if self.current_downloads:
            self.current_downloads.pop(0)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 600, 500)
        self.setFont(UI_FONT)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self.get_tab_widget_style())
        self.tabs.setFont(UI_FONT)
        self.general_tab = QWidget()
        self.security_tab = QWidget()
        self.data_management_tab = QWidget()
        self.about_tab = QWidget()

        self.tabs.addTab(self.general_tab, QIcon("icons/general.png") if os.path.exists("icons/general.png") else QIcon.fromTheme("preferences-desktop"), "General")
        self.tabs.addTab(self.security_tab, "Security")
        self.tabs.addTab(self.data_management_tab, "Data Management")
        self.tabs.addTab(self.about_tab, "About Us")

        self.setup_general_tab()
        self.setup_security_tab()
        self.setup_data_management_tab()
        self.setup_about_tab()

        self.save_button = QPushButton(QIcon("icons/save.png") if os.path.exists("icons/save.png") else QIcon.fromTheme("document-save"), "Save Settings")
        self.save_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        self.save_button.setFont(UI_FONT)
        self.save_button.clicked.connect(self.save_settings)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        self.update_cache_size()
        self.apply_theme()

    def get_tab_widget_style(self):
        theme = self.parent.theme
        tab_text_color, tab_background_color, tab_selected_background = (
            (DARK_MODE_TEXT, DARK_MODE_ACCENT, DARK_MODE_BACKGROUND) if theme == "Dark" 
            else (LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, LIGHT_MODE_BACKGROUND)
        )
        return (
            f"QTabWidget::pane {{ border: none; border-radius: {BORDER_RADIUS}; "
            f"background-color: {DARK_MODE_BACKGROUND if theme == 'Dark' else LIGHT_MODE_BACKGROUND}; }}"
            f"QTabBar::tab {{ background-color: {tab_background_color}; color: {tab_text_color}; "
            f"border: 1px solid {'#444' if theme == 'Dark' else '#bbb'}; border-bottom: none; "
            f"padding: 8px 16px; border-top-left-radius: {BORDER_RADIUS}; "
            f"border-top-right-radius: {BORDER_RADIUS}; }}"
            f"QTabBar::tab:selected {{ background: {tab_selected_background}; border-bottom: 2px solid {PRIMARY_COLOR}; }}"
            "QTabBar::tab:!selected {{ margin-top: 2px; }}"
            f"QTabBar::tab:hover {{ background: {'#e0e0e0' if theme == 'Light' else '#3a3a3a'}; }}"
            "QTabWidget::tab-bar {{ alignment: center; }}"
        )

    def setup_general_tab(self):
        layout = QFormLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.general_tab.setLayout(layout)

        self.home_page_input = QLineEdit()
        self.home_page_input.setStyleSheet(f"border-radius: {BORDER_RADIUS}; padding: 6px; background-color: {DARK_MODE_ACCENT if self.parent.theme == 'Dark' else LIGHT_MODE_ACCENT}; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}; border: 1px solid {'#444' if self.parent.theme == 'Dark' else '#ccc'}")
        self.home_page_input.setFont(UI_FONT)
        self.home_page_input.setPlaceholderText("Enter your home page URL...")
        layout.addRow(QLabel("Home Page:").setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}"), self.home_page_input)

        self.search_engine_dropdown = QComboBox()
        self.search_engine_dropdown.setStyleSheet(f"border-radius: {BORDER_RADIUS}; padding: 6px; background-color: {DARK_MODE_ACCENT if self.parent.theme == 'Dark' else LIGHT_MODE_ACCENT}; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}; border: 1px solid {'#444' if self.parent.theme == 'Dark' else '#ccc'}")
        self.search_engine_dropdown.setFont(UI_FONT)
        self.search_engine_dropdown.addItems(["Lilo", "Mojeek", "Google", "Bing", "DuckDuckGo", "Yahoo", "Ecosia", "Qwant", "Brave", "SearchXNG"])
        layout.addRow(QLabel("Search Engine:").setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}"), self.search_engine_dropdown)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setStyleSheet(f"border-radius: {BORDER_RADIUS}; padding: 6px; background-color: {DARK_MODE_ACCENT if self.parent.theme == 'Dark' else LIGHT_MODE_ACCENT}; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}; border: 1px solid {'#444' if self.parent.theme == 'Dark' else '#ccc'}")
        self.theme_dropdown.setFont(UI_FONT)
        self.theme_dropdown.addItems(["Dark", "Light"])
        layout.addRow(QLabel("Theme:").setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}"), self.theme_dropdown)

    def setup_security_tab(self):
        layout = QFormLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.security_tab.setLayout(layout)

        self.javascript_checkbox = QCheckBox("Enable JavaScript")
        self.javascript_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.javascript_checkbox.setFont(UI_FONT)
        self.javascript_checkbox.setChecked(True)
        layout.addRow(self.javascript_checkbox)

        self.popup_checkbox = QCheckBox("Block Pop-ups")
        self.popup_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.popup_checkbox.setFont(UI_FONT)
        self.popup_checkbox.setChecked(True)
        layout.addRow(self.popup_checkbox)

        self.mixed_content_checkbox = QCheckBox("Block Mixed Content")
        self.mixed_content_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.mixed_content_checkbox.setFont(UI_FONT)
        self.mixed_content_checkbox.setChecked(True)
        layout.addRow(self.mixed_content_checkbox)

        self.dnt_checkbox = QCheckBox("Send Do Not Track")
        self.dnt_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.dnt_checkbox.setFont(UI_FONT)
        self.dnt_checkbox.setChecked(True)
        layout.addRow(self.dnt_checkbox)

        self.third_party_cookies_checkbox = QCheckBox("Block Third-Party Cookies")
        self.third_party_cookies_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.third_party_cookies_checkbox.setFont(UI_FONT)
        self.third_party_cookies_checkbox.setChecked(True)
        layout.addRow(self.third_party_cookies_checkbox)

        self.tracker_block_checkbox = QCheckBox("Block Trackers/Ads")
        self.tracker_block_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.tracker_block_checkbox.setFont(UI_FONT)
        self.tracker_block_checkbox.setChecked(False)
        layout.addRow(self.tracker_block_checkbox)

        self.clear_on_exit_checkbox = QCheckBox("Clear Data on Exit")
        self.clear_on_exit_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.clear_on_exit_checkbox.setFont(UI_FONT)
        layout.addRow(self.clear_on_exit_checkbox)

        self.private_browsing_checkbox = QCheckBox("Enable Private Browsing")
        self.private_browsing_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.private_browsing_checkbox.setFont(UI_FONT)
        layout.addRow(self.private_browsing_checkbox)

        self.https_only_checkbox = QCheckBox("Enforce HTTPS-Only")
        self.https_only_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.https_only_checkbox.setFont(UI_FONT)
        self.https_only_checkbox.setChecked(self.parent.privacy_engine.https_only)
        layout.addRow(self.https_only_checkbox)

        self.proxy_checkbox = QCheckBox("Enable Proxy")
        self.proxy_checkbox.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.proxy_checkbox.setFont(UI_FONT)
        self.proxy_checkbox.setChecked(True)
        layout.addRow(self.proxy_checkbox)

        self.proxy_dropdown = QComboBox()
        self.proxy_dropdown.setStyleSheet(f"border-radius: {BORDER_RADIUS}; padding: 6px; background-color: {DARK_MODE_ACCENT if self.parent.theme == 'Dark' else LIGHT_MODE_ACCENT}; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}; border: 1px solid {'#444' if self.parent.theme == 'Dark' else '#ccc'}")
        self.proxy_dropdown.setFont(UI_FONT)
        self.proxy_dropdown.addItem("Random Proxy")
        self.proxy_dropdown.addItems(self.parent.privacy_engine.proxy_list)
        layout.addRow(QLabel("Select Proxy:").setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}"), self.proxy_dropdown)

        self.clear_cookies_button = QPushButton("Clear Cookies")
        self.clear_cookies_button.setStyleSheet(self.parent.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_cookies_button.setFont(UI_FONT)
        self.clear_cookies_button.clicked.connect(self.clear_cookies)
        layout.addWidget(self.clear_cookies_button)

    def setup_data_management_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.data_management_tab.setLayout(layout)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.setStyleSheet(self.parent.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_cache_button.setFont(UI_FONT)
        self.clear_cache_button.clicked.connect(self.clear_cache)
        layout.addWidget(self.clear_cache_button)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.setStyleSheet(self.parent.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_history_button.setFont(UI_FONT)
        self.clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_history_button)

        self.cache_size_label = QLabel("Cache Size: Calculating...")
        self.cache_size_label.setStyleSheet(f"font-weight: bold; color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}")
        self.cache_size_label.setFont(UI_FONT)
        layout.addWidget(self.cache_size_label)

    def setup_about_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.about_tab.setLayout(layout)
        self.about_text = QTextEdit()
        self.about_text.setReadOnly(True)
        self.about_text.setStyleSheet(
            f"background-color: {DARK_MODE_ACCENT if self.parent.theme == 'Dark' else LIGHT_MODE_ACCENT}; "
            f"color: {DARK_MODE_TEXT if self.parent.theme == 'Dark' else LIGHT_MODE_TEXT}; "
            f"border-radius: {BORDER_RADIUS}; padding: 6px"
        )
        self.about_text.setFont(UI_FONT)
        self.about_text.setText(
            "Mojo Browser | v0.2.3 Beta\n\nDeveloped using PyQt5 & Python.\nFeatures:\n"
            "- Dark/Light themes\n- Multiple search engines\n- Enhanced security\n"
            "- Optional tracker blocking\n- Data management\n- Downloads\n- Proxy support\n- Anti-fingerprinting\n\n"
            "GitHub: https://Github.com/Muhammad-Noraeii\nhttps://Github.com/Guguss-31/"
        )
        layout.addWidget(self.about_text)

    def update_cache_size(self):
        try:
            profile = QWebEngineProfile.defaultProfile()
            size_mb = self.get_directory_size(profile.cachePath()) / (1024 * 1024)
            self.cache_size_label.setText(f"Cache Size: {size_mb:.2f} MB")
        except Exception as e:
            self.cache_size_label.setText(f"Cache Size: Error ({str(e)})")

    def get_directory_size(self, directory):
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(directory):
                for f in filenames:
                    total_size += os.path.getsize(os.path.join(dirpath, f))
        except Exception:
            pass
        return total_size

    def clear_cookies(self):
        try:
            self.parent.tabs.currentWidget().page().profile().clearHttpCache()
            self.parent.tabs.currentWidget().page().profile().clearAllVisitedLinks()
            QMessageBox.information(self.parent, "Cookies Cleared", "Cookies have been cleared.", QMessageBox.Ok, QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self.parent, "Error", f"Failed to clear cookies: {str(e)}", QMessageBox.Ok, QMessageBox.Ok)

    def clear_cache(self):
        QWebEngineProfile.defaultProfile().clearHttpCache()
        self.update_cache_size()
        QMessageBox.information(self.parent, "Cache Cleared", "Cache has been cleared.", QMessageBox.Ok, QMessageBox.Ok)

    def clear_history(self):
        self.parent.tabs.currentWidget().page().profile().clearAllVisitedLinks()
        self.parent.clear_history_data()

    def save_settings(self):
        self.parent.settings_persistence.privacy_settings.update({
            "do_not_track": self.dnt_checkbox.isChecked(),
            "block_third_party_cookies": self.third_party_cookies_checkbox.isChecked(),
            "clear_data_on_exit": self.clear_on_exit_checkbox.isChecked(),
            "private_browsing": self.private_browsing_checkbox.isChecked()
        })
        self.parent.privacy_engine.https_only = self.https_only_checkbox.isChecked()
        if self.proxy_checkbox.isChecked():
            selected_proxy = self.proxy_dropdown.currentText()
            if selected_proxy == "Random Proxy":
                self.parent.privacy_engine.set_random_proxy()
            else:
                self.parent.privacy_engine.set_random_proxy(specific_proxy=selected_proxy)
        else:
            self.parent.privacy_engine.proxy_settings = None
            self.parent.statusBar().showMessage("Proxy disabled", 5000)
        self.parent.privacy_engine.save_privacy_settings()
        self.parent.apply_settings(
            self.home_page_input.text(),
            self.search_engine_dropdown.currentText(),
            self.theme_dropdown.currentText(),
            self.javascript_checkbox.isChecked(),
            self.popup_checkbox.isChecked(),
            self.mixed_content_checkbox.isChecked()
        )
        self.accept()

    def apply_theme(self):
        theme = self.parent.theme
        dialog_background, text_color, input_background, input_border = (
            (DARK_MODE_BACKGROUND, DARK_MODE_TEXT, DARK_MODE_ACCENT, "#444") if theme == "Dark" 
            else (LIGHT_MODE_BACKGROUND, LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, "#ccc")
        )
        self.setStyleSheet(
            f"QDialog {{ background-color: {dialog_background}; color: {text_color}; border-radius: {BORDER_RADIUS}; }}"
            f"QLabel {{ color: {text_color}; }}"
            f"QLineEdit {{ background-color: {input_background}; color: {text_color}; border: 1px solid {input_border}; "
            f"border-radius: {BORDER_RADIUS}; padding: 6px; }}"
            f"QComboBox {{ background-color: {input_background}; color: {text_color}; border: 1px solid {input_border}; "
            f"border-radius: {BORDER_RADIUS}; padding: 6px; }}"
            f"QCheckBox {{ color: {text_color}; }}"
            f"QTextEdit {{ background-color: {input_background}; color: {text_color}; border: 1px solid {input_border}; "
            f"border-radius: {BORDER_RADIUS}; padding: 6px; }}"
            f"QPushButton {{ margin: 10px; }}"
        )
        self.save_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        self.clear_cache_button.setStyleSheet(self.parent.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_cookies_button.setStyleSheet(self.parent.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.clear_history_button.setStyleSheet(self.parent.get_button_style("#f44336", "#e57373", "#D32F2F"))
        self.tabs.setStyleSheet(self.get_tab_widget_style())

class PrivacyInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def interceptRequest(self, info):
        settings = self.parent.settings_persistence.privacy_settings
        if settings["block_third_party_cookies"]:
            info.setHttpHeader(b"Cookie", b"")
        if settings["do_not_track"]:
            info.setHttpHeader(b"DNT", b"1")

class MojoBrowser(QMainWindow):
    DEFAULT_HOME_PAGE = "https://mojox.org/search"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mojo Browser")
        self.setGeometry(100, 100, 1024, 768)
        self.setFont(UI_FONT)

        self.settings_persistence = SettingsPersistence(self)
        self.bookmarks = []
        self.history = []
        self.private_profile = None
        self.privacy_interceptor = PrivacyInterceptor(self)
        self.privacy_engine = initialize_privacy(self)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_tool_bar()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.tab_context_menu)
        self.tabs.setStyleSheet(self.get_tab_style())
        self.tabs.setFont(UI_FONT)
        self.layout.addWidget(self.tabs)

        self.settings_persistence.load_settings()
        self.add_new_tab(QUrl(self.home_page))

        self.status_bar = QStatusBar()
        self.status_bar.setFont(UI_FONT)
        self.setStatusBar(self.status_bar)

        self.setup_shortcuts()
        self.apply_styles()

        self.cache_timer = QTimer(self)
        self.cache_timer.timeout.connect(self.update_cache_size_periodic)
        self.cache_timer.start(60000)

    def get_tab_style(self):
        theme = self.theme
        tab_text_color, tab_background_color, tab_selected_background = (
            (DARK_MODE_TEXT, DARK_MODE_ACCENT, DARK_MODE_BACKGROUND) if theme == "Dark" 
            else (LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, LIGHT_MODE_BACKGROUND)
        )
        return (
            "QTabBar::close-button { image: url('icons/close_tab.png'); }"
            f"QTabWidget::pane {{ border: none; border-radius: {BORDER_RADIUS}; "
            f"background-color: {DARK_MODE_BACKGROUND if theme == 'Dark' else LIGHT_MODE_BACKGROUND}; }}"
            f"QTabBar::tab {{ background-color: {tab_background_color}; color: {tab_text_color}; "
            f"border: 1px solid {'#444' if theme == 'Dark' else '#bbb'}; border-bottom: none; padding: 8px 16px; "
            f"border-top-left-radius: {BORDER_RADIUS}; border-top-right-radius: {BORDER_RADIUS}; }}"
            f"QTabBar::tab:selected {{ background: {tab_selected_background}; border-bottom: 2px solid {PRIMARY_COLOR}; }}"
            "QTabBar::tab:!selected {{ margin-top: 2px; }}"
            f"QTabBar::tab:hover {{ background: {'#e0e0e0' if theme == 'Light' else '#3a3a3a'}; }}"
            "QTabWidget::tab-bar {{ alignment: center; }}"
        )

    def get_statusbar_style(self):
        theme = self.theme
        return (
            f"QStatusBar {{ background-color: {DARK_MODE_BACKGROUND if theme == 'Dark' else LIGHT_MODE_BACKGROUND}; "
            f"color: {DARK_MODE_TEXT if theme == 'Dark' else LIGHT_MODE_TEXT}; border: none; border-radius: {BORDER_RADIUS}; padding: 6px; }}"
        )

    def get_button_style(self, background_color, hover_color, pressed_color):
        text_color = DARK_MODE_TEXT if self.theme == "Dark" else LIGHT_MODE_TEXT
        return (
            f"QPushButton {{ background-color: {background_color}; color: {text_color}; "
            f"border: none; border-radius: {BUTTON_BORDER_RADIUS}; padding: 10px 18px; min-width: 60px; min-height: 36px; }}"
            f"QPushButton:hover {{ background-color: {hover_color}; opacity: 0.9; }}"
            f"QPushButton:pressed {{ background-color: {pressed_color}; }}"
        )

    def create_tool_bar(self):
        self.tool_bar = QToolBar("Navigation", self)
        self.addToolBar(self.tool_bar)
        self.tool_bar.setIconSize(QSize(32, 32))
        self.tool_bar.setFont(UI_FONT)
        self.tool_bar.setStyleSheet(self.get_toolbar_style())

        actions = [
            (QIcon("icons/back.png") if os.path.exists("icons/back.png") else QIcon.fromTheme("go-previous"), 
             "Back", "Go to previous page", self.browser_back),
            (QIcon("icons/forward.png") if os.path.exists("icons/forward.png") else QIcon.fromTheme("go-next"), 
             "Forward", "Go to next page", self.browser_forward),
            (QIcon.fromTheme("view-refresh"), "Reload", "Reload page", self.browser_reload),
            (QIcon.fromTheme("process-stop"), "Stop", "Stop loading", self.browser_stop),
            (QIcon("icons/home.png") if os.path.exists("icons/home.png") else QIcon.fromTheme("go-home"), 
             "Home", "Go to homepage", self.go_home),
            (QIcon.fromTheme("zoom-in"), "Zoom In", "Increase zoom", self.zoom_in),
            (QIcon.fromTheme("zoom-out"), "Zoom Out", "Decrease zoom", self.zoom_out),
            (QIcon.fromTheme("view-fullscreen"), "Fullscreen", "Toggle fullscreen", self.toggle_fullscreen),
        ]
        for icon, text, tip, connect in actions:
            action = QAction(icon, text, self)
            action.setStatusTip(tip)
            action.setFont(UI_FONT)
            action.triggered.connect(connect)
            self.tool_bar.addAction(action)

        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet(self.get_addressbar_style())
        self.address_bar.setFont(UI_FONT)
        self.address_bar.returnPressed.connect(self.load_page)
        self.tool_bar.addWidget(self.address_bar)

        go_action = QAction(QIcon("icons/search.png") if os.path.exists("icons/search.png") else QIcon.fromTheme("go-jump"), 
                            "Go", self)
        go_action.setStatusTip("Go to address or search")
        go_action.setFont(UI_FONT)
        go_action.triggered.connect(self.load_page)
        self.tool_bar.addAction(go_action)

        self.tool_bar.addWidget(QWidget().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        additional_actions = [
            (QIcon("icons/new_tab.png") if os.path.exists("icons/new_tab.png") else QIcon.fromTheme("document-new"), 
             "New Tab", "Open new tab", self.add_new_tab),
            (QIcon.fromTheme("emblem-favorite"), "Bookmark", "Bookmark page", self.settings_persistence.add_bookmark),
            (QIcon.fromTheme("bookmarks"), "Bookmarks", "View bookmarks", self.settings_persistence.view_bookmarks),
            (QIcon.fromTheme("document-open-recent"), "History", "View history", self.settings_persistence.view_history),
            (QIcon("icons/settings.png") if os.path.exists("icons/settings.png") else QIcon.fromTheme("preferences-system"), 
             "Settings", "Open settings", self.open_settings),
        ]
        for icon, text, tip, connect in additional_actions:
            action = QAction(icon, text, self)
            action.setStatusTip(tip)
            action.setFont(UI_FONT)
            action.triggered.connect(connect)
            self.tool_bar.addAction(action)

    def get_toolbar_style(self):
        theme = self.theme
        toolbar_background = DARK_MODE_BACKGROUND if theme == "Dark" else LIGHT_MODE_BACKGROUND
        text_color = DARK_MODE_TEXT if theme == "Dark" else LIGHT_MODE_TEXT
        return (
            f"QToolBar {{ background-color: {toolbar_background}; "
            f"color: {text_color}; border: none; padding: 8px; "
            f"border-radius: {BORDER_RADIUS}; spacing: 8px; }}"
            f"QToolButton {{ background-color: {PRIMARY_COLOR}; "
            f"color: {text_color}; border: none; margin: 2px; "
            f"border-radius: {BUTTON_BORDER_RADIUS}; padding: 10px; }}"
            f"QToolButton:hover {{ background-color: {BUTTON_HOVER_COLOR}; opacity: 0.9; }}"
            f"QToolButton:pressed {{ background-color: {BUTTON_PRESSED_COLOR}; }}"
        )

    def get_addressbar_style(self):
        theme = self.theme
        background_color = DARK_MODE_ACCENT if theme == "Dark" else LIGHT_MODE_ACCENT
        text_color = DARK_MODE_TEXT if theme == "Dark" else LIGHT_MODE_TEXT
        border_color = "#444" if theme == "Dark" else "#ccc"
        return (
            f"QLineEdit {{ background-color: {background_color}; "
            f"color: {text_color}; "
            f"border: 1px solid {border_color}; border-radius: {BORDER_RADIUS}; "
            f"padding: 8px; font-size: 14px; }}"
        )

    def apply_styles(self):
        theme = self.theme
        main_background, main_text_color, input_background, input_border, list_background, list_text_color, list_selected_background = (
            (DARK_MODE_BACKGROUND, DARK_MODE_TEXT, DARK_MODE_ACCENT, "#444", DARK_MODE_ACCENT, DARK_MODE_TEXT, "#555") if theme == "Dark" 
            else (LIGHT_MODE_BACKGROUND, LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, "#ccc", LIGHT_MODE_ACCENT, LIGHT_MODE_TEXT, "#e0e0e0")
        )
        app_stylesheet = (
            f"QMainWindow {{ background-color: {main_background}; color: {main_text_color}; border-radius: {BORDER_RADIUS}; }}"
            f"QToolBar {{ background-color: {main_background}; color: {main_text_color}; border: none; border-radius: {BORDER_RADIUS}; }}"
            "QToolBar::handle {{ background: transparent; border: none; }}"
            f"QLineEdit {{ background-color: {input_background}; color: {main_text_color}; border: 1px solid {input_border}; "
            f"border-radius: {BORDER_RADIUS}; padding: 8px; }}"
            f"QPushButton, QAction {{ background-color: {PRIMARY_COLOR}; "
            f"color: {main_text_color}; "
            f"border: 1px solid {'#555' if theme == 'Dark' else '#bbb'}; border-radius: {BUTTON_BORDER_RADIUS}; "
            f"padding: 10px 18px; min-width: 60px;}}"
            f"QPushButton:hover, QAction:hover {{ background-color: {BUTTON_HOVER_COLOR}; opacity: 0.9; }}"
            f"QPushButton:pressed, QAction:pressed {{ background-color: {BUTTON_PRESSED_COLOR}; }}"
            f"QStatusBar {{ background-color: {main_background}; color: {main_text_color}; border: none; border-radius: {BORDER_RADIUS}; }}"
            f"QListWidget {{ background-color: {list_background}; color: {list_text_color}; border: 1px solid {input_border}; "
            f"border-radius: {BORDER_RADIUS}; padding: 8px; font-size: 14px; }}"
            "QListWidget::item {{ padding: 8px; }}"
            f"QListWidget::item:selected {{ background-color: {list_selected_background}; }}"
            f"QTextEdit {{ background-color: {input_background}; color: {main_text_color}; border: 1px solid {input_border}; "
            f"border-radius: {BORDER_RADIUS}; padding: 8px; }}"
        )
        self.setStyleSheet(app_stylesheet)
        self.tabs.setStyleSheet(self.get_tab_style())
        self.statusBar().setStyleSheet(self.get_statusbar_style())
        self.tool_bar.setStyleSheet(self.get_toolbar_style())
        self.address_bar.setStyleSheet(self.get_addressbar_style())
        if hasattr(self, 'settings_dialog') and self.settings_dialog:
            self.settings_dialog.apply_theme()

    def add_new_tab(self, url=None):
        browser = QWebEngineView(self) if self.settings_persistence.privacy_settings["private_browsing"] else QWebEngineView()
        if self.settings_persistence.privacy_settings["private_browsing"]:
            if not self.private_profile:
                self.private_profile = QWebEngineProfile("PrivateProfile", self)
                self.private_profile.setCachePath("")
                self.private_profile.setPersistentStoragePath("")
            page = PrivacyPage(self.private_profile, browser)
            page.setPrivacyEngine(self.privacy_engine)
            browser.setPage(page)
        else:
            page = PrivacyPage(QWebEngineProfile.defaultProfile(), browser)
            page.setPrivacyEngine(self.privacy_engine)
            browser.setPage(page)

        self.apply_webengine_settings(browser)
        browser.setUrl(url or QUrl(self.home_page))
        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda u, b=browser: (self.update_tab_title(b, u), self.update_history(u), self.update_address_bar(i)))
        browser.loadStarted.connect(lambda: self.statusBar().showMessage("Loading..."))
        browser.loadFinished.connect(lambda ok, b=browser: self.load_finished(ok, b))
        self.download_handler = DownloadHandler(browser)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def update_tab_title(self, browser, url):
        index = self.tabs.indexOf(browser)
        title = browser.page().title() or "New Tab"
        self.tabs.setTabText(index, title[:30] + "..." if len(title) > 30 else title)

    def update_address_bar(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.address_bar.setText(browser.url().toString())

    def load_page(self):
        url = self.address_bar.text().strip()
        browser = self.tabs.currentWidget()
        if not url:
            return
        if re.match(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$', url):
            browser.setUrl(QUrl(url if url.startswith(('http://', 'https://')) else f"https://{url}"))
        elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', url):
            browser.setUrl(QUrl(f"http://{url}"))
        else:
            browser.setUrl(QUrl(self.get_search_url(url)))

    def get_search_url(self, query):
        search_engines = {
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Yahoo": "https://search.yahoo.com/search?p=",
            "Ecosia": "https://www.ecosia.org/search?method=index&q=",
            "Qwant": "https://www.qwant.com/?q=",
            "Lilo": "https://search.lilo.org/?q=",
            "Brave": "https://search.brave.com/search?q=",
            "Mojeek": "https://www.mojeek.com/search?q=",
            "SearchXNG": "https://search.inetol.net/search?q="
        }
        return f"{search_engines.get(self.search_engine, search_engines['Google'])}{query.replace(' ', '+')}"

    def browser_back(self):
        browser = self.tabs.currentWidget()
        if browser.history().canGoBack():
            browser.back()

    def browser_forward(self):
        browser = self.tabs.currentWidget()
        if browser.history().canGoForward():
            browser.forward()

    def browser_reload(self):
        self.tabs.currentWidget().reload()

    def browser_stop(self):
        self.tabs.currentWidget().stop()

    def go_home(self):
        self.tabs.currentWidget().setUrl(QUrl(self.home_page))

    def zoom_in(self):
        browser = self.tabs.currentWidget()
        browser.setZoomFactor(min(browser.zoomFactor() + 0.1, 2.0))

    def zoom_out(self):
        browser = self.tabs.currentWidget()
        browser.setZoomFactor(max(browser.zoomFactor() - 0.1, 0.5))

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+T", self.add_new_tab),
            ("Ctrl+W", lambda: self.close_tab(self.tabs.currentIndex())),
            ("Ctrl+R", self.browser_reload),
            ("Ctrl+H", self.settings_persistence.view_history),
            ("Ctrl+B", self.settings_persistence.view_bookmarks),
            ("Ctrl+Q", self.close),
            ("Ctrl+=", self.zoom_in),
            ("Ctrl+-", self.zoom_out),
            ("F11", self.toggle_fullscreen)
        ]
        for key, func in shortcuts:
            shortcut = QAction(self)
            shortcut.setShortcut(QKeySequence(key))
            shortcut.triggered.connect(func)
            self.addAction(shortcut)

    def tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index == -1:
            return
        menu = QMenu(self)
        menu.setFont(UI_FONT)
        rename_action = menu.addAction("Rename Tab")
        close_action = menu.addAction("Close Tab")
        action = menu.exec_(self.tabs.mapToGlobal(pos))
        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new tab name:")
            if ok and new_name:
                self.tabs.setTabText(index, new_name)
        elif action == close_action:
            self.close_tab(index)

    def load_finished(self, ok, browser):
        self.statusBar().clearMessage()
        if not ok:
            self.statusBar().showMessage("Failed to load page", 3000)

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.setParent(self)
        settings = self.settings_persistence.privacy_settings
        self.settings_dialog.home_page_input.setText(self.home_page)
        self.settings_dialog.search_engine_dropdown.setCurrentText(self.search_engine)
        self.settings_dialog.theme_dropdown.setCurrentText(self.theme)
        self.settings_dialog.javascript_checkbox.setChecked(self.javascript_enabled)
        self.settings_dialog.popup_checkbox.setChecked(self.block_popups)
        self.settings_dialog.mixed_content_checkbox.setChecked(self.block_mixed_content)
        self.settings_dialog.dnt_checkbox.setChecked(settings["do_not_track"])
        self.settings_dialog.third_party_cookies_checkbox.setChecked(settings["block_third_party_cookies"])
        self.settings_dialog.clear_on_exit_checkbox.setChecked(settings["clear_data_on_exit"])
        self.settings_dialog.private_browsing_checkbox.setChecked(settings["private_browsing"])
        self.settings_dialog.exec_()

    def apply_settings(self, home_page, search_engine, theme, javascript_enabled, block_popups, block_mixed_content):
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
            if self.settings_persistence.privacy_settings["do_not_track"]:
                browser.page().profile().setHttpUserAgent("MojoBrowser/0.2 (Privacy Enhanced)")

    def apply_webengine_settings(self, browser):
        settings = browser.settings()
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(settings.WebAttribute.JavascriptCanOpenWindows, not self.block_popups)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, not self.block_mixed_content)
        profile = browser.page().profile()
        profile.setUrlRequestInterceptor(self.privacy_engine)
        self.privacy_engine.apply_proxy(profile)

    def update_history(self, url):
        self.settings_persistence.update_history(url)

    def clear_history_data(self):
        self.history.clear()
        self.settings_persistence.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.", QMessageBox.Ok, QMessageBox.Ok)

    def update_cache_size_periodic(self):
        if hasattr(self, 'settings_dialog') and self.settings_dialog.isVisible():
            self.settings_dialog.update_cache_size()

    def closeEvent(self, event):
        if self.settings_persistence.privacy_settings["clear_data_on_exit"]:
            self.settings_persistence.clear_all_private_data()
        super().closeEvent(event)

class SettingsPersistence:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"
        self.bookmarks_file = "bookmarks.json"
        self.history_file = "history.json"
        self.privacy_settings = {
            "do_not_track": True,
            "block_third_party_cookies": True,
            "block_trackers": False, 
            "clear_data_on_exit": False,
            "private_browsing": False
        }
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
                self.privacy_settings.update(settings.get("privacy_settings", {}))
        else:
            self.parent.home_page = self.parent.DEFAULT_HOME_PAGE
            self.parent.search_engine = "Google"
            self.parent.theme = "Dark"
            self.parent.javascript_enabled = True
            self.parent.block_popups = True
            self.parent.block_mixed_content = True

    def save_settings(self):
        with open(self.settings_file, "w") as file:
            json.dump({
                "home_page": self.parent.home_page,
                "search_engine": self.parent.search_engine,
                "theme": self.parent.theme,
                "javascript_enabled": self.parent.javascript_enabled,
                "block_popups": self.parent.block_popups,
                "block_mixed_content": self.parent.block_mixed_content,
                "privacy_settings": self.privacy_settings
            }, file)

    def load_bookmarks(self):
        self.parent.bookmarks = json.load(open(self.bookmarks_file, "r")) if os.path.exists(self.bookmarks_file) else []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as file:
            json.dump(self.parent.bookmarks, file)

    def add_bookmark(self):
        browser = self.parent.tabs.currentWidget()
        current_url = browser.url().toString()
        if current_url not in self.parent.bookmarks:
            self.parent.bookmarks.append(current_url)
            self.save_bookmarks()
            QMessageBox.information(self.parent, "Bookmark Added", f"Bookmarked: {current_url}", QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.information(self.parent, "Bookmark Exists", "This URL is already bookmarked.", QMessageBox.Ok, QMessageBox.Ok)

    def view_bookmarks(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Bookmarks")
        dialog.setGeometry(300, 300, 400, 300)
        dialog.setFont(UI_FONT)
        layout = QVBoxLayout(dialog)
        bookmark_list = QListWidget()
        theme = self.parent.theme
        list_background, list_text_color, list_selected_background = (
            (DARK_MODE_ACCENT, DARK_MODE_TEXT, "#555") if theme == "Dark" else (LIGHT_MODE_ACCENT, LIGHT_MODE_TEXT, "#e0e0e0")
        )
        bookmark_list.setStyleSheet(
            f"QListWidget {{ background-color: {list_background}; color: {list_text_color}; "
            f"border: 1px solid {'#444' if theme == 'Dark' else '#ccc'}; border-radius: {BORDER_RADIUS}; "
            "padding: 8px; font-size: 14px; }}"
            "QListWidget::item {{ padding: 8px; }}"
            f"QListWidget::item:selected {{ background-color: {list_selected_background}; }}"
        )
        bookmark_list.setFont(UI_FONT)
        bookmark_list.addItems(self.parent.bookmarks)
        bookmark_list.itemDoubleClicked.connect(lambda item: self.parent.tabs.currentWidget().setUrl(QUrl(item.text())))
        layout.addWidget(bookmark_list)
        
        close_button = QPushButton("Close")
        close_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        close_button.setFont(UI_FONT)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec_()

    def load_history(self):
        self.parent.history = json.load(open(self.history_file, "r")) if os.path.exists(self.history_file) else []

    def save_history(self):
        with open(self.history_file, "w") as file:
            json.dump(self.parent.history, file)

    def update_history(self, url):
        url_str = url.toString()
        if url_str and url_str not in self.parent.history:
            self.parent.history.append(url_str)
            self.save_history()

    def view_history(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("History")
        dialog.setGeometry(300, 300, 400, 300)
        dialog.setFont(UI_FONT)
        layout = QVBoxLayout(dialog)
        history_list = QListWidget()
        theme = self.parent.theme
        list_background, list_text_color, list_selected_background = (
            (DARK_MODE_ACCENT, DARK_MODE_TEXT, "#555") if theme == "Dark" else (LIGHT_MODE_ACCENT, LIGHT_MODE_TEXT, "#e0e0e0")
        )
        history_list.setStyleSheet(
            f"QListWidget {{ background-color: {list_background}; color: {list_text_color}; "
            f"border: 1px solid {'#444' if theme == 'Dark' else '#ccc'}; border-radius: {BORDER_RADIUS}; "
            "padding: 8px; font-size: 14px; }}"
            "QListWidget::item {{ padding: 8px; }}"
            f"QListWidget::item:selected {{ background-color: {list_selected_background}; }}"
        )
        history_list.setFont(UI_FONT)
        history_list.addItems(self.parent.history)
        history_list.itemDoubleClicked.connect(lambda item: self.parent.tabs.currentWidget().setUrl(QUrl(item.text())))
        layout.addWidget(history_list)
        
        clear_history_button = QPushButton("Clear History")
        clear_history_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        clear_history_button.setFont(UI_FONT)
        clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_button)
        
        close_button = QPushButton("Close")
        close_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        close_button.setFont(UI_FONT)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec_()

    def clear_history(self):
        self.parent.history.clear()
        self.save_history()
        QMessageBox.information(self.parent, "History Cleared", "Browsing history has been cleared.", QMessageBox.Ok, QMessageBox.Ok)

    def clear_all_private_data(self):
        self.clear_history()
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        profile.clearAllVisitedLinks()
        self.parent.bookmarks.clear()
        self.save_bookmarks()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(UI_FONT)
    browser = MojoBrowser()
    browser.show()
    sys.exit(app.exec_())