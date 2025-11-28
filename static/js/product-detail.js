document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls
    const quantityInput = document.querySelector('input[name="quantity"]');
    const decreaseBtn = document.querySelector('.quantity-btn.decrease');
    const increaseBtn = document.querySelector('.quantity-btn.increase');
    
    if (quantityInput && decreaseBtn && increaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            const currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
        
        increaseBtn.addEventListener('click', function() {
            const currentValue = parseInt(quantityInput.value);
            const maxValue = parseInt(quantityInput.getAttribute('max'));
            if (currentValue < maxValue) {
                quantityInput.value = currentValue + 1;
            }
        });
    }
    
    // Star rating functionality
    const starRating = document.querySelector('.star-rating');
    const ratingValue = document.querySelector('input[name="rating"]');
    
    if (starRating && ratingValue) {
        // Click handler for stars
        starRating.addEventListener('click', function(e) {
            if (e.target.classList.contains('fa-star')) {
                const rating = parseInt(e.target.getAttribute('data-rating'));
                ratingValue.value = rating;
                updateStars(rating);
            }
        });

        // Hover handler for stars
        starRating.addEventListener('mouseover', function(e) {
            if (e.target.classList.contains('fa-star')) {
                const rating = parseInt(e.target.getAttribute('data-rating'));
                updateStars(rating);
            }
        });

        // Reset stars when mouse leaves
        starRating.addEventListener('mouseleave', function() {
            const rating = parseInt(ratingValue.value);
            updateStars(rating);
        });

        // Helper function to update star display
        function updateStars(rating) {
            const stars = starRating.querySelectorAll('.fa-star');
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('filled');
                } else {
                    star.classList.remove('filled');
                }
            });
        }
    }
    
    // Add to cart form submission
    const addToCartForm = document.querySelector('.add-to-cart-form');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const quantity = this.querySelector('input[name="quantity"]').value;
            const productId = this.getAttribute('data-product-id');
            
            // Create a form and submit it
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/add-to-cart/${productId}`;
            
            const quantityInput = document.createElement('input');
            quantityInput.type = 'hidden';
            quantityInput.name = 'quantity';
            quantityInput.value = quantity;
            
            form.appendChild(quantityInput);
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Review form submission
    const reviewForm = document.getElementById('add-review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const rating = this.querySelector('input[name="rating"]').value;
            const comment = this.querySelector('textarea[name="comment"]').value;
            const productId = this.getAttribute('data-product-id');
            
            if (!productId) {
                alert('Error: Product ID not found');
                return;
            }
            
            if (rating === '0') {
                alert('Please select a rating');
                return;
            }
            
            if (!comment.trim()) {
                alert('Please write a review');
                return;
            }
            
            // Create a form and submit it
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/add-review/${productId}`;
            
            const ratingInput = document.createElement('input');
            ratingInput.type = 'hidden';
            ratingInput.name = 'rating';
            ratingInput.value = rating;
            
            const commentInput = document.createElement('input');
            commentInput.type = 'hidden';
            commentInput.name = 'comment';
            commentInput.value = comment;
            
            form.appendChild(ratingInput);
            form.appendChild(commentInput);
            document.body.appendChild(form);
            form.submit();
        });
    }
}); 