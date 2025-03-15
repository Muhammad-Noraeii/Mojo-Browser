import sys
import json
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QDialog, QFormLayout, QTabWidget, QTextEdit, QCheckBox,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QToolBar, QStatusBar,
    QAction, QStyle, QSizePolicy, QSpacerItem, QScrollArea, QInputDialog, QMenu, QSystemTrayIcon,
    QProgressBar, QDialogButtonBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings, QWebEngineDownloadItem
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, Qt, QSize, QTimer, QEvent, QRect, QDir
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPalette, QColor, QDesktopServices
import requests

from addon import ExtensionManager
from MojoPrivacy import PrivacyEngine, PrivacyPage, initialize_privacy

PRIMARY_COLOR = "#3B82F6"
SECONDARY_COLOR = "#475569"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#F59E0B"
BACKGROUND_COLOR = "#F3F4F6"
DARK_MODE_BACKGROUND = "#111827"
DARK_MODE_TEXT = "#D1D5DB"
DARK_MODE_ACCENT = "#1F2A44"
LIGHT_MODE_BACKGROUND = "#FFFFFF"
LIGHT_MODE_TEXT = "#1F2937"
LIGHT_MODE_ACCENT = "#F3F4F6"
BORDER_RADIUS = "8px"
BUTTON_BORDER_RADIUS = "5px"
BUTTON_HOVER_COLOR = "#60A5FA"
BUTTON_PRESSED_COLOR = "#2563EB"

UI_FONT = QFont("Nunito", 13)
FALLBACK_FONT = QFont("Arial", 13)

class ExtensionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Extensions")
        self.setGeometry(300, 300, 450, 350)
        self.setFont(UI_FONT)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self.extensions_list = QListWidget()
        self.extensions_list.setStyleSheet(self.parent.get_list_style())
        self.parent.extension_manager.load_extensions()
        for ext_name in self.parent.extension_manager.extensions.keys():
            item = QListWidgetItem(ext_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if self.parent.extension_manager.extension_status.get(ext_name) == 'enabled' else Qt.Unchecked)
            self.extensions_list.addItem(item)
        layout.addWidget(self.extensions_list)

        buttons_layout = QHBoxLayout()
        enable_button = QPushButton("Enable")
        enable_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        enable_button.clicked.connect(self.enable_selected_extension)
        disable_button = QPushButton("Disable")
        disable_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        disable_button.clicked.connect(self.disable_selected_extension)
        download_button = QPushButton("Download")
        download_button.setStyleSheet(self.parent.get_button_style(ACCENT_COLOR, "#FBBF24", "#D97706"))
        download_button.clicked.connect(self.download_extension)
        store_button = QPushButton("Get from MojoX")
        store_button.setStyleSheet(self.parent.get_button_style(ACCENT_COLOR, "#FBBF24", "#D97706"))
        store_button.clicked.connect(self.fetch_store_extensions)
        buttons_layout.addWidget(enable_button)
        buttons_layout.addWidget(disable_button)
        buttons_layout.addWidget(download_button)
        buttons_layout.addWidget(store_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        close_button = QPushButton("Close")
        close_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def enable_selected_extension(self):
        selected = self.extensions_list.currentItem()
        if selected and selected.checkState() != Qt.Checked:
            ext_name = selected.text()
            self.parent.extension_manager.enable_extension(ext_name)
            selected.setCheckState(Qt.Checked)

    def disable_selected_extension(self):
        selected = self.extensions_list.currentItem()
        if selected and selected.checkState() == Qt.Checked:
            ext_name = selected.text()
            self.parent.extension_manager.disable_extension(ext_name)
            selected.setCheckState(Qt.Unchecked)

    def download_extension(self):
        url, ok = QInputDialog.getText(self, "Download Extension", "Enter the URL of the .js extension:")
        if ok and url:
            ext_name = self.parent.extension_manager.download_extension(url)
            if ext_name:
                item = QListWidgetItem(ext_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.extensions_list.addItem(item)
            else:
                QMessageBox.warning(self, "Download Failed", "Failed to download the extension.", QMessageBox.Ok)

    def fetch_store_extensions(self):
        extensions = self.parent.extension_manager.fetch_store_extensions()
        if not extensions:
            QMessageBox.warning(self, "Fetch Failed", "Failed to fetch extensions from the store.", QMessageBox.Ok)
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("MojoX Extension Store")
        dialog.setGeometry(300, 300, 600, 400)
        layout = QVBoxLayout()

        store_list = QListWidget()
        store_list.setSpacing(6)

        for ext in extensions:
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(6, 6, 6, 6)

            text_widget = QWidget()
            text_layout = QVBoxLayout()
            name_label = QLabel(ext["name"])
            name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            desc_label = QLabel(ext["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 12px;")
            author_label = QLabel(f"By: {ext['author']}")
            author_label.setStyleSheet("font-size: 10px; color: #888;")
            text_layout.addWidget(name_label)
            text_layout.addWidget(desc_label)
            text_layout.addWidget(author_label)
            text_widget.setLayout(text_layout)
            item_layout.addWidget(text_widget)

            checkbox = QCheckBox()
            item_layout.addWidget(checkbox)

            item_widget.setLayout(item_layout)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, ext["url"])
            item.setData(Qt.UserRole + 1, ext["name"])
            store_list.addItem(item)
            store_list.setItemWidget(item, item_widget)

        layout.addWidget(store_list)

        download_button = QPushButton("Download Selected")
        download_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        download_button.clicked.connect(lambda: self.download_selected_extensions(store_list, dialog))
        layout.addWidget(download_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def download_selected_extensions(self, store_list, dialog):
        for i in range(store_list.count()):
            item = store_list.item(i)
            checkbox = store_list.itemWidget(item).findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                url = item.data(Qt.UserRole)
                ext_name = self.parent.extension_manager.download_extension(url)
                if ext_name:
                    list_item = QListWidgetItem(ext_name)
                    list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                    list_item.setCheckState(Qt.Unchecked)
                    self.extensions_list.addItem(list_item)
        dialog.accept()

    def close_dialog(self):
        for i in range(self.extensions_list.count()):
            item = self.extensions_list.item(i)
            ext_name = item.text()
            is_enabled = item.checkState() == Qt.Checked
            if is_enabled:
                self.parent.extension_manager.enable_extension(ext_name)
            else:
                self.parent.extension_manager.disable_extension(ext_name)
        self.accept()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 700, 600)
        self.setFont(UI_FONT)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self.get_tab_widget_style())
        self.tabs.setFont(UI_FONT)
        self.general_tab = QWidget()
        self.security_tab = QWidget()
        self.data_management_tab = QWidget()
        self.performance_tab = QWidget()
        self.about_tab = QWidget()

        self.tabs.addTab(self.general_tab, QIcon("icons/general.png") if os.path.exists("icons/general.png") else QIcon.fromTheme("preferences-desktop"), "General")
        self.tabs.addTab(self.security_tab, "Security")
        self.tabs.addTab(self.data_management_tab, "Data Management")
        self.tabs.addTab(self.performance_tab, "Performance")
        self.tabs.addTab(self.about_tab, "About Us")

        self.setup_general_tab()
        self.setup_security_tab()
        self.setup_data_management_tab()
        self.setup_performance_tab()
        self.setup_about_tab()

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(self.parent.get_button_style(SECONDARY_COLOR, "#6B7280", "#374151"))
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.layout.addLayout(self.button_layout)
        self.layout.setSpacing(12)
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
            f"background-color: {tab_selected_background}; padding: 12px; }}"
            f"QTabBar::tab {{ background-color: {tab_background_color}; color: {tab_text_color}; "
            f"border: 1px solid {'#4B5563' if theme == 'Dark' else '#D1D5DB'}; border-bottom: none; "
            f"padding: 12px 24px; border-top-left-radius: {BORDER_RADIUS}; "
            f"border-top-right-radius: {BORDER_RADIUS}; margin-right: 2px; font-weight: 500; font-size: 14px; }}"
            f"QTabBar::tab:selected {{ background: {tab_selected_background}; "
            f"border-bottom: 3px solid {PRIMARY_COLOR}; font-weight: bold; }}"
            "QTabBar::tab:!selected {{ margin-top: 3px; }}"
            f"QTabBar::tab:hover {{ background: {'#374151' if theme == 'Dark' else '#E5E7EB'}; }}"
            "QTabWidget::tab-bar {{ alignment: center; }}"
        )

    def setup_general_tab(self):
        layout = QFormLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.general_tab.setLayout(layout)

        self.home_page_input = QLineEdit()
        self.home_page_input.setStyleSheet(self.parent.get_input_style())
        self.home_page_input.setPlaceholderText("Enter your home page URL...")
        layout.addRow(QLabel("Home Page:").setStyleSheet(self.parent.get_label_style()), self.home_page_input)

        self.search_engine_dropdown = QComboBox()
        self.search_engine_dropdown.setStyleSheet(self.parent.get_input_style())
        self.search_engine_dropdown.addItems(["Lilo", "Mojeek", "Google", "Bing", "DuckDuckGo", "Yahoo", "Ecosia", "Qwant", "Brave", "SearchXNG"])
        layout.addRow(QLabel("Search Engine:").setStyleSheet(self.parent.get_label_style()), self.search_engine_dropdown)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setStyleSheet(self.parent.get_input_style())
        self.theme_dropdown.addItems(["Dark", "Light", "System"])
        self.theme_dropdown.currentTextChanged.connect(self.preview_theme)
        layout.addRow(QLabel("Theme:").setStyleSheet(self.parent.get_label_style()), self.theme_dropdown)

        self.new_tab_behavior = QComboBox()
        self.new_tab_behavior.setStyleSheet(self.parent.get_input_style())
        self.new_tab_behavior.addItems(["Home Page", "Blank Page", "Last Page"])
        layout.addRow(QLabel("New Tab Opens:").setStyleSheet(self.parent.get_label_style()), self.new_tab_behavior)

    def setup_security_tab(self):
        layout = QFormLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.security_tab.setLayout(layout)

        checkboxes = [
            ("javascript_checkbox", "Enable JavaScript", True),
            ("popup_checkbox", "Block Pop-ups", True),
            ("mixed_content_checkbox", "Block Mixed Content", True),
            ("dnt_checkbox", "Send Do Not Track", True),
            ("third_party_cookies_checkbox", "Block Third-Party Cookies", True),
            ("tracker_block_checkbox", "Block Trackers/Ads", False),
            ("clear_on_exit_checkbox", "Clear Data on Exit", False),
            ("private_browsing_checkbox", "Enable Private Browsing", False),
            ("https_only_checkbox", "Enforce HTTPS-Only", self.parent.privacy_engine.https_only),
            ("proxy_checkbox", "Enable Proxy", True),
            ("fingerprint_protection", "Enable Fingerprint Protection", False)
        ]
        
        for name, text, default in checkboxes:
            checkbox = QCheckBox(text)
            checkbox.setStyleSheet(self.parent.get_checkbox_style())
            checkbox.setChecked(default)
            setattr(self, name, checkbox)
            layout.addRow(checkbox)

        self.proxy_dropdown = QComboBox()
        self.proxy_dropdown.setStyleSheet(self.parent.get_input_style())
        self.proxy_dropdown.addItem("Random Proxy")
        self.proxy_dropdown.addItems(self.parent.privacy_engine.proxy_list)
        layout.addRow(QLabel("Select Proxy:").setStyleSheet(self.parent.get_label_style()), self.proxy_dropdown)

        self.clear_cookies_button = QPushButton("Clear Cookies")
        self.clear_cookies_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        self.clear_cookies_button.clicked.connect(self.clear_cookies)
        layout.addWidget(self.clear_cookies_button)

    def setup_data_management_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.data_management_tab.setLayout(layout)

        buttons = [
            ("clear_cache_button", "Clear Cache", self.clear_cache),
            ("clear_history_button", "Clear History", self.clear_history),
            ("clear_all_data_button", "Clear All Data", self.clear_all_data)
        ]
        
        for name, text, handler in buttons:
            button = QPushButton(text)
            button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
            button.clicked.connect(handler)
            setattr(self, name, button)
            layout.addWidget(button)

        self.cache_size_label = QLabel("Cache Size: Calculating...")
        self.cache_size_label.setStyleSheet(self.parent.get_label_style())
        layout.addWidget(self.cache_size_label)
        
        auto_clear_layout = QHBoxLayout()
        auto_clear_label = QLabel("Auto-clear interval:")
        auto_clear_label.setStyleSheet(self.parent.get_label_style())
        self.auto_clear_interval = QComboBox()
        self.auto_clear_interval.setStyleSheet(self.parent.get_input_style())
        self.auto_clear_interval.addItems(["Never", "Daily", "Weekly", "Monthly"])
        auto_clear_layout.addWidget(auto_clear_label)
        auto_clear_layout.addWidget(self.auto_clear_interval)
        layout.addLayout(auto_clear_layout)
        
        layout.addStretch()

    def setup_performance_tab(self):
        layout = QFormLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.performance_tab.setLayout(layout)

        self.hardware_acceleration = QCheckBox("Enable Hardware Acceleration")
        self.hardware_acceleration.setStyleSheet(self.parent.get_checkbox_style())
        self.hardware_acceleration.setChecked(True)
        layout.addRow(self.hardware_acceleration)

        self.preload_pages = QCheckBox("Preload Pages for Faster Browsing")
        self.preload_pages.setStyleSheet(self.parent.get_checkbox_style())
        layout.addRow(self.preload_pages)

        self.cache_size_limit = QComboBox()
        self.cache_size_limit.setStyleSheet(self.parent.get_input_style())
        self.cache_size_limit.addItems(["50 MB", "100 MB", "250 MB", "500 MB", "Unlimited"])
        layout.addRow(QLabel("Cache Size Limit:").setStyleSheet(self.parent.get_label_style()), self.cache_size_limit)

    def setup_about_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.about_tab.setLayout(layout)
        
        self.about_text = QTextEdit()
        self.about_text.setReadOnly(True)
        self.about_text.setStyleSheet(self.parent.get_input_style())
        self.about_text.setText(
            "Mojo Browser | v0.2.5 Alpha\n\n"
            "Developed using PyQt5 & Python.\nEnhanced Features:\n"
            "- Dark/Light/System themes\n- Multiple search engines\n- Advanced security options\n"
            "- Performance optimizations\n- Proxy & fingerprint protection\n"
            "- System tray integration\n- Improved UI/UX\n- JavaScript extension support from mojox.org\n"
            "** Mojo Browser ** : an idea by Muhammad Noraeii"
            "\n"
            "GitHub: https://Github.com/Muhammad-Noraeii\nhttps://Github.com/Guguss-31/"
        )
        layout.addWidget(self.about_text)

    def preview_theme(self, theme):
        temp_theme = theme if theme != "System" else ("Dark" if QApplication.palette().color(QPalette.Window).lightness() < 128 else "Light")
        self.apply_theme(temp_theme)

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
            current_tab = self.parent.tabs.currentWidget()
            if isinstance(current_tab, QWebEngineView):
                current_tab.page().profile().clearHttpCache()
                current_tab.page().profile().clearAllVisitedLinks()
                QMessageBox.information(self.parent, "Cookies Cleared", "Cookies have been cleared.", QMessageBox.Ok)
            else:
                QMessageBox.warning(self.parent, "Error", "Current tab is not a web page.", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self.parent, "Error", f"Failed to clear cookies: {str(e)}", QMessageBox.Ok)

    def clear_cache(self):
        QWebEngineProfile.defaultProfile().clearHttpCache()
        self.update_cache_size()
        QMessageBox.information(self.parent, "Cache Cleared", "Cache has been cleared.", QMessageBox.Ok)

    def clear_history(self):
        self.parent.tabs.currentWidget().page().profile().clearAllVisitedLinks()
        self.parent.clear_history_data()

    def clear_all_data(self):
        if QMessageBox.question(self.parent, "Confirm", "Clear all browsing data?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.parent.settings_persistence.clear_all_private_data()
            self.update_cache_size()

    def save_settings(self):
        settings = self.parent.settings_persistence.privacy_settings
        settings.update({
            "do_not_track": self.dnt_checkbox.isChecked(),
            "block_third_party_cookies": self.third_party_cookies_checkbox.isChecked(),
            "clear_data_on_exit": self.clear_on_exit_checkbox.isChecked(),
            "private_browsing": self.private_browsing_checkbox.isChecked(),
            "block_trackers": self.tracker_block_checkbox.isChecked(),
            "fingerprint_protection": self.fingerprint_protection.isChecked()
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
            self.mixed_content_checkbox.isChecked(),
            self.new_tab_behavior.currentText(),
            self.hardware_acceleration.isChecked(),
            self.preload_pages.isChecked(),
            self.cache_size_limit.currentText()
        )
        self.accept()

    def apply_theme(self, theme=None):
        theme = theme or self.parent.theme
        dialog_background, text_color, input_background, input_border = (
            (DARK_MODE_BACKGROUND, DARK_MODE_TEXT, DARK_MODE_ACCENT, "#4B5563") if theme == "Dark" 
            else (LIGHT_MODE_BACKGROUND, LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, "#D1D5DB")
        )
        self.setStyleSheet(
            f"QDialog {{ background-color: {dialog_background}; color: {text_color}; "
            f"border-radius: {BORDER_RADIUS}; padding: 15px; }}"
            f"QLabel {{ color: {text_color}; font-size: 14px; }}"
            f"QTabWidget::tab-bar {{ font-size: 14px; font-family: 'Nunito'; }}"
        )
        self.save_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        self.cancel_button.setStyleSheet(self.parent.get_button_style(SECONDARY_COLOR, "#6B7280", "#374151"))
        self.clear_cache_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        self.clear_cookies_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        self.clear_history_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        self.clear_all_data_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
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
        if settings["block_trackers"]:
            url = info.requestUrl().toString()
            if any(tracker in url.lower() for tracker in ["ads.", "tracking", "analytics", "doubleclick"]):
                info.block(True)
        if settings["fingerprint_protection"]:
            info.setHttpHeader(b"User-Agent", b"MojoBrowser/0.2 (Generic)")
            self.enhance_fingerprint_protection(info)

    def enhance_fingerprint_protection(self, info):
        if self.parent.settings_persistence.privacy_settings["fingerprint_protection"]:
            info.setHttpHeader(b"Accept-Language", b"en-US,en;q=0.9")
            info.setHttpHeader(b"Accept", b"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
            js_spoof = """
            Object.defineProperty(window, 'screen', {
                value: { width: 1920, height: 1080, availWidth: 1920, availHeight: 1080 },
                writable: false
            });
            """
            self.parent.tabs.currentWidget().page().runJavaScript(js_spoof)

class DownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setGeometry(300, 300, 500, 400)
        self.active_downloads = 0
        self.parent_browser = parent
        self.layout = QVBoxLayout()
        self.downloads_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.downloads_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"QScrollArea {{ border: 1px solid {'#4B5563' if parent.theme == 'Dark' else '#D1D5DB'}; border-radius: {BORDER_RADIUS}; }}")
        self.layout.addWidget(self.scroll_area)

        self.button_layout = QHBoxLayout()
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        self.close_button.clicked.connect(self.close)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)
        self.setStyleSheet(
            f"QDialog {{ background-color: {DARK_MODE_BACKGROUND if parent.theme == 'Dark' else LIGHT_MODE_BACKGROUND}; "
            f"color: {DARK_MODE_TEXT if parent.theme == 'Dark' else LIGHT_MODE_TEXT}; border-radius: {BORDER_RADIUS}; padding: 15px; }}"
            f"QLabel {{ font-size: 14px; padding: 6px; }}"
            f"QProgressBar {{ border: 1px solid {'#4B5563' if parent.theme == 'Dark' else '#D1D5DB'}; border-radius: 5px; text-align: center; }}"
            "QProgressBar::chunk { background-color: #3B82F6; border-radius: 3px; }"
        )

    def add_download(self, download):
        self.active_downloads += 1
        download_widget = QWidget()
        download_layout = QHBoxLayout()
        label = QLabel(download.suggestedFileName())
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setMinimumWidth(120)
        progress.setMaximumWidth(220)
        speed_label = QLabel("0 KB/s")
        speed_label.setMinimumWidth(70)
        time_label = QLabel("Calculating...")
        time_label.setMinimumWidth(100)
        cancel_button = QPushButton("Cancel")
        pause_button = QPushButton("Pause")
        pause_button.setStyleSheet(self.parent_browser.get_button_style("#F59E0B", "#FBBF24", "#D97706"))
        download_layout.addWidget(label)
        download_layout.addWidget(progress)
        download_layout.addWidget(speed_label)
        download_layout.addWidget(time_label)
        download_layout.addWidget(pause_button)
        download_layout.addWidget(cancel_button)
        download_widget.setLayout(download_layout)
        self.downloads_layout.addWidget(download_widget)
        
        last_received = [0]
        start_time = QTimer()
        start_time.start()
        
        def update_speed(received, total):
            elapsed_time = start_time.elapsed() / 1000
            speed = (received - last_received[0]) / 1024
            speed_label.setText(f"{speed:.1f} KB/s")
            last_received[0] = received
            progress.setValue(int((received / total) * 100))
            if speed > 0:
                remaining_time = (total - received) / (speed * 1024)
                time_label.setText(f"{int(remaining_time // 60)}m {int(remaining_time % 60)}s remaining")
            else:
                time_label.setText("Calculating...")

        download.downloadProgress.connect(update_speed)
        download.finished.connect(lambda: self.on_download_finished(download, download_widget))
        download.stateChanged.connect(lambda state: self.on_state_changed(state, download_widget, pause_button))
        cancel_button.clicked.connect(download.cancel)
        pause_button.clicked.connect(lambda: download.pause() if download.state() == QWebEngineDownloadItem.DownloadInProgress else download.resume())

    def on_download_finished(self, download, widget):
        self.active_downloads -= 1
        if download.state() == QWebEngineDownloadItem.DownloadCompleted:
            widget.findChild(QLabel).setText(f"{download.suggestedFileName()} - Completed")
            widget.findChild(QPushButton).hide()
        if self.active_downloads == 0:
            QTimer.singleShot(1000, self.close)

    def on_state_changed(self, state, widget, pause_button):
        if state == QWebEngineDownloadItem.DownloadCancelled:
            self.active_downloads -= 1
            widget.findChild(QLabel).setText(f"{widget.findChild(QLabel).text()} - Cancelled")
            widget.findChild(QPushButton, "Cancel").hide()
            if self.active_downloads == 0:
                QTimer.singleShot(1000, self.close)
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            pause_button.setText("Resume")
        elif state == QWebEngineDownloadItem.DownloadInProgress:
            pause_button.setText("Pause")

class MojoBrowser(QMainWindow):
    DEFAULT_HOME_PAGE = "https://mojox.org/search"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mojo Browser")
        self.setGeometry(100, 100, 1280, 800)
        self.setFont(UI_FONT)

        self.setWindowIcon(QIcon("icons/Mojo.ico"))

        self.settings_persistence = SettingsPersistence(self)
        self.bookmarks = []
        self.history = []
        self.private_profile = None
        self.privacy_interceptor = PrivacyInterceptor(self)
        self.privacy_engine = initialize_privacy(self)
        self.new_tab_behavior = "Home Page"
        self.hardware_acceleration = True
        self.preload_pages = False
        self.cache_size_limit = "250 MB"
        self.downloads = {}
        self.download_dialog = None
        self.profiles = {"Default": QWebEngineProfile.defaultProfile()}

        self.extension_manager = ExtensionManager(self)
        self.extension_manager.load_extension_status()
        self.extension_manager.load_extensions()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.create_tool_bar()
        self.create_tabs()
        self.setup_system_tray()
        self.setup_download_manager()

        self.settings_persistence.load_settings()
        self.apply_styles()  
        self.add_new_tab(QUrl(self.home_page))

        self.status_bar = QStatusBar()
        self.status_bar.setFont(UI_FONT)
        self.setStatusBar(self.status_bar)

        self.setup_shortcuts()
        self.apply_styles()

        self.cache_timer = QTimer(self)
        self.cache_timer.timeout.connect(self.update_cache_size_periodic)
        self.cache_timer.start(30000)

        self.performance_timer = QTimer(self)
        self.performance_timer.timeout.connect(self.optimize_performance)
        self.performance_timer.start(60000)

        self.tab_suspension_timer = QTimer(self)
        self.tab_suspension_timer.timeout.connect(self.suspend_inactive_tabs)
        self.tab_suspension_timer.start(120000)
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(86400000)

    def create_tool_bar(self):
        self.tool_bar = QToolBar("Navigation", self)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)
        self.tool_bar.setIconSize(QSize(28, 28))
        self.tool_bar.setFont(UI_FONT)
        self.tool_bar.setStyleSheet(self.get_toolbar_style())
        self.tool_bar.setMovable(True)

        actions = [
            ("back.png", "go-previous", "Back", "Go to previous page", self.browser_back),
            ("forward.png", "go-next", "Forward", "Go to next page", self.browser_forward),
            (None, "view-refresh", "Reload", "Reload page", self.browser_reload),
            (None, "process-stop", "Stop", "Stop loading", self.browser_stop),
            ("home.png", "go-home", "Home", "Go to homepage", self.go_home),
            (None, "zoom-in", "Zoom In", "Increase zoom", self.zoom_in),
            (None, "zoom-out", "Zoom Out", "Decrease zoom", self.zoom_out),
            (None, "view-fullscreen", "Fullscreen", "Toggle fullscreen", self.toggle_fullscreen),
        ]
        
        for icon_file, theme_icon, text, tip, connect in actions:
            icon = QIcon(f"icons/{icon_file}") if icon_file and os.path.exists(f"icons/{icon_file}") else QIcon.fromTheme(theme_icon)
            action = QAction(icon, text, self)
            action.setStatusTip(tip)
            action.triggered.connect(connect)
            self.tool_bar.addAction(action)

        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet(self.get_input_style())
        self.address_bar.setMinimumWidth(320)
        self.address_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.address_bar.returnPressed.connect(self.load_page)
        self.address_bar.setClearButtonEnabled(True)
        self.tool_bar.addWidget(self.address_bar)

        go_action = QAction(QIcon("icons/search.png") if os.path.exists("icons/search.png") else QIcon.fromTheme("go-jump"), "Go", self)
        go_action.setStatusTip("Go to address or search")
        go_action.triggered.connect(self.load_page)
        self.tool_bar.addAction(go_action)

        self.tool_bar.addSeparator()
        
        additional_actions = [
            ("new_tab.png", "document-new", "New Tab", "Open new tab", self.add_new_tab),
            (None, "emblem-favorite", "Bookmark", "Bookmark page", self.settings_persistence.add_bookmark),
            (None, "bookmarks", "Bookmarks", "View bookmarks", self.settings_persistence.view_bookmarks),
            (None, "document-open-recent", "History", "View history", self.settings_persistence.view_history),
            ("settings.png", "preferences-system", "Settings", "Open settings", self.open_settings),
            ("exten.png", "applications-other", "Extensions", "Manage extensions", self.open_extensions),
        ]
        
        for icon_file, theme_icon, text, tip, connect in additional_actions:
            icon = QIcon(f"icons/{icon_file}") if icon_file and os.path.exists(f"icons/{icon_file}") else QIcon.fromTheme(theme_icon)
            action = QAction(icon, text, self)
            action.setStatusTip(tip)
            action.triggered.connect(connect)
            self.tool_bar.addAction(action)

        reader_action = QAction(QIcon.fromTheme("document-preview"), "Reader Mode", self)
        reader_action.setStatusTip("Toggle reader mode")
        reader_action.triggered.connect(self.toggle_reader_mode)
        self.tool_bar.addAction(reader_action)

        profile_action = QAction(QIcon.fromTheme("system-users"), "Switch Profile", self)
        profile_action.setStatusTip("Switch user profile")
        profile_action.triggered.connect(self.switch_profile)
        self.tool_bar.addAction(profile_action)

    def get_toolbar_style(self):
        theme = self.theme
        return (
            f"QToolBar {{ background-color: {DARK_MODE_ACCENT if theme == 'Dark' else LIGHT_MODE_ACCENT}; "
            f"color: {DARK_MODE_TEXT if theme == 'Dark' else LIGHT_MODE_TEXT}; "
            f"border-radius: {BORDER_RADIUS}; padding: 10px; spacing: 10px; }}"
            f"QToolButton {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {PRIMARY_COLOR}, stop:1 {self.adjust_color(PRIMARY_COLOR, -20)}); "
            f"color: {TEXT_COLOR}; border: none; border-radius: {BUTTON_BORDER_RADIUS}; padding: 12px; "
            f"font-size: 14px; }}"
            f"QToolButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {BUTTON_HOVER_COLOR}, stop:1 {self.adjust_color(BUTTON_HOVER_COLOR, -20)}); }}"
            f"QToolButton:pressed {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {BUTTON_PRESSED_COLOR}, stop:1 {self.adjust_color(BUTTON_PRESSED_COLOR, -20)}); }}"
        )

    def apply_styles(self):
        theme = self.theme
        main_background, main_text_color, input_background, input_border = (
            (DARK_MODE_BACKGROUND, DARK_MODE_TEXT, DARK_MODE_ACCENT, "#4B5563") if theme == "Dark" 
            else (LIGHT_MODE_BACKGROUND, LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, "#D1D5DB")
        )
        app_stylesheet = (
            f"QMainWindow {{ background-color: {main_background}; color: {main_text_color}; font-size: 14px; }}"
            f"QToolBar {{ background-color: {input_background}; }}"
            f"QStatusBar {{ background-color: {input_background}; }}"
        )
        self.setStyleSheet(app_stylesheet)
        self.tabs.setStyleSheet(self.get_tab_style())
        self.statusBar().setStyleSheet(self.get_statusbar_style())
        self.tool_bar.setStyleSheet(self.get_toolbar_style())
        self.address_bar.setStyleSheet(self.get_input_style())
        if hasattr(self, 'settings_dialog') and self.settings_dialog:
            self.settings_dialog.apply_theme()

    def open_extensions(self):
        dialog = ExtensionsDialog(self)
        dialog.exec_()

    def create_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.tab_context_menu)
        self.tabs.setStyleSheet(self.get_tab_style())
        self.tabs.setFont(UI_FONT)
        self.tabs.setDocumentMode(True)
        self.layout.addWidget(self.tabs)

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icons/app_icon.png") if os.path.exists("icons/app_icon.png") else QIcon.fromTheme("web-browser"), self)
        tray_menu = QMenu()
        tray_menu.addAction("Restore", self.showNormal)
        tray_menu.addAction("New Tab", lambda: self.add_new_tab())
        tray_menu.addAction("Quit", self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()

    def get_tab_style(self):
        theme = self.theme
        tab_text_color, tab_background_color, tab_selected_background = (
            (DARK_MODE_TEXT, DARK_MODE_ACCENT, DARK_MODE_BACKGROUND) if theme == "Dark" 
            else (LIGHT_MODE_TEXT, LIGHT_MODE_ACCENT, LIGHT_MODE_BACKGROUND)
        )
        return (
            "QTabBar::close-button { image: url('icons/close_tab.png'); width: 14px; height: 14px; subcontrol-position: right; }"
            f"QTabWidget::pane {{ border: none; border-radius: {BORDER_RADIUS}; background-color: {tab_selected_background}; padding: 8px; }}"
            f"QTabBar::tab {{ background-color: {tab_background_color}; color: {tab_text_color}; "
            f"border: 1px solid {'#4B5563' if theme == 'Dark' else '#D1D5DB'}; border-bottom: none; "
            f"padding: 10px 20px; border-top-left-radius: {BORDER_RADIUS}; border-top-right-radius: {BORDER_RADIUS}; font-size: 14px; }}"
            f"QTabBar::tab:selected {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {tab_selected_background}, stop:1 {self.adjust_color(tab_selected_background, -10)}); "
            f"border-bottom: 3px solid {PRIMARY_COLOR}; font-weight: bold; }}"
            f"QTabBar::tab:hover:!selected {{ background: {'#374151' if theme == 'Dark' else '#E5E7EB'}; }}"
        )

    def get_statusbar_style(self):
        theme = self.theme
        return (
            f"QStatusBar {{ background-color: {DARK_MODE_ACCENT if theme == 'Dark' else LIGHT_MODE_ACCENT}; "
            f"color: {DARK_MODE_TEXT if theme == 'Dark' else LIGHT_MODE_TEXT}; border-radius: {BORDER_RADIUS}; padding: 6px; font-size: 14px; }}"
        )

    def get_button_style(self, background_color, hover_color, pressed_color):
        text_color = DARK_MODE_TEXT if self.theme == "Dark" else LIGHT_MODE_TEXT
        return (
            f"QPushButton {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {background_color}, stop:1 {self.adjust_color(background_color, -20)}); "
            f"color: {TEXT_COLOR}; border: none; border-radius: {BUTTON_BORDER_RADIUS}; padding: 12px 24px; "
            f"font-weight: 500; font-size: 14px; }}"
            f"QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {hover_color}, stop:1 {self.adjust_color(hover_color, -20)}); }}"
            f"QPushButton:pressed {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {pressed_color}, stop:1 {self.adjust_color(pressed_color, -20)}); }}"
        )

    def get_input_style(self):
        theme = self.theme
        return (
            f"QLineEdit, QComboBox, QTextEdit {{ background-color: {DARK_MODE_ACCENT if theme == 'Dark' else LIGHT_MODE_ACCENT}; "
            f"color: {DARK_MODE_TEXT if theme == 'Dark' else LIGHT_MODE_TEXT}; border: 1px solid {'#4B5563' if theme == 'Dark' else '#D1D5DB'}; "
            f"border-radius: {BORDER_RADIUS}; padding: 10px; font-size: 14px; }}"
            f"QLineEdit:focus, QComboBox:focus {{ border: 2px solid {PRIMARY_COLOR}; }}"
        )

    def get_checkbox_style(self):
        theme = self.theme
        return f"QCheckBox {{ color: {DARK_MODE_TEXT if self.theme == 'Dark' else LIGHT_MODE_TEXT}; padding: 8px; font-weight: 500; font-size: 14px; }}"

    def get_label_style(self):
        theme = self.theme
        return f"QLabel {{ color: {DARK_MODE_TEXT if theme == 'Dark' else LIGHT_MODE_TEXT}; font-weight: 600; font-size: 14px; }}"

    def get_list_style(self):
        theme = self.theme
        list_background, list_text_color, list_selected_background = (
            (DARK_MODE_ACCENT, DARK_MODE_TEXT, "#374151") if theme == "Dark" 
            else (LIGHT_MODE_ACCENT, LIGHT_MODE_TEXT, "#E5E7EB")
        )
        return (
            f"QListWidget {{ background-color: {list_background}; color: {list_text_color}; "
            f"border: 1px solid {'#4B5563' if theme == 'Dark' else '#D1D5DB'}; border-radius: {BORDER_RADIUS}; padding: 10px; font-size: 14px; }}"
            "QListWidget::item { padding: 10px; }"
            f"QListWidget::item:selected {{ background-color: {list_selected_background}; }}"
        )

    def adjust_color(self, hex_color, amount):
        color = int(hex_color[1:], 16)
        r = min(max((color >> 16) + amount, 0), 255)
        g = min(max(((color >> 8) & 0xFF) + amount, 0), 255)
        b = min(max((color & 0xFF) + amount, 0), 255)
        return f"#{r:02x}{g:02x}{b:02x}"

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
        
        if not url:
            if self.new_tab_behavior == "Home Page":
                url = QUrl(self.home_page)
            elif self.new_tab_behavior == "Blank Page":
                url = QUrl("about:blank")
            elif self.new_tab_behavior == "Last Page" and self.history:
                url = QUrl(self.history[-1])
            else:
                url = QUrl(self.home_page)
                
        browser.setUrl(url)
        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda u, b=browser: (self.update_tab_title(b, u), self.update_history(u), self.update_address_bar(i)))
        browser.loadStarted.connect(lambda: self.statusBar().showMessage("Loading..."))
        browser.loadProgress.connect(lambda p: self.statusBar().showMessage(f"Loading... {p}%"))
        browser.loadFinished.connect(lambda ok, b=browser: (self.load_finished(ok, b), self.extension_manager.inject_extensions(b)))
        
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(lambda pos: self.show_web_context_menu(pos, browser))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_tab_title(self, browser, url):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            title = browser.page().title() or "New Tab"
            self.tabs.setTabText(index, title[:30] + "..." if len(title) > 30 else title)
            self.tabs.setTabToolTip(index, title)

    def update_address_bar(self, index):
        if index >= 0:
            browser = self.tabs.widget(index)
            if browser:
                self.address_bar.setText(browser.url().toString())
                self.statusBar().showMessage(f"Zoom: {int(browser.zoomFactor() * 100)}%", 2000)

    def load_page(self):
        url = self.address_bar.text().strip()
        browser = self.tabs.currentWidget()
        if not url or not browser:
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
        if browser and browser.history().canGoBack():
            browser.back()

    def browser_forward(self):
        browser = self.tabs.currentWidget()
        if browser and browser.history().canGoForward():
            browser.forward()

    def browser_reload(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.reload()

    def browser_stop(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.stop()

    def go_home(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl(self.home_page))

    def zoom_in(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.setZoomFactor(min(browser.zoomFactor() + 0.1, 2.5))
            self.update_address_bar(self.tabs.currentIndex())

    def zoom_out(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.setZoomFactor(max(browser.zoomFactor() - 0.1, 0.25))
            self.update_address_bar(self.tabs.currentIndex())

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
            ("F5", self.browser_reload),
            ("Ctrl+H", self.settings_persistence.view_history),
            ("Ctrl+B", self.settings_persistence.view_bookmarks),
            ("Ctrl+Q", self.close),
            ("Ctrl+=", self.zoom_in),
            ("Ctrl+-", self.zoom_out),
            ("F11", self.toggle_fullscreen),
            ("Ctrl+Tab", lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())),
            ("Ctrl+Shift+T", self.reopen_last_tab),
            ("Ctrl+Shift+R", self.toggle_reader_mode),
        ]
        for key, func in shortcuts:
            shortcut = QAction(self)
            shortcut.setShortcut(QKeySequence(key))
            shortcut.triggered.connect(func)
            self.addAction(shortcut)

    def reopen_last_tab(self):
        if self.history:
            self.add_new_tab(QUrl(self.history[-1]))

    def tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index == -1:
            return
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background-color: {DARK_MODE_ACCENT if self.theme == 'Dark' else LIGHT_MODE_ACCENT}; "
            f"color: {DARK_MODE_TEXT if self.theme == 'Dark' else LIGHT_MODE_TEXT}; border-radius: {BORDER_RADIUS}; padding: 6px; font-size: 14px; }}"
            f"QMenu::item:selected {{ background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; }}"
        )
        menu.addAction("Rename Tab", lambda: self.rename_tab(index))
        menu.addAction("Close Tab", lambda: self.close_tab(index))
        menu.addAction("Duplicate Tab", lambda: self.duplicate_tab(index))
        menu.addAction("Pin Tab", lambda: self.pin_tab(index))
        menu.exec_(self.tabs.mapToGlobal(pos))

    def rename_tab(self, index):
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new tab name:")
        if ok and new_name:
            self.tabs.setTabText(index, new_name)

    def duplicate_tab(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.add_new_tab(browser.url())

    def pin_tab(self, index):
        current_text = self.tabs.tabText(index)
        self.tabs.setTabText(index, f"📍 {current_text}")

    def load_finished(self, ok, browser):
        self.statusBar().clearMessage()
        if not ok:
            self.statusBar().showMessage("Failed to load page", 3000)
        else:
            self.statusBar().showMessage("Page loaded successfully", 1000)

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self)
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
        self.settings_dialog.tracker_block_checkbox.setChecked(settings.get("block_trackers", False))
        self.settings_dialog.fingerprint_protection.setChecked(settings.get("fingerprint_protection", False))
        self.settings_dialog.new_tab_behavior.setCurrentText(self.new_tab_behavior)
        self.settings_dialog.hardware_acceleration.setChecked(self.hardware_acceleration)
        self.settings_dialog.preload_pages.setChecked(self.preload_pages)
        self.settings_dialog.cache_size_limit.setCurrentText(self.cache_size_limit)
        self.settings_dialog.exec_()

    def apply_settings(self, home_page, search_engine, theme, javascript_enabled, 
                      block_popups, block_mixed_content, new_tab_behavior, 
                      hardware_acceleration, preload_pages, cache_size_limit):
        self.home_page = home_page or self.home_page
        self.search_engine = search_engine
        self.theme = theme if theme != "System" else ("Dark" if QApplication.palette().color(QPalette.Window).lightness() < 128 else "Light")
        self.javascript_enabled = javascript_enabled
        self.block_popups = block_popups
        self.block_mixed_content = block_mixed_content
        self.new_tab_behavior = new_tab_behavior
        self.hardware_acceleration = hardware_acceleration
        self.preload_pages = preload_pages
        self.cache_size_limit = cache_size_limit
        
        self.apply_styles()
        self.settings_persistence.save_settings()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser:
                self.apply_webengine_settings(browser)
                if self.settings_persistence.privacy_settings["do_not_track"]:
                    browser.page().profile().setHttpUserAgent("MojoBrowser/0.2 (Privacy Enhanced)")

    def apply_webengine_settings(self, browser):
        settings = browser.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, not self.block_popups)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, not self.block_mixed_content)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, self.hardware_acceleration)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, self.hardware_acceleration)
        
        profile = browser.page().profile()
        profile.setUrlRequestInterceptor(self.privacy_engine)
        self.privacy_engine.apply_proxy(profile)
        
        if self.cache_size_limit != "Unlimited":
            size_mb = int(self.cache_size_limit.split()[0])
            profile.setHttpCacheMaximumSize(size_mb * 1024 * 1024)

    def update_history(self, url):
        self.settings_persistence.update_history(url)

    def clear_history_data(self):
        self.history.clear()
        self.settings_persistence.save_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.", QMessageBox.Ok)

    def update_cache_size_periodic(self):
        if hasattr(self, 'settings_dialog') and self.settings_dialog.isVisible():
            self.settings_dialog.update_cache_size()

    def optimize_performance(self):
        current_browser = self.tabs.currentWidget()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser and browser != current_browser:
                browser.page().runJavaScript("window.gc && window.gc();")
        self.suspend_inactive_tabs()

    def closeEvent(self, event):
        if self.settings_persistence.privacy_settings["clear_data_on_exit"]:
            self.settings_persistence.clear_all_private_data()
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage("Mojo Browser", "Running in background", QSystemTrayIcon.Information, 2000)
            event.ignore()
        else:
            super().closeEvent(event)

    def setup_download_manager(self):
        self.download_path = QDir.homePath() + "/Downloads"
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

    def handle_download(self, download):
        suggested_path = os.path.join(self.download_path, download.suggestedFileName())
        download.setPath(suggested_path)
        download.accept()
        if not self.download_dialog or not self.download_dialog.isVisible():
            self.download_dialog = DownloadDialog(self)
            self.download_dialog.show()
        self.downloads[download] = download
        self.download_dialog.add_download(download)

    def suspend_inactive_tabs(self):
        current_browser = self.tabs.currentWidget()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser and browser != current_browser and not self.tabs.tabText(i).startswith("📍"):
                browser.page().setLifecycleState(QWebEnginePage.LifecycleState.Discarded)
                browser.page().setBackgroundColor(QColor(self.theme == "Dark" and DARK_MODE_BACKGROUND or LIGHT_MODE_BACKGROUND))

    def toggle_reader_mode(self):
        browser = self.tabs.currentWidget()
        if not browser or not self.javascript_enabled:
            if not self.javascript_enabled:
                QMessageBox.warning(self, "JavaScript Disabled", "Reader Mode requires JavaScript.", QMessageBox.Ok)
            return

        if getattr(browser, 'reader_mode_active', False):
            browser.page().runJavaScript("""
            var orig = document.getElementById('original-content');
            if (orig) {
                document.body.innerHTML = orig.innerHTML;
                document.body.removeAttribute('style');
                orig.remove();
                window.scrollTo(0, window.readerScroll || 0);
            }
            """)
            browser.reader_mode_active = False
            self.statusBar().showMessage("Reader Mode Off", 2000)
            return

        browser.page().runJavaScript("""
        var orig = document.createElement('div');
        orig.id = 'original-content';
        orig.style.display = 'none';
        orig.innerHTML = document.body.innerHTML;
        document.body.appendChild(orig);
        window.readerScroll = window.scrollY;
        """)

        reader_js = """
        (function() {
            function getContent() {
                const tags = ['article','main','[role="main"]','.content','.post','.article-body',
                    '.story-body','.entry-content','#main-content','.post-content','.article__content',
                    '[itemprop="articleBody"]','.zn-body__paragraph','.storytext','.post-body',
                    '#article-content','.entry','.wp-post-content','.articleBody','.article-content',
                    '.td-post-content'];
                let best = null, max = 0;
                for (let i = 0; i < tags.length; i++) {
                    const els = document.querySelectorAll(tags[i]);
                    for (let j = 0; j < els.length; j++) {
                        const el = els[j], len = el.textContent.length, ps = el.getElementsByTagName('p').length;
                        const score = len + ps * 60;
                        if (score > max && len > 100) {
                            best = el;
                            max = score;
                        }
                    }
                }
                if (!best) {
                    const ps = document.getElementsByTagName('p'), div = document.createElement('div');
                    let count = 0;
                    for (let i = 0; i < ps.length && count < 20; i++) {
                        if (ps[i].textContent.length > 40) {
                            div.appendChild(ps[i].cloneNode(true));
                            count++;
                        }
                    }
                    return count > 1 ? div : document.body.cloneNode(true);
                }
                return best.cloneNode(true);
            }

            const content = getContent(), remove = ['script','style','nav','header','footer','aside',
                'form','button','input','select','textarea','[class*="ad"]','[id*="ad"]',
                '[class*="banner"]','[id*="banner"]','[class*="sidebar"]','[role="complementary"]',
                '[aria-hidden="true"]','[class*="comment"]','[id*="comment"]','[class*="widget"]',
                '[id*="widget"]','.social-share','.related-posts','.author-bio'];
            for (let i = 0; i < remove.length; i++) {
                const els = content.querySelectorAll(remove[i]);
                for (let j = els.length - 1; j >= 0; j--) els[j].remove();
            }

            const media = content.querySelectorAll('img,video,picture');
            for (let i = 0, m = 0; i < media.length && m < 8; i++) {
                const el = media[i];
                if (el.tagName === 'IMG' || el.tagName === 'PICTURE') {
                    const img = el.tagName === 'PICTURE' ? el.querySelector('img') : el;
                    if (img) {
                        img.src = img.src || img.getAttribute('data-src') || '';
                        img.srcset = '';
                    }
                } else if (el.tagName === 'VIDEO') el.controls = true;
                m++;
                if (m === 8) while (++i < media.length) media[i].remove();
            }

            const title = document.querySelector('h1,h2,[class*="title"],[id*="title"],.headline,' +
                '.post-title,[itemprop="headline"],.entry-title,.article-header') || document.createElement('h1');
            title.textContent = title.textContent.trim() || document.title.split(/[-|–]/)[0].trim();

            const div = document.createElement('div');
            div.id = 'reader-content';
            div.appendChild(title.cloneNode(true));
            div.appendChild(content);

            document.body.innerHTML = '';
            document.body.style.cssText = 'background:#f7fafc;margin:0;padding:0';
            document.body.appendChild(div);

            const css = document.createElement('style');
            css.textContent = '#reader-content{margin:30px auto;padding:20px;background:#fff;max-width:900px;}' +
                'h1{font-size:32px;margin:0 0 20px;color:#111827;}' +
                'p{font-size:17px;margin:0 0 15px;color:#1f2a44;line-height:1.7;}' +
                'h2,h3,h4,h5,h6{color:#374151;margin:20px 0 10px;}' +
                'h2{font-size:26px;}h3{font-size:22px;}' +
                'img,video{max-width:100%;margin:15px auto;display:block;}' +
                'a{color:#2563eb;text-decoration:none;}' +
                'a:hover{color:#2563eb;text-decoration:none;}' +
                'blockquote{margin:15px 0;padding:10px 15px;border-left:4px solid #e5e7eb;background:#f9fafb;color:#4b5563;}' +
                'pre{background:#f4f4f5;padding:10px;overflow-x:auto;}';
            document.head.appendChild(css);

            window.scrollTo(0, 0);

            const controls = document.createElement('div');
            controls.id = 'reader-controls';
            controls.style.cssText = 'position:fixed;top:10px;right:10px;background:#fff;padding:10px;border-radius:5px;box-shadow:0 0 10px rgba(0,0,0,0.1);z-index:1000;';
            controls.innerHTML = `
                <label for="font-size">Font Size:</label>
                <input type="range" id="font-size" name="font-size" min="12" max="36" value="17">
                <label for="font-family">Font:</label>
                <select id="font-family" name="font-family">
                    <option value="Arial">Arial</option>
                    <option value="Georgia">Georgia</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Verdana">Verdana</option>
                </select>
                <label for="bg-color">Background:</label>
                <input type="color" id="bg-color" name="bg-color" value="#f7fafc">
            `;
            document.body.appendChild(controls);

            document.getElementById('font-size').addEventListener('input', function() {
                document.querySelector('#reader-content').style.fontSize = this.value + 'px';
            });

            document.getElementById('font-family').addEventListener('change', function() {
                document.querySelector('#reader-content').style.fontFamily = this.value;
            });

            document.getElementById('bg-color').addEventListener('input', function() {
                document.querySelector('#reader-content').style.backgroundColor = this.value;
            });
        })();
        """
        browser.page().runJavaScript(reader_js, lambda _: setattr(browser, 'reader_mode_active', True))
        self.statusBar().showMessage("Reader Mode On", 2000)
        browser.page().runJavaScript(reader_js)
        browser.reader_mode_active = True
        self.statusBar().showMessage("Reader Mode Enabled", 2000)

    def switch_profile(self):
        profile_name, ok = QInputDialog.getItem(self, "Switch Profile", "Select Profile:", list(self.profiles.keys()) + ["New Profile"], 0, False)
        if not ok:
            return
        if profile_name == "New Profile":
            profile_name, ok = QInputDialog.getText(self, "New Profile", "Profile Name:")
            if ok and profile_name and profile_name not in self.profiles:
                self.profiles[profile_name] = QWebEngineProfile(profile_name, self)
        if profile_name in self.profiles:
            browser = self.tabs.currentWidget()
            if browser:
                browser.setPage(PrivacyPage(self.profiles[profile_name], browser))
                self.apply_webengine_settings(browser)
                self.statusBar().showMessage(f"Switched to profile: {profile_name}", 2000)

    def check_for_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/Muhammad-Noraeii/MojoBrowser/releases/latest")
            latest_version = response.json()["tag_name"]
            current_version = "v0.2.4"
            if latest_version > current_version:
                if QMessageBox.question(self, "Update Available", f"Version {latest_version} is available. Update now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl("https://github.com/Muhammad-Noraeii/MojoBrowser/releases/latest"))
        except Exception as e:
            self.statusBar().showMessage(f"Update check failed: {str(e)}", 5000)

    def show_web_context_menu(self, pos, browser):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background-color: {DARK_MODE_ACCENT if self.theme == 'Dark' else LIGHT_MODE_ACCENT}; "
            f"color: {DARK_MODE_TEXT if self.theme == 'Dark' else LIGHT_MODE_TEXT}; border-radius: {BORDER_RADIUS}; padding: 6px; font-size: 14px; }}"
            f"QMenu::item:selected {{ background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; }}"
        )
        menu.addAction("Back", self.browser_back)
        menu.addAction("Forward", self.browser_forward)
        menu.addAction("Reload", self.browser_reload)
        menu.addAction("Copy URL", lambda: QApplication.clipboard().setText(browser.url().toString()))
        menu.addAction("Save Page As...", lambda: browser.page().save(f"{self.download_path}/page.html", QWebEngineDownloadItem.SingleHtmlSaveFormat))
        menu.exec_(browser.mapToGlobal(pos))

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
            "private_browsing": False,
            "fingerprint_protection": False
        }
        self.load_settings()
        self.load_bookmarks()
        self.load_history()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r", encoding="utf-8") as file:
                settings = json.load(file)
                self.parent.home_page = settings.get("home_page", self.parent.DEFAULT_HOME_PAGE)
                self.parent.search_engine = settings.get("search_engine", "Google")
                self.parent.theme = settings.get("theme", "Dark")
                self.parent.javascript_enabled = settings.get("javascript_enabled", True)
                self.parent.block_popups = settings.get("block_popups", True)
                self.parent.block_mixed_content = settings.get("block_mixed_content", True)
                self.parent.new_tab_behavior = settings.get("new_tab_behavior", "Home Page")
                self.parent.hardware_acceleration = settings.get("hardware_acceleration", True)
                self.parent.preload_pages = settings.get("preload_pages", False)
                self.parent.cache_size_limit = settings.get("cache_size_limit", "250 MB")
                self.privacy_settings.update(settings.get("privacy_settings", {}))
        else:
            self.parent.home_page = self.parent.DEFAULT_HOME_PAGE
            self.parent.search_engine = "Google"
            self.parent.theme = "Dark"
            self.parent.javascript_enabled = True
            self.parent.block_popups = True
            self.parent.block_mixed_content = True
            self.parent.new_tab_behavior = "Home Page"
            self.parent.hardware_acceleration = True
            self.parent.preload_pages = False
            self.parent.cache_size_limit = "250 MB"

    def save_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as file:
            json.dump({
                "home_page": self.parent.home_page,
                "search_engine": self.parent.search_engine,
                "theme": self.parent.theme,
                "javascript_enabled": self.parent.javascript_enabled,
                "block_popups": self.parent.block_popups,
                "block_mixed_content": self.parent.block_mixed_content,
                "new_tab_behavior": self.parent.new_tab_behavior,
                "hardware_acceleration": self.parent.hardware_acceleration,
                "preload_pages": self.parent.preload_pages,
                "cache_size_limit": self.parent.cache_size_limit,
                "privacy_settings": self.privacy_settings
            }, file, indent=4)

    def load_bookmarks(self):
        self.parent.bookmarks = json.load(open(self.bookmarks_file, "r", encoding="utf-8")) if os.path.exists(self.bookmarks_file) else []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w", encoding="utf-8") as file:
            json.dump(self.parent.bookmarks, file, indent=4)

    def add_bookmark(self):
        browser = self.parent.tabs.currentWidget()
        if not browser:
            return
        current_url = browser.url().toString()
        title, ok = QInputDialog.getText(self.parent, "Add Bookmark", "Bookmark name:", text=browser.page().title())
        if ok and current_url not in [b["url"] for b in self.parent.bookmarks]:
            self.parent.bookmarks.append({"url": current_url, "title": title})
            self.save_bookmarks()
            QMessageBox.information(self.parent, "Bookmark Added", f"Bookmarked: {title}", QMessageBox.Ok)
        else:
            QMessageBox.information(self.parent, "Bookmark Exists", "This URL is already bookmarked.", QMessageBox.Ok)

    def view_bookmarks(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Bookmarks")
        dialog.setGeometry(300, 300, 550, 450)
        layout = QVBoxLayout(dialog)
        bookmark_list = QListWidget()
        for bookmark in self.parent.bookmarks:
            item = QListWidgetItem(bookmark["title"])
            item.setData(Qt.UserRole, bookmark["url"])
            bookmark_list.addItem(item)
        bookmark_list.setStyleSheet(self.parent.get_list_style())
        bookmark_list.itemDoubleClicked.connect(lambda item: self.parent.tabs.currentWidget().setUrl(QUrl(item.data(Qt.UserRole))))
        layout.addWidget(bookmark_list)
        
        buttons_layout = QHBoxLayout()
        remove_button = QPushButton("Remove Selected")
        remove_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        remove_button.clicked.connect(lambda: self.remove_bookmark(bookmark_list))
        close_button = QPushButton("Close")
        close_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        close_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(remove_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        dialog.exec_()

    def remove_bookmark(self, bookmark_list):
        selected = bookmark_list.currentItem()
        if selected:
            url = selected.data(Qt.UserRole)
            self.parent.bookmarks = [b for b in self.parent.bookmarks if b["url"] != url]
            self.save_bookmarks()
            bookmark_list.takeItem(bookmark_list.currentRow())

    def load_history(self):
        self.parent.history = json.load(open(self.history_file, "r", encoding="utf-8")) if os.path.exists(self.history_file) else []

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump(self.parent.history, file, indent=4)

    def update_history(self, url):
        url_str = url.toString()
        if url_str and url_str not in self.parent.history[-50:]:
            self.parent.history.append(url_str)
            if len(self.parent.history) > 50:
                self.parent.history.pop(0)
            self.save_history()

    def view_history(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("History")
        dialog.setGeometry(300, 300, 550, 450)
        layout = QVBoxLayout(dialog)
        history_list = QListWidget()
        for url in reversed(self.parent.history[-50:]):
            history_list.addItem(url)
        history_list.setStyleSheet(self.parent.get_list_style())
        history_list.itemDoubleClicked.connect(lambda item: self.parent.tabs.currentWidget().setUrl(QUrl(item.text())))
        layout.addWidget(history_list)
        
        buttons_layout = QHBoxLayout()
        clear_button = QPushButton("Clear History")
        clear_button.setStyleSheet(self.parent.get_button_style("#EF4444", "#F87171", "#DC2626"))
        clear_button.clicked.connect(self.clear_history)
        close_button = QPushButton("Close")
        close_button.setStyleSheet(self.parent.get_button_style(PRIMARY_COLOR, BUTTON_HOVER_COLOR, BUTTON_PRESSED_COLOR))
        close_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(clear_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        dialog.exec_()

    def clear_history(self):
        self.parent.history.clear()
        self.save_history()
        QMessageBox.information(self.parent, "History Cleared", "Browsing history has been cleared.", QMessageBox.Ok)

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
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(LIGHT_MODE_BACKGROUND))
    palette.setColor(QPalette.WindowText, QColor(LIGHT_MODE_TEXT))
    app.setPalette(palette)
    
    try:
        browser = MojoBrowser()
        browser.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start browser: {str(e)}")
        sys.exit(1)
