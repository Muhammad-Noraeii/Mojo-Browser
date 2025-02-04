[برای مشاهده نسخه ی فارسی کلیک کنید.](readme-fa.md)

# Screenshots


# Mojo Browser - v0.1 Alpha

Mojo  Browser is a lightweight web browser built using **PyQt5** and **Python**. This project aims to create a modern web browser with essential features such as customizable settings, file downloading, cache management, and security options, while also providing a sleek user interface.

## Features

### 1. **Web Browser**
   - Basic web browsing features such as **Back**, **Forward**, and **Reload**.
   - **Address Bar** to enter URLs or search terms.
   - Built-in search engine integration for:
     - Google
     - Bing
     - DuckDuckGo
     - Yahoo

### 2. **Settings Management**
   - **Home Page Customization**: Set a default homepage URL.
   - **Search Engine Selection**: Choose from multiple search engines.
   - **Theme Options**: Choose between **Dark** and **Light** themes.
   - **JavaScript Settings**: Enable or disable JavaScript execution.
   - **Pop-Up Blocking**: Block pop-ups for a safer browsing experience.
   - **Mixed Content Blocking**: Prevent loading of insecure HTTP content on HTTPS pages.

### 3. **Download Manager**
   - **Download Handling**: Prompt to select a directory for saving files.
   - **Progress Tracking**: Display download progress in the terminal.
   - **Notifications**: Inform the user when downloads start and complete.

### 4. **Data Management**
   - **Clear Cache**: Clear the browser cache to free up space.
   - **Clear History**: Clear browsing history to maintain privacy.
   - **Clear Cookies**: Delete all cookies stored by the browser.

### 5. **About**
   - Displays the browser’s version and credits in the "About Us" section.
   - Provides links to the GitHub repository for developers to contribute or download the source code.

## Requirements

To run Mojo Browser, you need the following:

- Python 3.6 or higher
- PyQt5 (including PyQtWebEngine)
- QtWebEngine for the web engine components

You can install the necessary dependencies using **pip**:

```bash
pip install PyQt5 PyQtWebEngine
```

## Installation

1. Clone the repository to your local machine:
   
   ```bash
   git clone https://github.com/Muhammad-Noraeii/Browser.git
   cd Browser
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

4. Once the app is launched, you will see a browser window where you can start browsing.

## Usage

### Launching the Browser
- After running the app, the **Mojo Browser** window will open with a default homepage set to **Google**.
- The **Address Bar** allows users to enter URLs directly or search the web using the selected search engine.
- **Navigation**: Use the **Back**, **Forward**, and **Reload** buttons to navigate through your history and refresh the current page.
- **Settings**: Open the settings dialog to customize preferences such as search engine, homepage, and theme.

### File Downloads
- When a download is initiated, a **file picker dialog** will appear, allowing the user to choose the save location.
- The browser will track download progress and notify the user once the download is complete.

### Data Management
- From the **Settings**, you can clear the cache, cookies, and browsing history to maintain privacy and free up space.
- **Cache Size**: The current cache size is displayed in the Data Management tab and updates dynamically.

### Themes
- **Dark Mode** and **Light Mode** themes are available. Switch between them for a customized experience based on your preference.

### Security Features
- Enable or disable **JavaScript** execution for enhanced security.
- Block **Pop-ups** to prevent annoying ads.
- Block **Mixed Content** to prevent insecure HTTP resources from loading on secure HTTPS pages.

## Configuration

### settings.json

Settings are stored in a **JSON file** (`settings.json`) located in the application's working directory. It contains information about the following configurations:

- **home_page**: The default homepage URL (e.g., `https://www.google.com`).
- **search_engine**: The default search engine selected by the user.
- **theme**: The theme preference (**Light** or **Dark**).
- **javascript_enabled**: Whether JavaScript is enabled.
- **block_popups**: Whether pop-ups are blocked.
- **block_mixed_content**: Whether mixed content is blocked.

Example:

```json
{
  "home_page": "https://www.google.com",
  "search_engine": "Google",
  "theme": "Dark",
  "javascript_enabled": true,
  "block_popups": true,
  "block_mixed_content": true
}
```

## Contributing

We welcome contributions to the project! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make the changes and write tests if applicable.
4. Open a Pull Request to merge your changes.

Please ensure all code adheres to the PEP 8 style guide and the app is properly tested before submitting a pull request.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **PyQt5**: The Python bindings for Qt5 that make this browser possible.
- **QtWebEngine**: For embedding the Chromium-based web engine in our app.
- **Python**: The backbone of this application.
- Special thanks to the **PyQt5** and **QtWebEngine** communities for their support and documentation.



## Contact

For issues or feature requests, please open an issue on the [GitHub repository](https://github.com/Muhammad-Noraeii/Browser). You can also reach out to the project maintainers at [Mail Me](mailto:Muhammad.Noraeii@gmail.com).

---

### Developer Links:

- GitHub Repository: [https://github.com/Muhammad-Noraeii/Browser](https://github.com/Muhammad-Noraeii/Browser)
- Issue Tracker: [https://github.com/Muhammad-Noraeii/Browser/issues](https://github.com/Muhammad-Noraeii/Browser/issues)
