document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.getElementById('downloadBtn');
    const urlInput = document.getElementById('url');
    const resultDiv = document.getElementById('result');
    const downloadInfo = document.getElementById('downloadInfo');

    const showError = (message) => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        downloadInfo.innerHTML = '';
        downloadInfo.appendChild(errorDiv);
        resultDiv.classList.remove('hidden');
    };

    const showSuccess = (message) => {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        downloadInfo.appendChild(successDiv);
    };

    downloadBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        const type = document.querySelector('input[name="type"]:checked').value;

        if (!url) {
            showError('Please enter a YouTube URL');
            return;
        }

        // Show loading state
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<span class="loading"></span>Downloading...';
        resultDiv.classList.remove('hidden');
        downloadInfo.innerHTML = '<div class="loading-message">Processing your request...</div>';

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    type: type
                })
            });

            const data = await response.json();

            if (data.success) {
                downloadInfo.innerHTML = '';

                if (type === 'video') {
                    downloadInfo.innerHTML = `
                        <div class="video-card">
                            <img src="${data.thumbnail}" alt="${data.title}" class="video-thumbnail">
                            <div class="video-info">
                                <h3 class="video-title">${data.title}</h3>
                                <a href="/downloads/${encodeURIComponent(data.filename)}" 
                                   class="btn btn-success" download>
                                    Download Video
                                </a>
                            </div>
                        </div>
                    `;
                    showSuccess('Video processed successfully!');
                } else {
                    downloadInfo.innerHTML = `
                        <h3 class="video-title mb-4">${data.playlist_title}</h3>
                        <div class="grid">
                            ${data.videos.map(video => `
                                <div class="video-card">
                                    <img src="${video.thumbnail}" alt="${video.title}" class="video-thumbnail">
                                    <div class="video-info">
                                        <h4 class="video-title">${video.title}</h4>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    showSuccess('Playlist processed successfully! Videos are being downloaded to your downloads folder.');
                }
            } else {
                showError(data.error || 'An error occurred while processing your request');
            }
        } catch (error) {
            showError('An error occurred while downloading. Please try again.');
            console.error(error);
        } finally {
            // Reset button state
            downloadBtn.disabled = false;
            downloadBtn.textContent = 'Download';
        }
    });
}); 