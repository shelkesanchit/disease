/**
 * Main JavaScript file for the Grape Farm Planner application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize 3D animations if the container exists
    initFarm3DAnimation();

    // Password confirmation validation
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    if (passwordField && confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            if (passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity("Passwords don't match");
            } else {
                confirmPasswordField.setCustomValidity('');
            }
        });
        
        passwordField.addEventListener('input', function() {
            if (passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity("Passwords don't match");
            } else {
                confirmPasswordField.setCustomValidity('');
            }
        });
    }

    // Task checkbox handling
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.getAttribute('data-task-id');
            const scheduleId = this.getAttribute('data-schedule-id');
            const status = this.checked ? 'completed' : 'pending';
            
            // Update task status via API
            fetch(`/api/task/${scheduleId}/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    const taskItem = document.querySelector(`.task-item[data-task-id="${taskId}"]`);
                    if (taskItem) {
                        if (status === 'completed') {
                            taskItem.classList.add('completed');
                        } else {
                            taskItem.classList.remove('completed');
                        }
                    }
                }
            })
            .catch(error => console.error('Error updating task status:', error));
        });
    });

    // Weather refresh button
    const refreshWeatherBtn = document.getElementById('refresh-weather');
    if (refreshWeatherBtn) {
        refreshWeatherBtn.addEventListener('click', function() {
            const locationSpan = document.querySelector('.weather-location');
            const location = locationSpan ? locationSpan.textContent.trim() : '';
            
            if (location) {
                this.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i>';
                
                fetch(`/api/weather/${location}`)
                    .then(response => response.json())
                    .then(data => {
                        // Reload the page to show updated weather
                        window.location.reload();
                    })
                    .catch(error => {
                        console.error('Error fetching weather data:', error);
                        this.innerHTML = '<i class="fas fa-sync-alt"></i>';
                    });
            }
        });
    }

    // PDF export button
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Generating...';
            this.disabled = true;
            
            fetch(this.href)
                .then(response => response.json())
                .then(data => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                    
                    if (data.download_url) {
                        // Redirect to download URL
                        window.location.href = data.download_url;
                    } else {
                        alert('PDF generated successfully. You can download it now.');
                    }
                })
                .catch(error => {
                    console.error('Error generating PDF:', error);
                    this.innerHTML = originalText;
                    this.disabled = false;
                    alert('Error generating PDF. Please try again later.');
                });
        });
    }

    // Alert dismissal
    const alertsItems = document.querySelectorAll('[data-alert-id]');
    alertsItems.forEach(item => {
        item.addEventListener('click', function() {
            const alertId = this.getAttribute('data-alert-id');
            
            fetch(`/api/alerts/${alertId}/read`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.classList.remove('fw-bold');
                    
                    // Update alerts counter
                    const alertsBadge = document.querySelector('.alert-badge');
                    if (alertsBadge) {
                        const currentCount = parseInt(alertsBadge.textContent);
                        if (currentCount > 1) {
                            alertsBadge.textContent = currentCount - 1;
                        } else {
                            alertsBadge.style.display = 'none';
                        }
                    }
                }
            })
            .catch(error => console.error('Error marking alert as read:', error));
        });
    });

    // Farm layout preview in new farm form
    const farmForm = document.getElementById('farmForm');
    if (farmForm) {
        const farmLength = document.getElementById('farm_length');
        const farmWidth = document.getElementById('farm_width');
        const plantWidthSpacing = document.getElementById('plant_width_spacing');
        const plantLengthSpacing = document.getElementById('plant_length_spacing');
        const grapeVariety = document.getElementById('grape_variety');
        
        // Auto-fill spacing based on grape variety
        if (grapeVariety) {
            grapeVariety.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                const widthSpacing = selectedOption.getAttribute('data-width-spacing');
                const lengthSpacing = selectedOption.getAttribute('data-length-spacing');
                
                if (widthSpacing && lengthSpacing) {
                    plantWidthSpacing.value = widthSpacing;
                    plantLengthSpacing.value = lengthSpacing;
                    updateLayoutPreview();
                }
            });
        }
        
        // Update layout preview when dimensions change
        [farmLength, farmWidth, plantWidthSpacing, plantLengthSpacing].forEach(element => {
            if (element) {
                element.addEventListener('input', updateLayoutPreview);
            }
        });
        
        function updateLayoutPreview() {
            const layoutCanvas = document.getElementById('layoutCanvas');
            const layoutMessage = document.getElementById('layoutMessage');
            const layoutStats = document.getElementById('layoutStats');
            
            if (!layoutCanvas || !layoutMessage || !layoutStats) return;
            
            const length = parseFloat(farmLength.value) || 0;
            const width = parseFloat(farmWidth.value) || 0;
            const pws = parseFloat(plantWidthSpacing.value) || 0;
            const pls = parseFloat(plantLengthSpacing.value) || 0;
            
            if (length > 0 && width > 0 && pws > 0 && pls > 0) {
                // Show canvas and hide message
                layoutCanvas.style.display = 'block';
                layoutMessage.style.display = 'none';
                layoutStats.style.display = 'block';
                
                // Calculate farm layout
                const data = {
                    farmLength: length,
                    farmWidth: width,
                    plantWidthSpacing: pws,
                    plantLengthSpacing: pls
                };
                
                fetch('/api/farm/layout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    const layout = data.layout;
                    const totalPlants = document.getElementById('totalPlants');
                    const rowsCols = document.getElementById('rowsCols');
                    const utilizationRate = document.getElementById('utilizationRate');
                    const totalArea = document.getElementById('totalArea');
                    
                    // Update stats
                    if (totalPlants) totalPlants.textContent = layout.max_capacity;
                    if (rowsCols) rowsCols.textContent = `${layout.max_plants_length} × ${layout.max_plants_width}`;
                    if (utilizationRate) utilizationRate.textContent = `${layout.utilization.toFixed(1)}%`;
                    if (totalArea) totalArea.textContent = `${layout.total_area.toFixed(1)} m²`;
                    
                    // Draw layout preview
                    drawLayoutPreview(layout);
                })
                .catch(error => {
                    console.error('Error calculating layout:', error);
                    layoutCanvas.style.display = 'none';
                    layoutMessage.style.display = 'block';
                    layoutMessage.textContent = 'Error calculating layout';
                });
            } else {
                // Hide canvas and show message
                layoutCanvas.style.display = 'none';
                layoutMessage.style.display = 'block';
                layoutStats.style.display = 'none';
            }
        }
        
        function drawLayoutPreview(layout) {
            const canvas = document.getElementById('layoutCanvas');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            
            // Set canvas dimensions
            const maxSize = 200;
            const aspectRatio = layout.total_area > 0 ? 
                Math.min(layout.used_width / layout.used_length, layout.used_length / layout.used_width) : 1;
            
            if (layout.used_width > layout.used_length) {
                canvas.width = maxSize;
                canvas.height = maxSize * aspectRatio;
            } else {
                canvas.height = maxSize;
                canvas.width = maxSize * aspectRatio;
            }
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Calculate scales
            const canvasWidth = canvas.width;
            const canvasHeight = canvas.height;
            const scaleX = canvasWidth / layout.total_area * layout.used_length;
            const scaleY = canvasHeight / layout.total_area * layout.used_width;
            
            // Draw unused area (light green)
            ctx.fillStyle = '#e8f5e9';
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Draw used area (darker green)
            ctx.fillStyle = '#81c784';
            ctx.fillRect(
                (canvasWidth - (layout.used_length * scaleX)) / 2,
                (canvasHeight - (layout.used_width * scaleY)) / 2,
                layout.used_length * scaleX,
                layout.used_width * scaleY
            );
            
            // Draw plants
            const plantRadius = Math.min(2, 
                Math.min(
                    (layout.used_length * scaleX) / (layout.max_plants_length * 4),
                    (layout.used_width * scaleY) / (layout.max_plants_width * 4)
                )
            );
            
            ctx.fillStyle = '#2e7d32';
            
            const startX = (canvasWidth - (layout.used_length * scaleX)) / 2;
            const startY = (canvasHeight - (layout.used_width * scaleY)) / 2;
            
            for (let row = 0; row < layout.max_plants_width; row++) {
                for (let col = 0; col < layout.max_plants_length; col++) {
                    const x = startX + (col * layout.plant_length_spacing + layout.plant_length_spacing/2) * scaleX;
                    const y = startY + (row * layout.plant_width_spacing + layout.plant_width_spacing/2) * scaleY;
                    
                    ctx.beginPath();
                    ctx.arc(x, y, plantRadius, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }
    }
});

/**
 * Initialize 3D Farm Animation using Three.js
 */
function initFarm3DAnimation() {
    const animationContainer = document.getElementById('farm-3d-animation');
    if (!animationContainer) return;
    
    // Set up the scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf1f8e9);
    
    // Set up camera
    const camera = new THREE.PerspectiveCamera(75, animationContainer.clientWidth / animationContainer.clientHeight, 0.1, 1000);
    camera.position.z = 15;
    camera.position.y = 5;
    
    // Set up renderer with antialiasing and better shadows
    const renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true
    });
    renderer.setSize(animationContainer.clientWidth, animationContainer.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    animationContainer.appendChild(renderer.domElement);
    
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    // Add directional light (sunlight)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(15, 25, 15);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    scene.add(directionalLight);
    
    // Add a subtle spotlight for dramatic effect
    const spotLight = new THREE.SpotLight(0xf39c12, 0.8);
    spotLight.position.set(-15, 20, 15);
    spotLight.angle = Math.PI / 6;
    spotLight.penumbra = 0.5;
    spotLight.castShadow = true;
    scene.add(spotLight);
    
    // Create ground (field)
    const groundGeometry = new THREE.PlaneGeometry(40, 40);
    const groundMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x27ae60,
        roughness: 0.8,
        metalness: 0.2
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -2;
    ground.receiveShadow = true;
    scene.add(ground);
    
    // Create a dirt path through vineyard
    const pathGeometry = new THREE.PlaneGeometry(2, 30);
    const pathMaterial = new THREE.MeshStandardMaterial({ 
        color: 0xb7845e,
        roughness: 0.9,
        metalness: 0
    });
    const path = new THREE.Mesh(pathGeometry, pathMaterial);
    path.rotation.x = -Math.PI / 2;
    path.position.y = -1.95;
    path.receiveShadow = true;
    scene.add(path);
    
    // Create vineyard rows
    const rows = 6;
    const plantsPerRow = 8;
    const spacing = 2.2;
    
    // Create plants group
    const plantsGroup = new THREE.Group();
    scene.add(plantsGroup);
    
    // Function to create a grape plant
    function createGrapePlant(x, z) {
        const plant = new THREE.Group();
        
        // Create trunk
        const trunkGeometry = new THREE.CylinderGeometry(0.1, 0.15, 1.5, 8);
        const trunkMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x8d6e63,
            roughness: 0.9
        });
        const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
        trunk.position.y = 0.75;
        trunk.castShadow = true;
        plant.add(trunk);
        
        // Create foliage (leaves)
        const foliageGeometry = new THREE.SphereGeometry(0.8, 10, 10);
        foliageGeometry.scale(1, 0.7, 1);
        
        // Use different shades of green for variety
        const greenColors = [0x2ecc71, 0x27ae60, 0x1e8449];
        const randomGreen = greenColors[Math.floor(Math.random() * greenColors.length)];
        
        const foliageMaterial = new THREE.MeshStandardMaterial({ 
            color: randomGreen,
            roughness: 0.8
        });
        const foliage = new THREE.Mesh(foliageGeometry, foliageMaterial);
        foliage.position.y = 1.6;
        foliage.castShadow = true;
        plant.add(foliage);
        
        // Create grapes
        if (Math.random() > 0.3) {
            // Random choice between purple and golden grapes
            const grapeColors = [0x9b59b6, 0xf1c40f];
            const grapeColor = Math.random() > 0.5 ? grapeColors[0] : grapeColors[1];
            
            const grapeGeometry = new THREE.SphereGeometry(0.25, 8, 8);
            const grapeMaterial = new THREE.MeshStandardMaterial({ 
                color: grapeColor,
                roughness: 0.5,
                metalness: 0.2
            });
            const grapes = new THREE.Mesh(grapeGeometry, grapeMaterial);
            grapes.position.set(0.6, 1.4, 0.2);
            grapes.castShadow = true;
            plant.add(grapes);
            
            const grapes2 = new THREE.Mesh(grapeGeometry, grapeMaterial);
            grapes2.position.set(-0.5, 1.3, 0.3);
            grapes2.castShadow = true;
            plant.add(grapes2);
        }
        
        // Position the plant
        plant.position.set(x, 0, z);
        
        return plant;
    }
    
    // Create vineyard
    for (let row = 0; row < rows; row++) {
        for (let plant = 0; plant < plantsPerRow; plant++) {
            const x = (row - rows/2) * spacing + Math.random() * 0.2;
            const z = (plant - plantsPerRow/2) * spacing + Math.random() * 0.2;
            // Skip plants in the middle for the path
            if (Math.abs(x) < 0.8) continue;
            const grapePlant = createGrapePlant(x, z);
            plantsGroup.add(grapePlant);
        }
    }
    
    // Create tractor
    function createTractor() {
        const tractor = new THREE.Group();
        
        // Tractor body
        const bodyGeometry = new THREE.BoxGeometry(1.8, 1.2, 2.4);
        const bodyMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x1e8449,
            roughness: 0.7,
            metalness: 0.3
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 1.1;
        body.castShadow = true;
        body.receiveShadow = true;
        tractor.add(body);
        
        // Tractor cab
        const cabGeometry = new THREE.BoxGeometry(1.4, 1, 1.2);
        const cabMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x145a32,
            metalness: 0.4,
            roughness: 0.6
        });
        const cab = new THREE.Mesh(cabGeometry, cabMaterial);
        cab.position.set(0, 2, -0.4);
        cab.castShadow = true;
        cab.receiveShadow = true;
        tractor.add(cab);
        
        // Tractor cab window
        const windowGeometry = new THREE.BoxGeometry(1.2, 0.7, 0.1);
        const windowMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x3498db,
            metalness: 0.8,
            roughness: 0.2,
            transparent: true,
            opacity: 0.6
        });
        const frontWindow = new THREE.Mesh(windowGeometry, windowMaterial);
        frontWindow.position.set(0, 2, 0.2);
        tractor.add(frontWindow);
        
        // Tractor grille
        const grilleGeometry = new THREE.BoxGeometry(1.4, 0.5, 0.1);
        const grilleMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x34495e,
            roughness: 0.4,
            metalness: 0.6
        });
        const grille = new THREE.Mesh(grilleGeometry, grilleMaterial);
        grille.position.set(0, 0.8, 1.2);
        tractor.add(grille);
        
        // Tractor headlights
        const headlightGeometry = new THREE.CircleGeometry(0.15, 16);
        const headlightMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xf1c40f,
            emissive: 0xf1c40f,
            emissiveIntensity: 0.5
        });
        
        const leftHeadlight = new THREE.Mesh(headlightGeometry, headlightMaterial);
        leftHeadlight.position.set(-0.5, 1, 1.25);
        leftHeadlight.rotation.y = Math.PI;
        tractor.add(leftHeadlight);
        
        const rightHeadlight = new THREE.Mesh(headlightGeometry, headlightMaterial);
        rightHeadlight.position.set(0.5, 1, 1.25);
        rightHeadlight.rotation.y = Math.PI;
        tractor.add(rightHeadlight);
        
        // Wheels
        const wheelGeometry = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 16);
        wheelGeometry.rotateZ(Math.PI/2);
        const wheelMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x212121,
            roughness: 0.7
        });
        
        const wheelPositions = [
            [-0.9, 0.5, -0.8],
            [0.9, 0.5, -0.8],
            [-0.9, 0.6, 0.8],
            [0.9, 0.6, 0.8]
        ];
        
        const wheels = [];
        wheelPositions.forEach((pos, index) => {
            const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
            wheel.position.set(...pos);
            wheel.castShadow = true;
            wheel.receiveShadow = true;
            tractor.add(wheel);
            wheels.push(wheel);
        });
        
        // Add wheel hubs
        wheelPositions.forEach((pos, index) => {
            const hubGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.42, 16);
            hubGeometry.rotateZ(Math.PI/2);
            const hubMaterial = new THREE.MeshStandardMaterial({ 
                color: 0xf39c12,
                roughness: 0.5,
                metalness: 0.6
            });
            const hub = new THREE.Mesh(hubGeometry, hubMaterial);
            hub.position.set(...pos);
            tractor.add(hub);
        });
        
        // Position tractor outside the field, ready to move in
        tractor.position.set(-15, 0, 0);
        tractor.rotation.y = Math.PI/2;
        
        // Store wheels for animation
        tractor.wheels = wheels;
        
        return tractor;
    }
    
    const tractor = createTractor();
    scene.add(tractor);
    
    // Create farmer (simple figure)
    function createFarmer() {
        const farmer = new THREE.Group();
        
        // Body
        const bodyGeometry = new THREE.CylinderGeometry(0.25, 0.25, 0.7, 8);
        const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.65;
        body.castShadow = true;
        farmer.add(body);
        
        // Head
        const headGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const headMaterial = new THREE.MeshStandardMaterial({ color: 0xe8beac });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.2;
        head.castShadow = true;
        farmer.add(head);
        
        // Hat
        const hatGeometry = new THREE.ConeGeometry(0.25, 0.25, 8);
        const hatMaterial = new THREE.MeshStandardMaterial({ color: 0xf39c12 });
        const hat = new THREE.Mesh(hatGeometry, hatMaterial);
        hat.position.y = 1.4;
        hat.castShadow = true;
        farmer.add(hat);
        
        // Arms
        const armGeometry = new THREE.CylinderGeometry(0.05, 0.05, 0.5, 8);
        const armMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db });
        
        const leftArm = new THREE.Mesh(armGeometry, armMaterial);
        leftArm.position.set(-0.35, 0.8, 0);
        leftArm.rotation.z = Math.PI / 4;
        leftArm.castShadow = true;
        farmer.add(leftArm);
        
        const rightArm = new THREE.Mesh(armGeometry, armMaterial);
        rightArm.position.set(0.35, 0.8, 0);
        rightArm.rotation.z = -Math.PI / 4;
        rightArm.castShadow = true;
        farmer.add(rightArm);
        
        // Legs
        const legGeometry = new THREE.CylinderGeometry(0.07, 0.07, 0.5, 8);
        const legMaterial = new THREE.MeshStandardMaterial({ color: 0x34495e });
        
        const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
        leftLeg.position.set(-0.15, 0.25, 0);
        leftLeg.castShadow = true;
        farmer.add(leftLeg);
        
        const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
        rightLeg.position.set(0.15, 0.25, 0);
        rightLeg.castShadow = true;
        farmer.add(rightLeg);
        
        // Position farmer
        farmer.position.set(5, 0, 2);
        
        return farmer;
    }
    
    const farmer = createFarmer();
    scene.add(farmer);
    
    // Create birds
    function createBird() {
        const bird = new THREE.Group();
        
        // Body
        const bodyGeometry = new THREE.SphereGeometry(0.15, 8, 8);
        bodyGeometry.scale(1, 0.6, 1.5);
        const bodyMaterial = new THREE.MeshStandardMaterial({ 
            color: Math.random() > 0.5 ? 0x3498db : 0xe74c3c
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.castShadow = true;
        bird.add(body);
        
        // Wings
        const wingGeometry = new THREE.BoxGeometry(0.5, 0.02, 0.2);
        const wingMaterial = new THREE.MeshStandardMaterial({ 
            color: bodyMaterial.color,
            roughness: 0.9
        });
        
        const leftWing = new THREE.Mesh(wingGeometry, wingMaterial);
        leftWing.position.set(-0.25, 0, 0);
        leftWing.castShadow = true;
        bird.add(leftWing);
        
        const rightWing = new THREE.Mesh(wingGeometry, wingMaterial);
        rightWing.position.set(0.25, 0, 0);
        rightWing.castShadow = true;
        bird.add(rightWing);
        
        // Head
        const headGeometry = new THREE.SphereGeometry(0.08, 8, 8);
        const headMaterial = new THREE.MeshStandardMaterial({ 
            color: bodyMaterial.color
        });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.set(0, 0, 0.15);
        head.castShadow = true;
        bird.add(head);
        
        // Beak
        const beakGeometry = new THREE.ConeGeometry(0.03, 0.1, 8);
        beakGeometry.rotateX(Math.PI / 2);
        const beakMaterial = new THREE.MeshStandardMaterial({ color: 0xf39c12 });
        const beak = new THREE.Mesh(beakGeometry, beakMaterial);
        beak.position.set(0, 0, 0.22);
        bird.add(beak);
        
        // Position bird at random location in the sky
        bird.position.set(
            Math.random() * 30 - 15,
            Math.random() * 5 + 5,
            Math.random() * 30 - 15
        );
        
        // Store original position and random movement pattern
        bird.originalPosition = {...bird.position};
        bird.flightRadius = Math.random() * 3 + 2;
        bird.flightSpeed = Math.random() * 0.001 + 0.001;
        bird.flightOffset = Math.random() * Math.PI * 2;
        bird.wings = { left: leftWing, right: rightWing };
        bird.wingSpeed = Math.random() * 0.1 + 0.1;
        
        return bird;
    }
    
    // Add a flock of birds
    const birds = [];
    for (let i = 0; i < 8; i++) {
        const bird = createBird();
        scene.add(bird);
        birds.push(bird);
    }
    
    // Create clouds
    function createCloud() {
        const cloud = new THREE.Group();
        const cloudMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xffffff,
            roughness: 0.5,
            transparent: true,
            opacity: 0.9
        });
        
        // Add 3-5 sphere geometries clustered together for the cloud
        const numPuffs = Math.floor(Math.random() * 3) + 4;
        for (let i = 0; i < numPuffs; i++) {
            const size = Math.random() * 1 + 0.8;
            const puffGeometry = new THREE.SphereGeometry(size, 7, 7);
            const puff = new THREE.Mesh(puffGeometry, cloudMaterial);
            
            // Random position within the cloud cluster
            puff.position.set(
                Math.random() * 3 - 1.5,
                Math.random() * 0.5,
                Math.random() * 3 - 1.5
            );
            
            cloud.add(puff);
        }
        
        // Random position in the sky
        cloud.position.set(
            Math.random() * 50 - 25,
            Math.random() * 8 + 12,
            Math.random() * 50 - 25
        );
        
        // Store original position for movement
        cloud.originalPosition = {...cloud.position};
        cloud.driftSpeed = Math.random() * 0.002 + 0.001;
        
        return cloud;
    }
    
    // Add clouds
    const clouds = [];
    for (let i = 0; i < 8; i++) {
        const cloud = createCloud();
        scene.add(cloud);
        clouds.push(cloud);
    }
    
    // Create sun
    const sunGeometry = new THREE.SphereGeometry(2, 16, 16);
    const sunMaterial = new THREE.MeshBasicMaterial({ 
        color: 0xf39c12,
        transparent: true,
        opacity: 0.9
    });
    const sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.position.set(30, 25, -30);
    scene.add(sun);
    
    // Create sun rays (glow effect)
    const sunLightGeometry = new THREE.SphereGeometry(3, 16, 16);
    const sunLightMaterial = new THREE.MeshBasicMaterial({ 
        color: 0xf39c12,
        transparent: true,
        opacity: 0.4
    });
    const sunLight = new THREE.Mesh(sunLightGeometry, sunLightMaterial);
    sun.add(sunLight);
    
    // Animation variables
    let tractorMoving = true;
    let tractorDirection = 1;
    let farmerDirection = 1;
    let farmerMoving = true;
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotate the plants group for a more dynamic "breathing" effect
        plantsGroup.children.forEach((plant, index) => {
            plant.rotation.z = Math.sin(Date.now() * 0.001 + index * 0.1) * 0.05;
            plant.rotation.x = Math.sin(Date.now() * 0.0008 + index * 0.1) * 0.02;
        });
        
        // Animate tractor
        if (tractorMoving) {
            tractor.position.x += 0.06 * tractorDirection;
            
            // Change direction at edges
            if (tractor.position.x > 12) {
                tractorDirection = -1;
                tractor.rotation.y = -Math.PI/2;
            } else if (tractor.position.x < -12) {
                tractorDirection = 1;
                tractor.rotation.y = Math.PI/2;
            }
        }
        
        // Animate farmer
        if (farmerMoving) {
            farmer.position.z += 0.02 * farmerDirection;
            // Simple walking animation
            farmer.rotation.y = farmerDirection > 0 ? Math.PI : 0;
            
            // Change direction
            if (farmer.position.z > 6) {
                farmerDirection = -1;
            } else if (farmer.position.z < -2) {
                farmerDirection = 1;
            }
        }
        
        // Animate birds
        birds.forEach(bird => {
            // Circular flight pattern
            bird.position.x = bird.originalPosition.x + Math.sin(Date.now() * bird.flightSpeed + bird.flightOffset) * bird.flightRadius;
            bird.position.z = bird.originalPosition.z + Math.cos(Date.now() * bird.flightSpeed + bird.flightOffset) * bird.flightRadius;
            bird.position.y = bird.originalPosition.y + Math.sin(Date.now() * bird.flightSpeed * 2) * 0.5;
            
            // Rotate bird in direction of movement
            bird.rotation.y = Math.atan2(
                (bird.position.x - bird.previousX) || 0.01,
                (bird.position.z - bird.previousZ) || 0.01
            );
            
            // Store position for next frame
            bird.previousX = bird.position.x;
            bird.previousZ = bird.position.z;
            
            // Flap wings
            const wingAngle = Math.sin(Date.now() * bird.wingSpeed) * 0.3;
            bird.wings.left.rotation.z = wingAngle;
            bird.wings.right.rotation.z = -wingAngle;
        });
        
        // Animate clouds
        clouds.forEach(cloud => {
            cloud.position.x = cloud.originalPosition.x + Math.sin(Date.now() * cloud.driftSpeed) * 8;
            // Subtle vertical movement
            cloud.position.y = cloud.originalPosition.y + Math.sin(Date.now() * cloud.driftSpeed * 0.5) * 0.5;
        });
        
        // Animate sun
        sun.rotation.z += 0.001;
        sunLight.scale.set(
            1 + Math.sin(Date.now() * 0.001) * 0.1,
            1 + Math.sin(Date.now() * 0.001) * 0.1,
            1 + Math.sin(Date.now() * 0.001) * 0.1
        );
        
        // Gently rotate the camera for a more dynamic and immersive view
        camera.position.x = Math.sin(Date.now() * 0.0003) * 6;
        camera.position.z = Math.cos(Date.now() * 0.0003) * 15 + 5;
        camera.position.y = 5 + Math.sin(Date.now() * 0.0005) * 1;
        camera.lookAt(0, 1, 0);
        
        renderer.render(scene, camera);
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (!animationContainer) return;
        
        const width = animationContainer.clientWidth;
        const height = animationContainer.clientHeight;
        
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });
    
    // Start animation loop
    animate();
}