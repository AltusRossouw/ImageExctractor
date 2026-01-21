import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import zipfile
import shutil
import time

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_images(url):
    """
    Returns all image URLs found on `url`
    """
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    urls = []
    # Standard images
    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        
        # Make the URL absolute
        img_url = urljoin(url, img_url)

        if is_valid_url(img_url):
            urls.append(img_url)

    # Icons (ico, svg, png, etc used as icons)
    for link in soup.find_all("link"):
        rel = link.attrs.get("rel", [])
        # valid rels for icons: 'icon', 'shortcut icon', 'apple-touch-icon', etc.
        # bs4 returns rel as list
        if any("icon" in r.lower() for r in rel):
            icon_url = link.attrs.get("href")
            if not icon_url:
                continue
            
            icon_url = urljoin(url, icon_url)
            if is_valid_url(icon_url):
                urls.append(icon_url)

    return list(set(urls))

def download_images(image_urls, download_folder="downloaded_images"):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    saved_images = []
    
    count = 1
    total = len(image_urls)
    
    print(f"Found {total} images. Downloading...")
    
    for url in image_urls:
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                # Guess filename from URL
                filename = os.path.join(download_folder, os.path.basename(urlparse(url).path))
                
                # If filename is empty or invalid, generate one
                if not os.path.basename(filename) or len(os.path.basename(filename)) < 3:
                     filename = os.path.join(download_folder, f"image_{count}.jpg")

                # Avoid overwrites
                base, ext = os.path.splitext(filename)
                if not ext:
                    # Try to guess extension from content-type if missing
                    # For simplicity, default to jpg or keep as is if no extension
                    # but let's just use what we have or add .jpg if totally missing
                    ext = ".jpg"
                    filename = base + ext

                # Check if file exists, if so append number
                uniq_count = 1
                while os.path.exists(filename):
                    filename = f"{base}_{uniq_count}{ext}"
                    uniq_count += 1
                
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                saved_images.append(filename)
                print(f"[{count}/{total}] Downloaded: {url}")
                count += 1
        except Exception as e:
            print(f"[{count}/{total}] Failed to download {url}: {e}")
            count += 1
            
    return saved_images

def create_zip_archive(files, zip_name):
    print(f"Creating zip file: {zip_name}")
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    print("Zip created successfully.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python image_scraper.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    
    if not is_valid_url(url):
        print("Error: Invalid URL. Please include scheme (http/https).")
        sys.exit(1)

    domain_name = urlparse(url).netloc
    
    # 1. Get all images
    print(f"Scanning {url} for images...")
    try:
        imgs = get_all_images(url)
    except Exception as e:
        print(f"Error fetching page: {e}")
        sys.exit(1)

    if not imgs:
        print("No images found.")
        sys.exit(0)

    # 2. Download images to temporary folder
    temp_dir = f"temp_images_{int(time.time())}"
    downloaded_files = download_images(imgs, temp_dir)

    if not downloaded_files:
        print("No images could be downloaded.")
        shutil.rmtree(temp_dir)
        sys.exit(0)

    # 3. Zip files
    zip_filename = f"images_{domain_name}.zip"
    create_zip_archive(downloaded_files, zip_filename)

    # 4. Cleanup
    shutil.rmtree(temp_dir)
    print(f"Done! Saved to {zip_filename}")

if __name__ == "__main__":
    main()
