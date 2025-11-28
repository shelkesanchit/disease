document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileLabel = document.querySelector('.file-text');
    const cameraButton = document.getElementById('camera-button');
    const cameraFeed = document.getElementById('camera-feed');
    const video = document.getElementById('video');
    const captureButton = document.getElementById('capture-button');
    const cancelCaptureButton = document.getElementById('cancel-capture-button');
    const loading = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const uploadedImage = document.getElementById('uploaded-image');
    const diseaseResult = document.getElementById('disease-result');
    const confidenceBars = document.getElementById('confidence-bars');
    const recommendationsText = document.getElementById('recommendations-text');
    const unsupportedImageError = document.getElementById('unsupported-image-error');

    let stream;

    // Update file label when a file is selected
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            fileLabel.textContent = this.files[0].name;
        } else {
            fileLabel.textContent = 'Choose an apple image';
        }
    });

    // Handle camera button click
    cameraButton.addEventListener('click', function() {
        cameraFeed.classList.remove('hidden');
        startCamera();
    });

    // Handle capture button click
    captureButton.addEventListener('click', function() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(function(blob) {
            const file = new File([blob], 'capture.png', { type: 'image/png' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            fileLabel.textContent = file.name;
            stopCamera();
            cameraFeed.classList.add('hidden');
        }, 'image/png');
    });

    // Handle cancel capture button click
    cancelCaptureButton.addEventListener('click', function() {
        stopCamera();
        cameraFeed.classList.add('hidden');
    });

    // Start camera feed
    function startCamera() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(s) {
                stream = s;
                video.srcObject = stream;
            })
            .catch(function(error) {
                console.error('Error accessing the camera:', error);
                alert('Error accessing the camera. Please ensure you have granted the necessary permissions.');
            });
    }

    // Stop camera feed
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(function(track) {
                track.stop();
            });
        }
    }

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please select an image first.');
            return;
        }
        
        // Show loading spinner
        loading.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        unsupportedImageError.classList.add('hidden');
        
        // Send request to the server
        fetch('/predictgrape', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                if (data.error === 'Unsupported image. Please upload an image of an apple.') {
                    unsupportedImageError.classList.remove('hidden');
                } else {
                    alert(data.error);
                }
                loading.classList.add('hidden');
                return;
            }
            
            // Update UI with results
            uploadedImage.src = data.image_url;
            diseaseResult.textContent = data.disease;
            
            // Add appropriate class for styling
            diseaseResult.className = 'diagnosis';
            if (data.disease === 'Healthy') {
                diseaseResult.classList.add('healthy');
            } else if (data.disease === 'Blotch Apple') {
                diseaseResult.classList.add('blotch');
            } else if (data.disease === 'Rotten Apple') {
                diseaseResult.classList.add('rotten');
            } else if (data.disease === 'Scab Apple') {
                diseaseResult.classList.add('scab');
            }
            
            // Display confidence scores
            displayConfidenceScores(data.confidence);
            
            // Show recommendations based on diagnosis
            showRecommendations(data.disease);
            
            // Hide loading and show results
            loading.classList.add('hidden');
            resultContainer.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during analysis. Please try again.');
            loading.classList.add('hidden');
        });
    });
    
    // Function to display confidence scores as bars
    function displayConfidenceScores(scores) {
        confidenceBars.innerHTML = '';
        
        const sortedScores = Object.entries(scores).sort((a, b) => b[1] - a[1]);
        
        sortedScores.forEach(([label, score]) => {
            const percentage = (score * 100).toFixed(1);
            
            const barContainer = document.createElement('div');
            barContainer.className = 'confidence-bar-container';
            
            const labelDiv = document.createElement('div');
            labelDiv.className = 'confidence-label';
            
            const nameSpan = document.createElement('span');
            nameSpan.textContent = label;
            
            const valueSpan = document.createElement('span');
            valueSpan.textContent = `${percentage}%`;
            
            labelDiv.appendChild(nameSpan);
            labelDiv.appendChild(valueSpan);
            
            const barDiv = document.createElement('div');
            barDiv.className = 'confidence-bar';
            
            const fillDiv = document.createElement('div');
            fillDiv.className = 'confidence-fill';
            fillDiv.style.width = `${percentage}%`;
            
            // Color based on disease type
            if (label === 'Healthy') {
                fillDiv.style.backgroundColor = '#4caf50';
            } else if (label === 'Blotch Apple') {
                fillDiv.style.backgroundColor = '#ff9800';
            } else if (label === 'Rotten Apple') {
                fillDiv.style.backgroundColor = '#f44336';
            } else if (label === 'Scab Apple') {
                fillDiv.style.backgroundColor = '#9c27b0';
            }
            
            barDiv.appendChild(fillDiv);
            barContainer.appendChild(labelDiv);
            barContainer.appendChild(barDiv);
            
            confidenceBars.appendChild(barContainer);
        });
    }
    
    // Function to show recommendations based on diagnosis
    function showRecommendations(disease) {
        let recommendations = '';
        
        switch (disease) {
            case 'Healthy':
                recommendations = `
                    <p>Your apple appears to be healthy! Here are some tips to maintain its condition and prevent diseases:</p>
                    <ul>
                        <li>Store in a cool, dry place</li>
                        <li>Keep separate from other fruits to prevent ethylene exposure</li>
                        <li>Check periodically for any developing issues</li>
                        <li>Apply preventive fungicides like <strong>sulfur</strong> or <strong>copper-based sprays</strong> during the growing season</li>
                        <li>Ensure proper orchard sanitation by removing fallen leaves and debris</li>
                    </ul>
                `;
                break;
            case 'Blotch Apple':
                recommendations = `
                    <p>Your apple shows signs of blotch disease. Here's what you can do:</p>
                    <ul>
                        <li>Remove affected apples from healthy ones</li>
                        <li>For trees, consider fungicide treatments in the growing season</li>
                        <li>Ensure proper sanitation of storage areas</li>
                        <li>Improve air circulation around fruit trees</li>
                        <li><strong>Pesticide Recommendations:</strong></li>
                        <ul>
                            <li><strong>Captan</strong>: One of the most frequently used fungicides for controlling apple blotch.</li>
                            <li><strong>Thiophanate-methyl</strong>: Often used in combination with captan for better results.</li>
                            <li><strong>Note</strong>: Natural fungicides like sulfur spray are not effective against apple blotch fungus.</li>
                        </ul>
                    </ul>
                `;
                break;
            case 'Rotten Apple':
                recommendations = `
                    <p>Your apple appears to be rotting. Here's what you should do:</p>
                    <ul>
                        <li>Remove the rotten apple immediately to prevent spread</li>
                        <li>Do not consume</li>
                        <li>Check other nearby apples for signs of rot</li>
                        <li>Clean storage area with disinfectant</li>
                        <li><strong>Pesticide Recommendations:</strong></li>
                        <ul>
                            <li><strong>Sulfur</strong>: The most commonly used fungicide for apples.</li>
                            <li><strong>Captan</strong>: Effective against a wide range of fungal diseases.</li>
                            <li><strong>Dithianon</strong>: Another fungicide used to protect apples from rot.</li>
                            <li><strong>Note</strong>: 99% of conventionally grown apples test positive for pesticides, so ensure proper washing before consumption.</li>
                        </ul>
                    </ul>
                `;
                break;
            case 'Scab Apple':
                recommendations = `
                    <p>Your apple shows signs of apple scab. Here's what you can do:</p>
                    <ul>
                        <li>Scab affects appearance but minor cases may still be safe to eat after removing affected areas</li>
                        <li>For trees, consider fungicide applications in early spring</li>
                        <li>Practice good orchard sanitation by removing fallen leaves</li>
                        <li>Improve air circulation by proper pruning</li>
                        <li><strong>Pesticide Recommendations:</strong></li>
                        <ul>
                            <li><strong>Fixed copper</strong>: Effective against apple scab.</li>
                            <li><strong>Bordeaux mixtures</strong>: A traditional fungicide for apple scab.</li>
                            <li><strong>Captan</strong>, <strong>chlorothalonil</strong>, <strong>mancozeb</strong>, <strong>myclobutanil</strong>, <strong>propiconazole</strong>, or <strong>thiophanate methyl</strong>: Available for apple scab control.</li>
                            <li><strong>Note</strong>: Alternate fungicides with different modes of action to prevent resistance development.</li>
                        </ul>
                    </ul>
                `;
                break;
            default:
                recommendations = `<p>No specific recommendations available for this diagnosis.</p>`;
        }
        
        recommendationsText.innerHTML = recommendations;
    }
});