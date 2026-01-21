import os
import io
import zipfile
import requests
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

def is_valid_url(url):
    """Check if URL has valid scheme and netloc."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_images(url):
    """
    Returns all image URLs found on `url`.
    Includes <img> tags and <link> icons.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch page: {e}")
    
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
    
    # Standard images
    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        if is_valid_url(img_url):
            urls.append(img_url)

    # Icons (ico, svg, png, etc used as icons)
    for link in soup.find_all("link"):
        rel = link.attrs.get("rel", [])
        if any("icon" in r.lower() for r in rel):
            icon_url = link.attrs.get("href")
            if not icon_url:
                continue
            icon_url = urljoin(url, icon_url)
            if is_valid_url(icon_url):
                urls.append(icon_url)

    return list(set(urls))


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape():
    """
    Accepts JSON: { "url": "https://example.com" }
    Returns: { "images": ["url1", "url2", ...] }
    """
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    
    url = data["url"]
    
    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL. Include scheme (http/https)."}), 400
    
    try:
        images = get_all_images(url)
        # Extract hostname for zip filename
        hostname = urlparse(url).netloc.replace('www.', '')
        return jsonify({"images": images, "count": len(images), "hostname": hostname})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def download():
    """
    Accepts JSON: { "images": ["url1", "url2", ...], "hostname": "example.com" }
    Returns: ZIP file containing downloaded images.
    """
    data = request.get_json()
    if not data or "images" not in data:
        return jsonify({"error": "Missing 'images' in request body"}), 400
    
    image_urls = data["images"]
    hostname = data.get("hostname", "images")  # Default to 'images' if not provided
    
    if not image_urls:
        return jsonify({"error": "No images provided"}), 400
    
    # Create in-memory zip
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, img_url in enumerate(image_urls):
            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    # Get filename from URL
                    parsed = urlparse(img_url)
                    filename = os.path.basename(parsed.path)
                    
                    # Handle empty or problematic filenames
                    if not filename or len(filename) < 3:
                        ext = ".jpg"
                        content_type = response.headers.get("Content-Type", "")
                        if "png" in content_type:
                            ext = ".png"
                        elif "svg" in content_type:
                            ext = ".svg"
                        elif "ico" in content_type or "icon" in content_type:
                            ext = ".ico"
                        elif "gif" in content_type:
                            ext = ".gif"
                        elif "webp" in content_type:
                            ext = ".webp"
                        filename = f"image_{i+1}{ext}"
                    
                    # Ensure unique filenames
                    base, ext = os.path.splitext(filename)
                    if not ext:
                        ext = ".jpg"
                    unique_filename = f"{base}_{i+1}{ext}"
                    
                    zf.writestr(unique_filename, response.content)
            except Exception:
                # Skip failed downloads
                continue
    
    zip_buffer.seek(0)
    
    # Create filename from hostname
    zip_filename = f"images_{hostname}.zip"
    
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=zip_filename
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
