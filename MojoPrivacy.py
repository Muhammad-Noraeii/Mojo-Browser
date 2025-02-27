import os
import json
import random
import logging
from PyQt5.QtCore import QUrl, QTimer, QEventLoop, QTime
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEnginePage
from PyQt5.QtNetwork import QNetworkProxy, QNetworkAccessManager, QNetworkRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0"
]

TRACKER_PATTERNS = [
    r"google-analytics\.com",
    r"doubleclick\.net",
    r"adservice\.google\.",
    r"facebook\.com/tr",
    r"twitter\.com/i/"
]

PROXY_LIST = [
    "88.135.41.109:4145", "103.251.223.105:6084", "182.160.110.154:9898",
    "198.44.171.161:7088", "104.207.53.203:3128"
]

class PrivacyEngine(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.https_only = True
        self.permissions = {}
        self.proxy_settings = None
        self.proxy_list = PROXY_LIST[:]
        self.working_proxies = []
        self.network_manager = QNetworkAccessManager()
        self.load_privacy_settings()
        self.initialize_proxies()

    def load_privacy_settings(self):
        try:
            if os.path.exists("privacy_settings.json"):
                with open("privacy_settings.json", "r") as f:
                    settings = json.load(f)
                    self.https_only = settings.get("https_only", True)
                    self.permissions = settings.get("permissions", {})
        except Exception as e:
            logging.error(f"Failed to load privacy settings: {e}")

    def save_privacy_settings(self):
        try:
            with open("privacy_settings.json", "w") as f:
                json.dump({
                    "https_only": self.https_only,
                    "permissions": self.permissions
                }, f)
        except Exception as e:
            logging.error(f"Failed to save privacy settings: {e}")

    def initialize_proxies(self):
        for proxy in self.proxy_list:
            if self.test_proxy(proxy):
                self.working_proxies.append(proxy)
        if not self.working_proxies:
            logging.error("No working proxies found.")
            self.parent.statusBar().showMessage("No functional proxies available", 5000)
        else:
            self.set_random_proxy()

    def test_proxy(self, proxy, timeout=5000):
        try:
            host, port = proxy.split(":")
            proxy_obj = QNetworkProxy()
            proxy_obj.setType(QNetworkProxy.HttpProxy)
            proxy_obj.setHostName(host)
            proxy_obj.setPort(int(port))
            self.network_manager.setProxy(proxy_obj)
            request = QNetworkRequest(QUrl("https://httpbin.org/get"))
            request.setAttribute(QNetworkRequest.RedirectPolicyAttribute, QNetworkRequest.NoLessSafeRedirectPolicy)
            reply = self.network_manager.get(request)
            loop = QEventLoop()
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            timer.start(timeout)
            reply.finished.connect(loop.quit)
            loop.exec_()
            success = reply.error() == QNetworkRequest.NoError and reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) == 200
            if success:
                logging.info(f"Proxy {proxy} is functional")
                return True
            else:
                logging.warning(f"Proxy {proxy} failed: {reply.errorString()}")
                return False
        except ValueError:
            logging.error(f"Invalid proxy format: {proxy}")
            return False
        except Exception as e:
            logging.warning(f"Proxy {proxy} test failed: {e}")
            return False
        finally:
            self.network_manager.setProxy(QNetworkProxy(QNetworkProxy.NoProxy))

    def set_random_proxy(self, specific_proxy=None):
        try:
            if specific_proxy:
                if specific_proxy in self.working_proxies:
                    proxy = specific_proxy
                elif self.test_proxy(specific_proxy):
                    proxy = specific_proxy
                    self.working_proxies.append(proxy)
                else:
                    logging.warning(f"Specified proxy {specific_proxy} not functional")
                    proxy = None
            else:
                proxy = None
            if not proxy:
                if not self.working_proxies:
                    raise Exception("No working proxies available")
                proxy = random.choice(self.working_proxies)
            host, port = proxy.split(":")
            self.proxy_settings = QNetworkProxy()
            self.proxy_settings.setType(QNetworkProxy.HttpProxy)
            self.proxy_settings.setHostName(host)
            self.proxy_settings.setPort(int(port))
            QNetworkProxy.setApplicationProxy(self.proxy_settings)
            logging.info(f"Using proxy: {proxy}")
            self.parent.statusBar().showMessage(f"Connected via proxy: {proxy}", 5000)
        except Exception as e:
            logging.error(f"Failed to set proxy: {e}")
            self.proxy_settings = None
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))
            self.parent.statusBar().showMessage("No functional proxy available", 5000)

    def apply_proxy(self, profile):
        if self.proxy_settings:
            QNetworkProxy.setApplicationProxy(self.proxy_settings)
            profile.clearHttpCache()
            logging.info("Proxy applied to profile")
        else:
            no_proxy = QNetworkProxy()
            no_proxy.setType(QNetworkProxy.NoProxy)
            QNetworkProxy.setApplicationProxy(no_proxy)
            logging.info("No proxy applied")

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        settings = self.parent.settings_persistence.privacy_settings
        if self.https_only and url.startswith("http://"):
            info.redirect(QUrl(url.replace("http://", "https://")))
            return
        if settings.get("block_third_party_cookies", True):
            info.setHttpHeader(b"Cookie", b"")
        if settings.get("do_not_track", True):
            info.setHttpHeader(b"DNT", b"1")
        if settings.get("block_trackers", False):
            for pattern in TRACKER_PATTERNS:
                if pattern in url:
                    info.block(True)
                    logging.info(f"Blocked tracker: {url}")
                    self.parent.statusBar().showMessage(f"Blocked tracker: {url}", 2000)
                    return
        host = info.requestUrl().host()
        if host in self.permissions:
            perms = self.permissions[host]
            if not perms.get("allow_cookies", True):
                info.setHttpHeader(b"Cookie", b"")
            if not perms.get("allow_js", True):
                info.block(True)

    def spoof_user_agent(self):
        return random.choice(USER_AGENTS)

    def apply_anti_fingerprinting(self, page):
        script = """
        (function() {
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type) {
                const ctx = originalGetContext.apply(this, arguments);
                if (type === '2d' || type === 'webgl') {
                    const originalFillRect = ctx.fillRect;
                    ctx.fillRect = function() {
                        originalFillRect.apply(this, arguments);
                        const noise = Math.random() * 0.1;
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
                value: { width: 1920, height: 1080, availWidth: 1920, availHeight: 1080 },
                writable: false
            });
        })();
        """
        page.runJavaScript(script)

class PrivacyPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.privacy_engine = None

    def setPrivacyEngine(self, engine):
        self.privacy_engine = engine
        if self.privacy_engine:
            self.privacy_engine.apply_anti_fingerprinting(self)
            self.profile().setHttpUserAgent(self.privacy_engine.spoof_user_agent())
            self.privacy_engine.apply_proxy(self.profile())

    def acceptNavigationRequest(self, url, type_, isMainFrame):
        if self.privacy_engine and self.privacy_engine.https_only and url.toString().startswith("http://"):
            self.setUrl(QUrl(url.toString().replace("http://", "https://")))
            return False
        return super().acceptNavigationRequest(url, type_, isMainFrame)

def initialize_privacy(browser):
    privacy_engine = PrivacyEngine(browser)
    return privacy_engine

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    from main import MojoBrowser
    browser = MojoBrowser()
    browser.show()
    sys.exit(app.exec_())