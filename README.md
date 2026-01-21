# 🖼️ Image Extractor

A sleek web application to scrape, preview, and download images from any website.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🔍 **Extract images** from any URL
- 👀 **Preview** all found images in a beautiful grid
- ✅ **Select** individual images or all at once
- 📦 **Download** selected images as a ZIP file (named after the website)
- 🎨 **Modern UI** with glassmorphism design and smooth animations

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ImageExtractor.git
cd ImageExtractor
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
Navigate to `http://localhost:5000`

## 📁 Project Structure

```
ImageExtractor/
├── app.py              # Flask backend
├── image_scraper.py    # Image scraping utilities
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main HTML template
└── static/
    ├── app.js          # Frontend JavaScript
    └── styles.css      # CSS styles
```

## 🛠️ Tech Stack

- **Backend:** Flask, BeautifulSoup4, Requests
- **Frontend:** Vanilla JavaScript, CSS3
- **Fonts:** Space Grotesk, JetBrains Mono

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

---

Built with ❤️ and Flask
