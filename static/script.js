// document.addEventListener('DOMContentLoaded', function() {
//     // DOM Elements
//     const uploadArea = document.getElementById('upload-area');
//     const fileInput = document.getElementById('file-input');
//     const previewContainer = document.getElementById('preview-container');
//     const previewImage = document.getElementById('preview-image');
//     const changeImageBtn = document.getElementById('change-image');
//     const analyzeImageBtn = document.getElementById('analyze-image');
//     const resultsSection = document.getElementById('results-section');
//     const loader = document.getElementById('loader');
//     const resultsContainer = document.getElementById('results-container');
//     const newAnalysisBtn = document.getElementById('new-analysis');
    
//     // Prediction Results Elements
//     const resultIcon = document.getElementById('result-icon');
//     const predictionText = document.getElementById('prediction-text');
//     const confidenceFill = document.getElementById('confidence-fill');
//     const confidenceText = document.getElementById('confidence-text');
//     const resultMessage = document.getElementById('result-message');
//     const symptomsList = document.getElementById('symptoms-list');
//     const pesticidesList = document.getElementById('pesticides-list');
//     const preventionList = document.getElementById('prevention-list');
//     const diseaseInfo = document.getElementById('disease-info');
//     const errorInfo = document.getElementById('error-info');
//     const errorMessage = document.getElementById('error-message');

//     // Event Listeners
//     uploadArea.addEventListener('click', () => fileInput.click());
    
//     // Handle drag and drop
//     uploadArea.addEventListener('dragover', (e) => {
//         e.preventDefault();
//         uploadArea.classList.add('dragover');
//     });
    
//     uploadArea.addEventListener('dragleave', () => {
//         uploadArea.classList.remove('dragover');
//     });
    
//     uploadArea.addEventListener('drop', (e) => {
//         e.preventDefault();
//         uploadArea.classList.remove('dragover');
        
//         if (e.dataTransfer.files.length) {
//             handleFileSelection(e.dataTransfer.files[0]);
//         }
//     });
    
//     fileInput.addEventListener('change', (e) => {
//         if (e.target.files.length) {
//             handleFileSelection(e.target.files[0]);
//         }
//     });
    
//     changeImageBtn.addEventListener('click', () => {
//         resetUI();
//     });
    
//     analyzeImageBtn.addEventListener('click', () => {
//         if (fileInput.files.length) {
//             analyzeImage(fileInput.files[0]);
//         }
//     });
    
//     newAnalysisBtn.addEventListener('click', () => {
//         resetUI();
//         resultsSection.hidden = true;
//     });
    
//     // Functions
//     function handleFileSelection(file) {
//         // Check if file is an image
//         if (!file.type.match('image/jpeg') && !file.type.match('image/png') && !file.type.match('image/jpg')) {
//             showError('Please select a valid image file (JPG, JPEG, or PNG)');
//             return;
//         }
        
//         const reader = new FileReader();
        
//         reader.onload = (e) => {
//             previewImage.src = e.target.result;
//             uploadArea.hidden = true;
//             previewContainer.hidden = false;
//         };
        
//         reader.readAsDataURL(file);
//     }
    
//     function analyzeImage(file) {
//         // Show loading state
//         resultsSection.hidden = false;
//         loader.hidden = false;
//         resultsContainer.hidden = true;
        
//         // Create form data
//         const formData = new FormData();
//         formData.append('file', file);
        
//         // Send request to server
//         fetch('/predict', {
//             method: 'POST',
//             body: formData
//         })
//         .then(response => response.json())
//         .then(data => {
//             displayResults(data);
//         })
//         .catch(error => {
//             showError('An error occurred while analyzing the image. Please try again.');
//             console.error('Error:', error);
//         })
//         .finally(() => {
//             loader.hidden = true;
//             resultsContainer.hidden = false;
//         });
//     }
    
//     function displayResults(data) {
//         // Reset previous results
//         resetResultsDisplay();
        
//         // Check if there was an error
//         if (data.error) {
//             showError(data.error);
//             return;
//         }
        
//         // Check if image is a grape leaf
//         if (!data.is_leaf) {
//             showError(data.message || 'The uploaded image does not appear to be a grape leaf.');
//             return;
//         }
        
//         // Handle unrecognized prediction
//         if (data.prediction === 'Unrecognized') {
//             predictionText.textContent = 'Unrecognized';
//             resultIcon.className = 'result-icon fas fa-question-circle status-unknown';
//             confidenceFill.style.width = `${data.confidence * 100}%`;
//             confidenceText.textContent = `${(data.confidence * 100).toFixed(1)}%`;
//             resultMessage.textContent = data.message;
//             diseaseInfo.hidden = true;
//             return;
//         }
        
//         // Display prediction results
//         predictionText.textContent = data.prediction;
//         confidenceFill.style.width = `${data.confidence * 100}%`;
//         confidenceText.textContent = `${(data.confidence * 100).toFixed(1)}%`;
//         resultMessage.textContent = data.message;
        
//         // Set icon and color based on prediction
//         if (data.prediction === 'Healthy') {
//             resultIcon.className = 'result-icon fas fa-check-circle status-healthy';
//         } else {
//             resultIcon.className = 'result-icon fas fa-virus status-disease';
//         }
        
//         // Display disease information
//         if (data.disease_info) {
//             diseaseInfo.hidden = false;
            
//             // Symptoms
//             renderList(symptomsList, data.disease_info.symptoms);
            
//             // Pesticides
//             renderList(pesticidesList, data.disease_info.pesticides);
            
//             // Prevention
//             renderList(preventionList, data.disease_info.prevention);
//         } else {
//             diseaseInfo.hidden = true;
//         }
//     }
    
//     function renderList(listElement, items) {
//         listElement.innerHTML = '';
        
//         if (items && items.length > 0) {
//             items.forEach(item => {
//                 const li = document.createElement('li');
//                 li.textContent = item;
//                 listElement.appendChild(li);
//             });
//         } else {
//             const li = document.createElement('li');
//             li.textContent = 'No information available';
//             listElement.appendChild(li);
//         }
//     }
    
//     function showError(message) {
//         errorInfo.hidden = false;
//         errorMessage.textContent = message;
//         diseaseInfo.hidden = true;
//         predictionText.textContent = 'Error';
//         resultIcon.className = 'result-icon fas fa-exclamation-circle status-disease';
//         confidenceFill.style.width = '0%';
//         confidenceText.textContent = '0%';
//         resultMessage.textContent = '';
//     }
    
//     function resetResultsDisplay() {
//         errorInfo.hidden = true;
//         diseaseInfo.hidden = false;
//         symptomsList.innerHTML = '';
//         pesticidesList.innerHTML = '';
//         preventionList.innerHTML = '';
//     }
    
//     function resetUI() {
//         uploadArea.hidden = false;
//         previewContainer.hidden = true;
//         previewImage.src = '';
//         fileInput.value = '';
//     }
// });



// document.addEventListener('DOMContentLoaded', () => {
//     const fileInput = document.getElementById('fileInput');
//     const captureButton = document.getElementById('captureButton');
//     const predictButton = document.getElementById('predictButton');
//     const cameraFeed = document.getElementById('cameraFeed');
//     const canvas = document.getElementById('canvas');
//     const resultMessage = document.getElementById('resultMessage');
//     const diseaseInfo = document.getElementById('diseaseInfo');
//     const pesticideImages = document.getElementById('pesticideImages');

//     let stream;

//     // Access camera
//     captureButton.addEventListener('click', async () => {
//         try {
//             stream = await navigator.mediaDevices.getUserMedia({ video: true });
//             cameraFeed.srcObject = stream;
//             predictButton.disabled = false;
//         } catch (err) {
//             alert('Error accessing camera: ' + err.message);
//         }
//     });

//     // Capture image from camera
//     predictButton.addEventListener('click', () => {
//         canvas.width = cameraFeed.videoWidth;
//         canvas.height = cameraFeed.videoHeight;
//         canvas.getContext('2d').drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);
//         const imageData = canvas.toDataURL('image/jpeg');
        
//         // Send the captured image to the server
//         fetch('/capture', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ image: imageData }),
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.error) {
//                 resultMessage.textContent = data.error;
//                 diseaseInfo.innerHTML = '';
//                 pesticideImages.innerHTML = '';
//             } else {
//                 resultMessage.textContent = data.message;
//                 if (data.is_leaf) {
//                     // Display disease information
//                     diseaseInfo.innerHTML = `
//                         <h3>Symptoms:</h3>
//                         <ul>${data.disease_info.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
//                         <h3>Pesticides:</h3>
//                         <ul>${data.disease_info.pesticides.map(p => `<li>${p}</li>`).join('')}</ul>
//                         <h3>Prevention:</h3>
//                         <ul>${data.disease_info.prevention.map(p => `<li>${p}</li>`).join('')}</ul>
//                     `;

//                     // Display pesticide images
//                     pesticideImages.innerHTML = data.disease_info.pesticides.map(p => `
//                         <img src="C:\Users\KUNAL\OneDrive\Desktop\Final_Project\uploads\Mancozeb.jpg${p}" alt="${p}" class="pesticide-image">
//                     `).join('');
//                 } else {
//                     diseaseInfo.innerHTML = '';
//                     pesticideImages.innerHTML = '';
//                 }
//             }
//         })
//         .catch(err => {
//             resultMessage.textContent = 'Error predicting image: ' + err.message;
//             diseaseInfo.innerHTML = '';
//             pesticideImages.innerHTML = '';
//         });
//     });

//     // Upload image
//     fileInput.addEventListener('change', (e) => {
//         const file = e.target.files[0];
//         if (file) {
//             const formData = new FormData();
//             formData.append('file', file);

//             fetch('/predict', {
//                 method: 'POST',
//                 body: formData,
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.error) {
//                     resultMessage.textContent = data.error;
//                     diseaseInfo.innerHTML = '';
//                     pesticideImages.innerHTML = '';
//                 } else {
//                     resultMessage.textContent = data.message;
//                     if (data.is_leaf) {
//                         diseaseInfo.innerHTML = `
//                             <h3>Symptoms:</h3>
//                             <ul>${data.disease_info.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
//                             <h3>Pesticides:</h3>
//                             <ul>${data.disease_info.pesticides.map(p => `<li>${p}</li>`).join('')}</ul>
//                             <h3>Prevention:</h3>
//                             <ul>${data.disease_info.prevention.map(p => `<li>${p}</li>`).join('')}</ul>
//                         `;

//                         // Display pesticide images
//                         pesticideImages.innerHTML = data.disease_info.pesticides.map(p => `
//                             <img src="https://via.placeholder.com/100?text=${p}" alt="${p}" class="pesticide-image">
//                         `).join('');
//                     } else {
//                         diseaseInfo.innerHTML = '';
//                         pesticideImages.innerHTML = '';
//                     }
//                 }
//             })
//             .catch(err => {
//                 resultMessage.textContent = 'Error predicting image: ' + err.message;
//                 diseaseInfo.innerHTML = '';
//                 pesticideImages.innerHTML = '';
//             });
//         }
//     });
// });



// document.addEventListener('DOMContentLoaded', () => {
//     const fileInput = document.getElementById('fileInput');
//     const captureButton = document.getElementById('captureButton');
//     const predictButton = document.getElementById('predictButton');
//     const cameraFeed = document.getElementById('cameraFeed');
//     const canvas = document.getElementById('canvas');
//     const resultMessage = document.getElementById('resultMessage');
//     const diseaseInfo = document.getElementById('diseaseInfo');
//     const pesticideImages = document.getElementById('pesticideImages');

//     // Mapping of pesticide names to image filenames
//     const pesticideImageMap = {
//         'Mancozeb': 'Mancozeb.jpg',
//         'Myclobutanil': 'myclobutanil.jpg',
//         'Captan': 'captain.jpg',
//         'Copper Oxychloride': 'kocide3000.jpg'
//     };

//     let stream;

//     // Access camera
//     captureButton.addEventListener('click', async () => {
//         try {
//             stream = await navigator.mediaDevices.getUserMedia({ video: true });
//             cameraFeed.srcObject = stream;
//             predictButton.disabled = false;
//         } catch (err) {
//             alert('Error accessing camera: ' + err.message);
//         }
//     });

//     // Capture image from camera
//     predictButton.addEventListener('click', () => {
//         canvas.width = cameraFeed.videoWidth;
//         canvas.height = cameraFeed.videoHeight;
//         canvas.getContext('2d').drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);
//         const imageData = canvas.toDataURL('image/jpeg');
        
//         // Send the captured image to the server
//         fetch('/capture', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ image: imageData }),
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.error) {
//                 resultMessage.textContent = data.error;
//                 diseaseInfo.innerHTML = '';
//                 pesticideImages.innerHTML = '';
//             } else {
//                 resultMessage.textContent = data.message;
//                 if (data.is_leaf) {
//                     // Display disease information
//                     diseaseInfo.innerHTML = `
//                         <h3>Symptoms:</h3>
//                         <ul>${data.disease_info.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
//                         <h3>Pesticides:</h3>
//                         <ul>${data.disease_info.pesticides.map(p => `<li>${p}</li>`).join('')}</ul>
//                         <h3>Prevention:</h3>
//                         <ul>${data.disease_info.prevention.map(p => `<li>${p}</li>`).join('')}</ul>
//                     `;

//                     // Display pesticide images for Black Rot
//                     if (data.prediction === 'Black Rot') {
//                         pesticideImages.innerHTML = data.disease_info.pesticides.map(p => `
//                             <div class="pesticide-container">
//                                 <img src="/static/pesticides/${pesticideImageMap[p]}" alt="${p}" class="pesticide-image">
//                                 <p>${p}</p>
//                             </div>
//                         `).join('');
//                     } else {
//                         pesticideImages.innerHTML = '';
//                     }
//                 } else {
//                     diseaseInfo.innerHTML = '';
//                     pesticideImages.innerHTML = '';
//                 }
//             }
//         })
//         .catch(err => {
//             resultMessage.textContent = 'Error predicting image: ' + err.message;
//             diseaseInfo.innerHTML = '';
//             pesticideImages.innerHTML = '';
//         });
//     });

//     // Upload image
//     fileInput.addEventListener('change', (e) => {
//         const file = e.target.files[0];
//         if (file) {
//             const formData = new FormData();
//             formData.append('file', file);

//             fetch('/predict', {
//                 method: 'POST',
//                 body: formData,
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.error) {
//                     resultMessage.textContent = data.error;
//                     diseaseInfo.innerHTML = '';
//                     pesticideImages.innerHTML = '';
//                 } else {
//                     resultMessage.textContent = data.message;
//                     if (data.is_leaf) {
//                         diseaseInfo.innerHTML = `
//                             <h3>Symptoms:</h3>
//                             <ul>${data.disease_info.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
//                             <h3>Pesticides:</h3>
//                             <ul>${data.disease_info.pesticides.map(p => `<li>${p}</li>`).join('')}</ul>
//                             <h3>Prevention:</h3>
//                             <ul>${data.disease_info.prevention.map(p => `<li>${p}</li>`).join('')}</ul>
//                         `;

//                         // Display pesticide images for Black Rot
//                         if (data.prediction === 'Black Rot') {
//                             pesticideImages.innerHTML = data.disease_info.pesticides.map(p => `
//                                 <div class="pesticide-container">
//                                     <img src="/static/pesticides/${pesticideImageMap[p]}" alt="${p}" class="pesticide-image">
//                                     <p>${p}</p>
//                                 </div>
//                             `).join('');
//                         } else {
//                             pesticideImages.innerHTML = '';
//                         }
//                     } else {
//                         diseaseInfo.innerHTML = '';
//                         pesticideImages.innerHTML = '';
//                     }
//                 }
//             })
//             .catch(err => {
//                 resultMessage.textContent = 'Error predicting image: ' + err.message;
//                 diseaseInfo.innerHTML = '';
//                 pesticideImages.innerHTML = '';
//             });
//         }
//     });
// });


document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const captureButton = document.getElementById('captureButton');
    const predictButton = document.getElementById('predictButton');
    const cameraFeed = document.getElementById('cameraFeed');
    const canvas = document.getElementById('canvas');
    const resultMessage = document.getElementById('resultMessage');
    const diseaseInfo = document.getElementById('diseaseInfo');

    // Define the diseases and their recommended products
    const diseaseProducts = {
        'Black Rot': [
            {
                name: 'BlackGuard Fungicide',
                image: 'captain.jpg',
                price: '246.99 INR',
                description: 'Effective against black rot in grape vines',
                url: '/product/blackguard-fungicide'
            },
            {
                name: 'Grape Shield Pro',
                image: 'Mancozeb.jpg',
                price: '832.50 INR',
                description: 'Advanced formula for black rot control',
                url: '/product/grape-shield-pro'
            }
        ],
        'Powdery Mildew': [
            {
                name: 'Mildew Combat Formula',
                image: 'fungicide3.jpg',
                price: '119.99 INR',
                description: 'Specialized treatment for powdery mildew',
                url: '/product/mildew-combat'
            },
            {
                name: 'PowerClean Spray',
                image: 'fungicide4.jpg',
                price: '279.99 INR',
                description: 'Fast-acting mildew control solution',
                url: '/product/powerclean-spray'
            }
        ],
        'Leaf Blight': [
            {
                name: 'Blight Fighter',
                image: 'myclobutanil.jpg',
                price: '22.50 INR',
                description: 'Protect your vines against leaf blight',
                url: '/product/blight-fighter'
            }
        ],
        'ESCA': [
            {
                name: 'ESCA Treatment Solution',
                image: 'Ranman400SC.jpg',
                price: '929.99 INR',
                description: 'Specialized formula for ESCA disease control',
                url: '/product/esca-treatment'
            }
        ],
        'Healthy': [
            {
                name: 'Preventative Care Kit',
                image: 'preventative.jpg',
                price: '18.99 INR',
                description: 'Keep your healthy vines in top condition',
                url: '/product/preventative-care'
            }
        ]
    };

    let stream;

    // Access camera
    captureButton.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            cameraFeed.srcObject = stream;
            predictButton.disabled = false;
        } catch (err) {
            alert('Error accessing camera: ' + err.message);
        }
    });

    // Capture image from camera
    predictButton.addEventListener('click', () => {
        canvas.width = cameraFeed.videoWidth;
        canvas.height = cameraFeed.videoHeight;
        canvas.getContext('2d').drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        
        // Send the captured image to the server
        fetch('/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultMessage.textContent = data.error;
                diseaseInfo.innerHTML = '';
                hideEcommerceInfo();
            } else {
                resultMessage.textContent = data.message;
                if (data.is_leaf) {
                    // Display disease information
                    diseaseInfo.innerHTML = `
                        <h3>Symptoms:</h3>
                        <ul>${data.disease_info.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
                        <h3>Pesticides:</h3>
                        <ul>${data.disease_info.pesticides.map(p => `<li>${p}</li>`).join('')}</ul>
                        <h3>Prevention:</h3>
                        <ul>${data.disease_info.prevention.map(p => `<li>${p}</li>`).join('')}</ul>
                    `;

                    // Display e-commerce recommendations
                    displayEcommerceInfo(data.prediction);
                } else {
                    diseaseInfo.innerHTML = '';
                    hideEcommerceInfo();
                }
            }
        })
        .catch(err => {
            resultMessage.textContent = 'Error predicting image: ' + err.message;
            diseaseInfo.innerHTML = '';
            hideEcommerceInfo();
        });
    });

    // Upload image
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/predict', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultMessage.textContent = data.error;
                    diseaseInfo.innerHTML = '';
                    hideEcommerceInfo();
                } else {
                    resultMessage.textContent = data.message;
                    if (data.is_leaf) {
                        diseaseInfo.innerHTML = `
                            <h3>Symptoms:</h3>
                            <ul>${data.disease_info.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
                            <h3>Pesticides:</h3>
                            <ul>${data.disease_info.pesticides.map(p => `<li>${p}</li>`).join('')}</ul>
                            <h3>Prevention:</h3>
                            <ul>${data.disease_info.prevention.map(p => `<li>${p}</li>`).join('')}</ul>
                        `;

                        // Display e-commerce recommendations
                        displayEcommerceInfo(data.prediction);
                    } else {
                        diseaseInfo.innerHTML = '';
                        hideEcommerceInfo();
                    }
                }
            })
            .catch(err => {
                resultMessage.textContent = 'Error predicting image: ' + err.message;
                diseaseInfo.innerHTML = '';
                hideEcommerceInfo();
            });
        }
    });

    // Function to display e-commerce recommendations
    function displayEcommerceInfo(disease) {
        const ecommerceInfo = document.getElementById('ecommerceInfo');
        const pesticideOptions = ecommerceInfo.querySelector('.pesticide-options');
        const shopNowButton = document.getElementById('shopNowButton');
        
        // Show the e-commerce section
        ecommerceInfo.style.display = 'block';
        
        // Get products for this disease
        const products = diseaseProducts[disease] || diseaseProducts['Healthy'];
        
        // Build the product cards
        let productsHTML = '';
        products.forEach(product => {
            productsHTML += `
                <div class="pesticide-card">
                    <img src="/static/pesticides/${product.image}" alt="${product.name}">
                    <h4>${product.name}</h4>
                    <div class="price">${product.price}</div>
                    <p>${product.description}</p>
                    <a href="/shop" class="view-product" target="_blank">View Details</a>
                </div>
            `;
        });
        
        // Insert the product cards
        pesticideOptions.innerHTML = productsHTML;
        
        // Update the main shop button
        shopNowButton.href = `/shop?disease=${disease}`;
    }

    // Function to hide e-commerce info
    function hideEcommerceInfo() {
        const ecommerceInfo = document.getElementById('ecommerceInfo');
        ecommerceInfo.style.display = 'none';
    }
});