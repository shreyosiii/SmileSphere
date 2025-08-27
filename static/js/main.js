// SmileSphere Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            const closeButton = flash.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Handle photo upload preview
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photo-preview');
    const previewContainer = document.getElementById('preview-container');

    if (photoInput && photoPreview && previewContainer) {
        photoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    photoPreview.src = e.target.result;
                    previewContainer.classList.remove('d-none');
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Camera functionality for photo upload
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-btn');
    const retakeBtn = document.getElementById('retake-btn');
    const cameraContainer = document.getElementById('camera-container');
    const cameraTab = document.getElementById('camera-tab');
    const uploadTab = document.getElementById('upload-tab');
    const capturedImageInput = document.getElementById('captured-image');
    
    if (video && canvas && captureBtn && retakeBtn && cameraTab) {
        let stream = null;

        // Start camera when camera tab is clicked
        cameraTab.addEventListener('click', function() {
            startCamera();
        });

        // Stop camera when upload tab is clicked
        if (uploadTab) {
            uploadTab.addEventListener('click', function() {
                stopCamera();
            });
        }

        // Start camera function
        function startCamera() {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(function(mediaStream) {
                        stream = mediaStream;
                        video.srcObject = mediaStream;
                        video.play();
                    })
                    .catch(function(err) {
                        console.log("Error accessing camera: " + err);
                        alert("Error accessing camera. Please make sure you've granted camera permissions.");
                    });
            } else {
                alert("Your browser doesn't support camera access. Please use the file upload option.");
            }
        }

        // Stop camera function
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => {
                    track.stop();
                });
                video.srcObject = null;
                stream = null;
            }
        }

        // Capture photo
        if (captureBtn) {
            captureBtn.addEventListener('click', function() {
                if (stream) {
                    // Add taking-photo class for shutter animation
                    if (cameraContainer) {
                        cameraContainer.classList.add('taking-photo');
                        setTimeout(() => {
                            cameraContainer.classList.remove('taking-photo');
                        }, 500);
                    }
                    
                    const context = canvas.getContext('2d');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    const imageDataURL = canvas.toDataURL('image/png');
                    if (capturedImageInput) {
                        capturedImageInput.value = imageDataURL;
                    }
                    
                    // Show retake button and hide capture button
                    captureBtn.classList.add('d-none');
                    retakeBtn.classList.remove('d-none');
                    
                    // Pause video
                    video.pause();
                }
            });
        }

        // Retake photo
        if (retakeBtn) {
            retakeBtn.addEventListener('click', function() {
                // Clear canvas and captured image input
                const context = canvas.getContext('2d');
                context.clearRect(0, 0, canvas.width, canvas.height);
                if (capturedImageInput) {
                    capturedImageInput.value = '';
                }
                
                // Show capture button and hide retake button
                captureBtn.classList.remove('d-none');
                retakeBtn.classList.add('d-none');
                
                // Resume video
                video.play();
            });
        }

        // Clean up when page is unloaded
        window.addEventListener('beforeunload', function() {
            stopCamera();
        });
    }

    // Like/React functionality
    const likeButtons = document.querySelectorAll('.like-button');
    
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const photoId = this.dataset.photoId;
            const likeCount = document.getElementById('like-count-' + photoId);
            
            fetch('/like/' + photoId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update like count
                    if (likeCount) {
                        likeCount.textContent = data.likes;
                    }
                    
                    // Toggle button appearance
                    if (data.liked) {
                        button.classList.add('liked');
                        button.querySelector('i').classList.remove('far');
                        button.querySelector('i').classList.add('fas');
                    } else {
                        button.classList.remove('liked');
                        button.querySelector('i').classList.remove('fas');
                        button.querySelector('i').classList.add('far');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });

    // Password strength validation
    const passwordInput = document.getElementById('password');
    const passwordConfirmInput = document.getElementById('password_confirm');
    const passwordStrength = document.getElementById('password-strength');
    
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let feedback = '';
            
            if (password.length >= 8) {
                strength += 1;
            }
            
            if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
                strength += 1;
            }
            
            if (password.match(/\d/)) {
                strength += 1;
            }
            
            if (password.match(/[^a-zA-Z\d]/)) {
                strength += 1;
            }
            
            switch (strength) {
                case 0:
                    passwordStrength.className = 'progress-bar bg-danger';
                    passwordStrength.style.width = '25%';
                    feedback = 'Very Weak';
                    break;
                case 1:
                    passwordStrength.className = 'progress-bar bg-danger';
                    passwordStrength.style.width = '25%';
                    feedback = 'Weak';
                    break;
                case 2:
                    passwordStrength.className = 'progress-bar bg-warning';
                    passwordStrength.style.width = '50%';
                    feedback = 'Fair';
                    break;
                case 3:
                    passwordStrength.className = 'progress-bar bg-info';
                    passwordStrength.style.width = '75%';
                    feedback = 'Good';
                    break;
                case 4:
                    passwordStrength.className = 'progress-bar bg-success';
                    passwordStrength.style.width = '100%';
                    feedback = 'Strong';
                    break;
            }
            
            passwordStrength.textContent = feedback;
        });
    }
    
    // Password confirmation validation
    if (passwordInput && passwordConfirmInput) {
        function validatePasswordMatch() {
            if (passwordInput.value !== passwordConfirmInput.value) {
                passwordConfirmInput.setCustomValidity("Passwords don't match");
            } else {
                passwordConfirmInput.setCustomValidity('');
            }
        }
        
        passwordInput.addEventListener('change', validatePasswordMatch);
        passwordConfirmInput.addEventListener('keyup', validatePasswordMatch);
    }
});