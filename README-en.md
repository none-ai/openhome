# OpenHome

A modern personal homepage with GitHub integration, RSS feeds, and smart theme colors.

![Screenshot](https://raw.githubusercontent.com/none-ai/openhome/main/screenshot.jpg)

## ✨ Features

- 🎨 **Modern Dark Theme** - Sleek, eye-friendly design
- 🌈 **Smart Theme Colors** - Auto-extracts colors from your GitHub avatar with intelligent adjustments
- 💾 **Color Caching** - Theme colors cached for 24 hours for faster loading
- 📊 GitHub Contribution Heatmap
- 📦 GitHub Public Repositories (sorted by stars)
- 📰 RSS Feed Aggregation
- ⚙️ **Fully Configurable** - YAML-based configuration
- 📱 **Responsive Design** - Works on all devices
- 🌍 Chinese Font Support

## 🚀 Quick Start

### 1. Configure

Copy the example config file:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` and modify:

```yaml
# GitHub username
github_username: "your-github-username"

# GitHub Token (optional, for higher API rate limits)
github_token: "ghp_xxxxxxxxxxxxxxxxxxxx"

# Port number
port: 8004

# RSS feeds
rss_feeds:
  - url: "https://your-blog.com/feed.xml"
    name: "My Blog"

# Bio
bio:
  name: "Your Name"
  title: "Developer"
  description: "Hello, I'm a developer."

# Social links
social:
  github: "your-github-username"
  email: "you@example.com"
```

### 2. Install

```bash
# Using pip
pip install -r requirements.txt

# Or using pyproject.toml (recommended)
pip install -e .
```

### 3. Run

```bash
python app.py
```

Open http://localhost:8004 in your browser.

## 📦 Installation Options

### From PyPI (Coming Soon)

```bash
pip install openhome
```

### From Source

```bash
git clone https://github.com/none-ai/openhome.git
cd openhome
pip install -e .
```

## 🔑 GitHub Token

### Why Token?

- **Without Token**: 60 requests/hour limit
- **With Token**: 5000 requests/hour limit

### How to Generate?

1. Login to GitHub
2. Go to Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
3. Click "Generate new token (classic)"
4. Select `repo` permission
5. Add the generated token to `config.yaml`

### Note

- Token is stored in `config.yaml`, which is in `.gitignore` and won't be committed
- Without token, GitHub API has 60 requests/hour limit

## 🎨 Smart Theme Colors

### How It Works

1. **Auto-extraction**: Extracts dominant color from GitHub avatar
2. **Intelligent Adjustment**:
   - Saturation: 40%-80% (avoid too dull or too vivid)
   - Brightness: 30%-70% (avoid too dark or too bright)
3. **Caching**: Colors cached for 24 hours

### Clear Cache Manually

Visit:
```
http://localhost:8004/api/clear-cache
```

Or delete `.cache/theme_colors.json` and restart.

## 🌍 Environment Variables (Optional)

If you need proxy for GitHub:

```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python app.py
```

## 📁 Project Structure

```
openhome/
├── app.py              # Main application
├── config.yaml         # Configuration (not committed)
├── config.example.yaml # Example config
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Package metadata
├── .gitignore         # Git ignore rules
├── .cache/            # Cache directory (auto-generated)
├── templates/
│   └── index.html     # Main template
└── static/
    └── avatar.png     # Avatar (optional)
```

## ⚙️ Configuration Reference

| Option | Description |
|--------|-------------|
| `github_username` | GitHub username for fetching repos |
| `github_token` | GitHub Token (optional) |
| `port` | Server port, default 8004 |
| `rss_feeds` | List of RSS feed sources |
| `bio.name` | Your name |
| `bio.title` | Title/Position |
| `bio.description` | Bio description |
| `bio.avatar` | Avatar path (GitHub avatar takes priority) |
| `social.*` | Social media links |

## 🌐 API Endpoints

- `GET /` - Main page
- `GET /api/clear-cache` - Clear cache

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Made with ❤️ by [stlin256](https://github.com/stlin256)
