import os
import json
import random
import logging
import requests
from typing import Optional, List, Dict
from PyQt5.QtCore import QUrl, QTimer, QEventLoop, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEnginePage
from PyQt5.QtNetwork import QNetworkProxy, QNetworkAccessManager, QNetworkRequest
from data_manager import DataManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
]

TRACKER_PATTERNS = [
    r"google-analytics\.com", r"doubleclick\.net", r"adservice\.google\.",
    r"facebook\.com/tr", r"twitter\.com/i/", r"pixel\.quantserve\.com",
    r"scorecardresearch\.com", r"adnxs\.com", r"outbrain\.com", r"taboola\.com",
    r"mixpanel\.com", r"hotjar\.com", r"quantcast\.com", r"krxd\.net",
]

class ProxyTester(QThread):
    result = pyqtSignal(str, bool)

    def __init__(self, proxy: str, timeout: int = 5000):
        super().__init__()
        self.proxy = proxy
        self.timeout = timeout

    def run(self):
        manager = QNetworkAccessManager()
        try:
            host, port = self.proxy.split(":")
            proxy_obj = QNetworkProxy(QNetworkProxy.HttpProxy, host, int(port))
            manager.setProxy(proxy_obj)
            request = QNetworkRequest(QUrl("https://httpbin.org/get"))
            request.setAttribute(QNetworkRequest.RedirectPolicyAttribute, QNetworkRequest.NoLessSafeRedirectPolicy)
            reply = manager.get(request)
            loop = QEventLoop()
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            timer.start(self.timeout)
            reply.finished.connect(loop.quit)
            loop.exec_()
            success = reply.error() == QNetworkRequest.NoError and reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) == 200
            self.result.emit(self.proxy, success)
            reply.deleteLater()
        except Exception:
            self.result.emit(self.proxy, False)

class PrivacyEngine(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.data_manager = DataManager()
        self.https_only = True
        self.permissions = {}
        self.proxy_settings = None
        self.proxy_list = self.load_proxies_from_file()
        self.working_proxies = []
        self.proxy_cache = self.data_manager.get_proxy_cache()
        self.tracker_blacklist_url = "https://easylist.to/easylist/easylist.txt"
        self.tracker_blacklist = set()
        self.load_privacy_settings()
        self.initialize_proxies()
        self.update_tracker_blacklist()
        self.anti_fingerprinting_enabled = True

    def load_proxies_from_file(self, filename="Proxy.txt") -> List[str]:
        proxies = []
        try:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if line and ":" in line:  
                            proxies.append(line)
                logger.info(f"Loaded {len(proxies)} proxies from {filename}")
            else:
                logger.error(f"Proxy file {filename} not found")
                self.parent.statusBar().showMessage(f"Proxy file {filename} not found", 5000)
        except Exception as e:
            logger.error(f"Failed to load proxies from {filename}: {str(e)}")
            self.parent.statusBar().showMessage(f"Error loading proxies: {str(e)}", 5000)
        return proxies

    def load_privacy_settings(self) -> None:
        try:
            settings = self.data_manager.get_privacy_settings()
            self.https_only = settings.get("https_only", True)
            self.permissions = settings.get("permissions", {})
            self.anti_fingerprinting_enabled = settings.get("anti_fingerprinting_enabled", True)
        except Exception as e:
            logger.error(f"Failed to load privacy settings: {str(e)}")
            self.parent.statusBar().showMessage(f"Privacy settings error: {str(e)}", 5000)
            self.save_privacy_settings()

    def save_privacy_settings(self) -> None:
        try:
            self.data_manager.set_privacy_settings({
                "https_only": self.https_only,
                "permissions": self.permissions,
                "anti_fingerprinting_enabled": self.anti_fingerprinting_enabled
            })
        except Exception as e:
            logger.error(f"Failed to save privacy settings: {str(e)}")
            self.parent.statusBar().showMessage(f"Failed to save privacy settings: {str(e)}", 5000)

    def load_proxy_cache(self) -> None:
        try:
            self.proxy_cache = self.data_manager.get_proxy_cache()
        except Exception as e:
            logger.error(f"Failed to load proxy cache: {str(e)}")
            self.proxy_cache = {}

    def save_proxy_cache(self) -> None:
        try:
            self.data_manager.set_proxy_cache(self.proxy_cache)
        except Exception as e:
            logger.error(f"Failed to save proxy cache: {str(e)}")

    def initialize_proxies(self) -> None:
        self.parent.statusBar().showMessage("Testing proxies...", 5000)
        self.working_proxies.clear()
        untested_proxies = [p for p in self.proxy_list if p not in self.proxy_cache]
        self.testers = []

        if not untested_proxies:
            self.working_proxies = [p for p, works in self.proxy_cache.items() if works]
            self.finalize_proxy_init()
            return

        for proxy in untested_proxies:
            tester = ProxyTester(proxy, timeout=3000)
            tester.result.connect(self.on_proxy_tested)
            self.testers.append(tester)
            tester.start()

    @pyqtSlot(str, bool)
    def on_proxy_tested(self, proxy: str, success: bool) -> None:
        self.proxy_cache[proxy] = success
        if success:
            self.working_proxies.append(proxy)
        self.testers = [t for t in self.testers if t.isRunning()]
        if not self.testers:
            self.save_proxy_cache()
            self.finalize_proxy_init()

    def finalize_proxy_init(self) -> None:
        if not self.working_proxies:
            logger.error("No working proxies found")
            self.parent.statusBar().showMessage("No functional proxies available", 5000)
        else:
            self.set_random_proxy()
            self.parent.statusBar().showMessage(f"Initialized {len(self.working_proxies)} proxies", 3000)

    def test_proxy(self, proxy: str) -> bool:
        manager = QNetworkAccessManager()
        try:
            host, port = proxy.split(":")
            proxy_obj = QNetworkProxy(QNetworkProxy.HttpProxy, host, int(port))
            manager.setProxy(proxy_obj)
            request = QNetworkRequest(QUrl("https://httpbin.org/get"))
            reply = manager.get(request)
            loop = QEventLoop()
            QTimer.singleShot(3000, loop.quit)
            reply.finished.connect(loop.quit)
            loop.exec_()
            return reply.error() == QNetworkRequest.NoError and reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) == 200
        except Exception:
            return False
        finally:
            manager.deleteLater()

    def set_random_proxy(self, specific_proxy: Optional[str] = None) -> None:
        try:
            if specific_proxy:
                if specific_proxy in self.working_proxies:
                    proxy = specific_proxy
                elif specific_proxy in self.proxy_list and self.test_proxy(specific_proxy):
                    proxy = specific_proxy
                    self.working_proxies.append(proxy)
                    self.proxy_cache[proxy] = True
                    self.save_proxy_cache()
                else:
                    raise ValueError(f"Proxy {specific_proxy} not functional")
            else:
                if not self.working_proxies:
                    raise ValueError("No working proxies available")
                proxy = random.choice(self.working_proxies)

            host, port = proxy.split(":")
            self.proxy_settings = QNetworkProxy(QNetworkProxy.HttpProxy, host, int(port))
            QNetworkProxy.setApplicationProxy(self.proxy_settings)
            self.parent.statusBar().showMessage(f"Connected via proxy: {proxy}", 5000)
        except Exception as e:
            logger.error(f"Failed to set proxy: {str(e)}")
            self.proxy_settings = None
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))
            self.parent.statusBar().showMessage(f"No functional proxy: {str(e)}", 5000)

    def apply_proxy(self, profile: QWebEngineProfile) -> None:
        try:
            if self.proxy_settings:
                QNetworkProxy.setApplicationProxy(self.proxy_settings)
                profile.clearHttpCache()
            else:
                QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))
        except Exception as e:
            logger.error(f"Failed to apply proxy: {str(e)}")
            self.parent.statusBar().showMessage(f"Proxy error: {str(e)}", 5000)

    def update_tracker_blacklist(self):
        try:
            response = requests.get(self.tracker_blacklist_url, timeout=10)
            response.raise_for_status()
            blacklist_content = response.text.splitlines()
            for line in blacklist_content:
                if line.startswith("||") and not line.startswith("||*"):
                    domain = line[2:].split("^")[0].split("/")[0]
                    self.tracker_blacklist.add(domain.lower())
            logger.info("Updated tracker blacklist from EasyList")
        except Exception as e:
            logger.error(f"Failed to update tracker blacklist: {str(e)}")
            self.parent.statusBar().showMessage("Failed to update tracker blacklist", 5000)

    def interceptRequest(self, info) -> None:
        try:
            url = info.requestUrl().toString()
            settings = self.parent.settings_persistence.privacy_settings
            url_lower = url.lower()
            url_host = info.requestUrl().host().lower()

            if self.https_only and url.startswith("http://"):
                info.redirect(QUrl(url.replace("http://", "https://")))
                return

            if settings.get("block_third_party_cookies", True):
                info.setHttpHeader(b"Cookie", b"")

            if settings.get("do_not_track", True):
                info.setHttpHeader(b"DNT", b"1")

            if settings.get("block_trackers", False):
                for pattern in TRACKER_PATTERNS:
                    if pattern in url_lower:
                        info.block(True)
                        self.parent.statusBar().showMessage(f"Blocked tracker: {url}", 2000)
                        return
                if self.tracker_blacklist and any(domain in url_lower for domain in self.tracker_blacklist):
                    info.block(True)
                    self.parent.statusBar().showMessage(f"Blocked tracker from blacklist: {url}", 2000)
                    return

            host = info.requestUrl().host()
            if host in self.permissions:
                perms = self.permissions[host]
                if not perms.get("allow_cookies", True):
                    info.setHttpHeader(b"Cookie", b"")
                if not perms.get("allow_js", True):
                    info.block(True)

            if self.anti_fingerprinting_enabled:
                info.setHttpHeader(b"Accept-Language", b"en-US,en;q=0.5")
                info.setHttpHeader(b"Accept", b"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
                info.setHttpHeader(b"Referer", b"")
        except Exception as e:
            logger.error(f"Error intercepting request: {str(e)}")
            self.parent.statusBar().showMessage(f"Privacy error: {str(e)}", 5000)

    def spoof_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def apply_anti_fingerprinting(self, page: QWebEnginePage) -> None:
        try:
            script = """
            (function() {
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type) {
                    const ctx = originalGetContext.apply(this, arguments);
                    if (type === '2d' || type === 'webgl') {
                        const originalFillRect = ctx.fillRect;
                        ctx.fillRect = function() {
                            originalFillRect.apply(this, arguments);
                            const noise = Math.random() * 0.2;
                            const imageData = ctx.getImageData(0, 0, this.width, this.height);
                            for (let i = 0; i < imageData.data.length; i += 4) {
                                imageData.data[i] += noise;
                                imageData.data[i + 1] += noise;
                                imageData.data[i + 2] += noise;
                            }
                            ctx.putImageData(imageData, 0, 0);
                        };
                    }
                    return ctx;
                };
                Object.defineProperty(window, 'screen', {
                    value: { width: 1920, height: 1080, availWidth: 1920, availHeight: 1080, colorDepth: 24, pixelDepth: 24 },
                    writable: false
                });
                Object.defineProperty(navigator, 'hardwareConcurrency', { value: 4, writable: false });
                Object.defineProperty(navigator, 'deviceMemory', { value: 8, writable: false });
                Object.defineProperty(navigator, 'platform', { value: 'Win32', writable: false });
                Object.defineProperty(navigator, 'languages', { value: ['en-US', 'en'], writable: false });
                Object.defineProperty(navigator, 'webdriver', { value: false, writable: false });
                window.chrome = window.chrome || {};
                Object.defineProperty(navigator, 'doNotTrack', { value: '1', writable: false });
                Object.defineProperty(navigator, 'connection', { 
                    value: { effectiveType: '4g', rtt: 50, downlink: 10, saveData: false }, 
                    writable: false 
                });
                Object.defineProperty(window, 'devicePixelRatio', { value: 1, writable: false });
                const originalGetBattery = navigator.getBattery;
                navigator.getBattery = function() {
                    return Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1.0
                    });
                };
                Object.defineProperty(navigator, 'plugins', { 
                    value: [], 
                    writable: false 
                });
                Object.defineProperty(navigator, 'mimeTypes', { 
                    value: [], 
                    writable: false 
                });
            })();
            """
            page.runJavaScript(script)
        except Exception as e:
            logger.error(f"Anti-fingerprinting failed: {str(e)}")
            self.parent.statusBar().showMessage(f"Anti-fingerprinting error: {str(e)}", 5000)

class PrivacyPage(QWebEnginePage):
    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)
        self.privacy_engine: Optional[PrivacyEngine] = None

    def setPrivacyEngine(self, engine: PrivacyEngine) -> None:
        try:
            self.privacy_engine = engine
            if self.privacy_engine:
                self.privacy_engine.apply_anti_fingerprinting(self)
                self.profile().setHttpUserAgent(self.privacy_engine.spoof_user_agent())
                self.privacy_engine.apply_proxy(self.profile())
        except Exception as e:
            logger.error(f"Failed to set PrivacyEngine: {str(e)}")
            if self.parent():
                self.parent().statusBar().showMessage(f"Privacy setup error: {str(e)}", 5000)

    def acceptNavigationRequest(self, url: QUrl, type_, isMainFrame: bool) -> bool:
        try:
            if self.privacy_engine and self.privacy_engine.https_only and url.toString().startswith("http://"):
                self.setUrl(QUrl(url.toString().replace("http://", "https://")))
                return False
            return super().acceptNavigationRequest(url, type_, isMainFrame)
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            if self.parent():
                self.parent().statusBar().showMessage(f"Navigation error: {str(e)}", 5000)
            return False

def initialize_privacy(browser):
    try:
        privacy_engine = PrivacyEngine(browser)
        return privacy_engine
    except Exception as e:
        logger.error(f"Failed to initialize PrivacyEngine: {str(e)}")
        browser.statusBar().showMessage(f"Privacy init failed: {str(e)}", 5000)
        return None