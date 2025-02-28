<div align="center">
   <img src="https://github.com/Muhammad-Noraeii/Mojo-Browser/blob/main/datas/browser.png?raw=true"/>
</div>


# Mojo Browser

![Mojo Browser Screenshot](https://imgurl.ir/uploads/t367213_screenshot.png)  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)  
[![Python Version](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)  
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)  
[![GitHub Release](https://img.shields.io/github/v/release/Muhammad-Noraeii/Mojo-browser)](https://github.com/Muhammad-Noraeii/Mojo-browser/releases)  
[![Stars](https://img.shields.io/github/stars/Muhammad-Noraeii/Mojo-browser?style=social)](https://github.com/Muhammad-Noraeii/Mojo-browser/stargazers)

**Mojo Browser** is a sleek, privacy-centric web browser built with Python and PyQt5. Designed for users who demand control over their online experience, it blends a modern interface with robust security features and performance optimizations. Whether you’re safeguarding your data or exploring the web, Mojo Browser offers a lightweight, open-source solution that stands out.

---

## ✨ Key Features

### Browsing Experience
- **Multi-Tab Interface**: Manage tabs effortlessly with drag-and-drop, pinning, and contextual options.
- **Theming Options**: Toggle between Dark, Light, or System themes for a tailored look.
- **Search Freedom**: Pick from 10+ engines, including privacy-respecting choices like DuckDuckGo and Mojeek.
- **Reader Mode**: Strip pages to essentials for focused reading.
- **Download Manager**: Track downloads with progress, pause/resume, and cancel capabilities.

### Privacy & Security
- **Privacy Engine**: Blocks trackers, enforces HTTPS, and spoofs user agents to shield your identity.
- **Proxy Support**: Rotates configurable proxies for added anonymity.
- **Fine-Tuned Controls**: Block third-party cookies, clear data on exit, and enable anti-fingerprinting.
- **Do Not Track (DNT)**: Signals privacy preferences to websites.
- **Fingerprint Protection**: Disrupts trackers with canvas noise and uniform screen metrics.

### Performance Optimization
- **Hardware Acceleration**: Leverages GPU for smooth rendering (optional).
- **Tab Suspension**: Reduces memory use by pausing inactive tabs.
- **Custom Cache**: Set limits from 50 MB to unlimited for balanced performance.
- **Preloading**: Optionally speeds up navigation with page preloading.

### Developer Highlights
- **Modular Codebase**: Cleanly separates privacy, UI, and settings for easy extension.
- **Open Source**: MIT-licensed, inviting collaboration.
- **Detailed Logging**: Simplifies debugging with comprehensive logs.

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.8 or higher
- **PyQt5**: 5.15 or later
- **OS**: Windows, macOS, Linux

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Muhammad-Noraeii/Mojo-browser.git
   cd Mojo-browser
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install PyQt5
   ```

4. **Launch the Browser**:
   ```bash
   python main.py
   ```

### Pre-built Binaries
Download executables from the [Releases](https://github.com/Muhammad-Noraeii/Mojo-browser/releases) page (cross-platform support in development).

---

## 🖥️ How to Use

1. **Start Browsing**: Launch the app and enter a URL or search term in the address bar.
2. **Customize**:
   - Access **Settings** via the toolbar to adjust privacy, performance, or UI.
   - Set your homepage, enable proxies, or tweak cache limits.
3. **Shortcuts**:
   - `Ctrl+T`: New tab
   - `Ctrl+R`: Reload page
   - `F11`: Fullscreen
   - See all shortcuts below!

---

## 🛠️ For Developers

### Project Structure
```
Mojo-browser/
├── main.py              # Main browser logic and UI
├── MojoPrivacy.py       # Privacy, proxy, and anti-fingerprinting tools
├── icons/               # Optional custom icons
└── README.md            # This documentation
```

### Core Modules
- **PrivacyEngine**: Handles proxy rotation, tracker blocking, and fingerprint defense.
- **MojoBrowser**: Drives the UI, tab system, and system tray integration.
- **SettingsDialog**: Provides a rich customization interface.

### Contributing
We’d love your help! Here’s how to contribute:
1. **Fork** the repo.
2. **Branch**: Create a feature branch (`git checkout -b feature/YourFeature`).
3. **Code**: Make changes with clear commits.
   - Stick to PEP 8 style.
   - Comment complex sections.
4. **Test**: Verify functionality across platforms.
5. **Push**: Submit your branch (`git push origin feature/YourFeature`).
6. **Pull Request**: Open a PR with a clear explanation.

---

## 🔧 Configuration

### Privacy Settings
Adjust via the UI or edit the generated `privacy_settings.json`:
```json
{
  "https_only": true,
  "permissions": {
    "example.com": {
      "allow_cookies": false,
      "allow_js": true
    }
  }
}
```

### Proxy Setup
Customize `PROXY_LIST` in `MojoPrivacy.py`:
```python
PROXY_LIST = ["proxy1.example.com:8080", "proxy2.example.com:3128"]
```

---

## 📝 Keyboard Shortcuts

| Shortcut         | Action                |
|-------------------|-----------------------|
| `Ctrl+T`         | New Tab              |
| `Ctrl+W`         | Close Tab            |
| `Ctrl+R` / `F5`  | Reload Page          |
| `Ctrl+H`         | View History         |
| `Ctrl+B`         | View Bookmarks       |
| `Ctrl+Q`         | Exit Browser         |
| `Ctrl+=`         | Zoom In              |
| `Ctrl+-`         | Zoom Out             |
| `F11`            | Fullscreen Toggle    |
| `Ctrl+Shift+R`   | Reader Mode Toggle   |
| `Ctrl+Shift+T`   | Reopen Last Tab      |

---

## 🌟 Future Plans

- Pre-compiled binaries for all platforms
- Extension framework
- WebRTC leak prevention
- Cloud-sync for bookmarks/settings
- Performance benchmarking

---

## 👥 Credits

- **[Muhammad Noraeii](https://github.com/Muhammad-Noraeii)** - Lead Developer
- **[Guguss-31](https://github.com/Guguss-31)** - Core Contributor

Thanks to the open-source community for fueling this project!

---

## 📜 License

Released under the [MIT License](LICENSE).

---

## 💬 Contact

- **Issues**: [Report bugs or suggest features](https://github.com/Muhammad-Noraeii/Mojo-browser/issues)
- **Email**: Reach out at your-email@example.com
- **Star Us**: Give a ⭐ on [GitHub](https://github.com/Muhammad-Noraeii/Mojo-browser)!

---

*Mojo Browser: Browse boldly, stay private, and enjoy the web your way.*

---
