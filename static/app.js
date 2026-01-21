/**
 * Image Extractor - Frontend Application
 */

// State
let selectedImages = new Set();
let allImages = [];
let currentHostname = 'images'; // Store the hostname for zip naming

// DOM Elements
const urlInput = document.getElementById('url-input');
const scrapeBtn = document.getElementById('scrape-btn');
const errorMessage = document.getElementById('error-message');
const resultsSection = document.getElementById('results-section');
const resultsCount = document.getElementById('results-count');
const imageGrid = document.getElementById('image-grid');
const selectAllBtn = document.getElementById('select-all-btn');
const downloadBtn = document.getElementById('download-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.querySelector('.loading-text');

// Event Listeners
scrapeBtn.addEventListener('click', handleScrape);
urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleScrape();
});
selectAllBtn.addEventListener('click', handleSelectAll);
downloadBtn.addEventListener('click', handleDownload);

/**
 * Handle scrape button click
 */
async function handleScrape() {
    const url = urlInput.value.trim();

    // Validation
    if (!url) {
        showError('Please enter a URL');
        return;
    }

    // Add https:// if missing
    let finalUrl = url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        finalUrl = 'https://' + url;
    }

    clearError();
    setLoading(true, 'Scanning for images...');
    scrapeBtn.classList.add('loading');

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: finalUrl })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to scrape images');
        }

        if (data.images.length === 0) {
            showError('No images found on this page');
            resultsSection.classList.add('hidden');
        } else {
            allImages = data.images;
            currentHostname = data.hostname || 'images'; // Store hostname
            selectedImages.clear();
            renderImages(data.images);
            resultsSection.classList.remove('hidden');
            updateResultsCount();
        }
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
        scrapeBtn.classList.remove('loading');
    }
}

/**
 * Render image grid
 */
function renderImages(images) {
    imageGrid.innerHTML = '';

    images.forEach((imageUrl, index) => {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.dataset.url = imageUrl;

        // Get filename from URL
        const filename = getFilename(imageUrl);

        card.innerHTML = `
            <img src="${imageUrl}" alt="${filename}" loading="lazy" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Crect fill=%22%2312121a%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%22 y=%2255%22 text-anchor=%22middle%22 fill=%22%2355556a%22 font-size=%2212%22%3EFailed%3C/text%3E%3C/svg%3E'">
            <div class="image-overlay"></div>
            <div class="check-indicator">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20,6 9,17 4,12"/>
                </svg>
            </div>
            <span class="image-filename">${filename}</span>
        `;

        card.addEventListener('click', () => toggleImageSelection(card, imageUrl));

        imageGrid.appendChild(card);
    });
}

/**
 * Toggle image selection
 */
function toggleImageSelection(card, imageUrl) {
    if (selectedImages.has(imageUrl)) {
        selectedImages.delete(imageUrl);
        card.classList.remove('selected');
    } else {
        selectedImages.add(imageUrl);
        card.classList.add('selected');
    }
    updateDownloadButton();
    updateSelectAllButton();
}

/**
 * Handle select all / deselect all
 */
function handleSelectAll() {
    const allSelected = selectedImages.size === allImages.length;

    if (allSelected) {
        // Deselect all
        selectedImages.clear();
        document.querySelectorAll('.image-card').forEach(card => {
            card.classList.remove('selected');
        });
    } else {
        // Select all
        allImages.forEach(url => selectedImages.add(url));
        document.querySelectorAll('.image-card').forEach(card => {
            card.classList.add('selected');
        });
    }

    updateDownloadButton();
    updateSelectAllButton();
}

/**
 * Handle download button click
 */
async function handleDownload() {
    if (selectedImages.size === 0) return;

    downloadBtn.classList.add('loading');
    downloadBtn.disabled = true;
    setLoading(true, `Downloading ${selectedImages.size} images...`);

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                images: Array.from(selectedImages),
                hostname: currentHostname
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to download images');
        }

        // Create download link
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `images_${currentHostname}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
        showError(error.message);
    } finally {
        downloadBtn.classList.remove('loading');
        downloadBtn.disabled = false;
        setLoading(false);
    }
}

/**
 * Update download button state
 */
function updateDownloadButton() {
    downloadBtn.disabled = selectedImages.size === 0;
    const text = selectedImages.size > 0
        ? `Download Selected (${selectedImages.size})`
        : 'Download Selected';
    downloadBtn.querySelector('.btn-text').textContent = text;
}

/**
 * Update select all button text
 */
function updateSelectAllButton() {
    const allSelected = selectedImages.size === allImages.length && allImages.length > 0;
    selectAllBtn.textContent = allSelected ? 'Deselect All' : 'Select All';
}

/**
 * Update results count
 */
function updateResultsCount() {
    resultsCount.textContent = `${allImages.length} Image${allImages.length !== 1 ? 's' : ''} Found`;
}

/**
 * Show/hide loading overlay
 */
function setLoading(isLoading, message = '') {
    if (isLoading) {
        loadingText.textContent = message;
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
}

/**
 * Clear error message
 */
function clearError() {
    errorMessage.textContent = '';
}

/**
 * Get filename from URL
 */
function getFilename(url) {
    try {
        const pathname = new URL(url).pathname;
        const filename = pathname.split('/').pop();
        return filename || 'image';
    } catch {
        return 'image';
    }
}
