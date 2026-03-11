# Contributing to OpenHome

Thank you for your interest in contributing to OpenHome! This guide will help you get started.

## 🎯 Ways to Contribute

- 🐛 **Report Bugs** - Found an issue? Let us know!
- 💡 **Feature Requests** - Have an idea? Share it!
- 📝 **Improve Documentation** - Help make docs better
- 💻 **Code Contributions** - Fix bugs, add features
- 🎨 **UI/UX Improvements** - Make it prettier

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openhome.git
   cd openhome
   ```
3. **Create** a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Setup

```bash
# Install dependencies
pip install -e .

# Copy config
cp config.example.yaml config.yaml

# Run in development
python app.py
```

## 🔧 Coding Standards

- Use **4 spaces** for indentation
- Follow **PEP 8** style guide
- Add **docstrings** to functions
- Keep functions **small** and **focused**

## 📝 Commit Messages

Use clear, descriptive commit messages:

```
feat: add dark mode toggle
fix: resolve RSS parsing error
docs: update installation guide
```

## 🧪 Testing

Before submitting:

```bash
# Test your changes
python app.py
```

## 📤 Submitting Changes

1. **Commit** your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

2. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create** a Pull Request

## 💬 Getting Help

- Open an [Issue](https://github.com/none-ai/openhome/issues)
- Join our discussions

## 📜 Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community welcoming.

---

Thank you for contributing! 🎉
