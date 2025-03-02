

# Contributing to Mojo Browser

Thank you for your interest in contributing to Mojo Browser! We welcome contributions from the community to help improve this privacy-focused, lightweight web browser. Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

---

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Coding Guidelines](#coding-guidelines)
- [Getting Help](#getting-help)

---

## How to Contribute

There are many ways to contribute to Mojo Browser:

- **Code**: Fix bugs, add features, or improve performance.
- **Documentation**: Enhance the README, add comments, or write tutorials.
- **Testing**: Report bugs or test new features.
- **Feedback**: Suggest improvements or share ideas.

---

## Reporting Bugs

If you find a bug, please let us know so we can fix it!

1. **Check Existing Issues**: Search the [Issues](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues) tab to ensure it hasn’t been reported.
2. **Open a New Issue**:
   - Go to the [Issues](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues) page.
   - Click "New Issue" and select "Bug Report".
   - Provide:
     - A clear title (e.g., "Crash when opening Settings in Dark Mode").
     - Steps to reproduce the bug.
     - Expected vs. actual behavior.
     - Your environment (OS, Python version, PyQt5 version).
     - Screenshots or logs (if applicable).
3. **Submit**: We’ll review and respond as soon as possible.

---

## Suggesting Features

Have an idea to make Mojo Browser better? We’d love to hear it!

1. **Check Existing Requests**: Browse the [Issues](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues) tab for similar suggestions.
2. **Open a Feature Request**:
   - Go to the [Issues](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues) page.
   - Click "New Issue" and select "Feature Request".
   - Include:
     - A descriptive title (e.g., "Add Support for Custom Keyboard Shortcuts").
     - A detailed explanation of the feature.
     - Why it would benefit users.
     - Any mockups or examples (optional).
3. **Submit**: We’ll discuss feasibility and next steps.

---

## Submitting Pull Requests

Ready to contribute code? Follow these steps:

1. **Fork the Repository**:
   - Click "Fork" on [Muhammad-Noraeii/Mojo-Browser](https://github.com/Muhammad-Noraeii/Mojo-Browser).
   - Clone your fork:
     ```bash
     git clone https://github.com/YOUR_USERNAME/Mojo-Browser.git
     cd Mojo-Browser
     ```

2. **Set Up the Environment**:
   - Install dependencies:
     ```bash
     pip install PyQt5 PyQtWebEngine requests
     ```

3. **Create a Branch**:
   - Use a descriptive name:
     ```bash
     git checkout -b feature/add-custom-shortcuts
     ```
   - For bug fixes, use `fix/` (e.g., `fix/crash-on-settings`).

4. **Make Changes**:
   - Follow the [Coding Guidelines](#coding-guidelines) below.
   - Test your changes locally with `python main.py`.

5. **Commit Changes**:
   - Write clear, concise commit messages:
     ```bash
     git commit -m "Add custom shortcut support in Settings"
     ```

6. **Push to Your Fork**:
   ```bash
   git push origin feature/add-custom-shortcuts
   ```

7. **Open a Pull Request**:
   - Go to your fork on GitHub and click "Pull Request".
   - Target the `main` branch of `Muhammad-Noraeii/Mojo-Browser`.
   - Provide:
     - A title (e.g., "Add Custom Shortcut Support").
     - A description of changes and why they’re useful.
     - Reference related issues (e.g., "Fixes #123").
   - Submit for review.

8. **Review Process**:
   - Maintainers will review your PR, suggest changes if needed, and merge it once approved.

---

## Coding Guidelines

To maintain consistency and quality, please adhere to these standards:

- **Language**: Python 3.8+.
- **Style**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). Use tools like `flake8` or `pylint` to check.
  - Indentation: 4 spaces.
  - Max line length: 100 characters.
  - Variable names: Descriptive (e.g., `extension_manager` not `ext_mgr`).
- **Comments**: Add docstrings for classes and functions; use inline comments sparingly for clarity.
- **Error Handling**: Use try-except blocks where appropriate (e.g., file I/O, network requests).
- **Dependencies**: Avoid adding new dependencies unless necessary; discuss in an issue first.
- **Testing**: Ensure your changes don’t break existing functionality. Test with `python main.py`.

Example:
```python
class ExtensionManager:
    """Manages browser extensions, including loading and enabling/disabling."""

    def load_extensions(self):
        """Load all .js extension files from the extensions directory."""
        try:
            ext_files = glob.glob(f"{self.extensions_dir}/*.js")
            self.extensions.clear()
            for ext_file in ext_files:
                ext_name = os.path.basename(ext_file).split('.')[0]
                self.extensions[ext_name] = ext_file
        except Exception as e:
            logger.error(f"Failed to load extensions: {str(e)}")
```

---

## Getting Help

- **Questions**: Open a discussion in the [Issues](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues) tab or contact a maintainer.
- **Community**: Join the conversation (add a link to a Discord or forum if created).
- **Documentation**: Refer to the [README](README.md) for setup and usage details.

---

Thank you for contributing to Mojo Browser! Together, we can make it a powerful tool for privacy and browsing freedom.

