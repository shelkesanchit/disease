document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls for each item
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        const input = selector.querySelector('input[name="quantity"]');
        const decreaseBtn = selector.querySelector('.quantity-btn.decrease');
        const increaseBtn = selector.querySelector('.quantity-btn.increase');
        
        if (input && decreaseBtn && increaseBtn) {
            decreaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value);
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            increaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value);
                input.value = currentValue + 1;
                input.dispatchEvent(new Event('change'));
            });
        }
    });
    
    // Update quantity form submission
    document.querySelectorAll('.update-quantity').forEach(input => {
        input.addEventListener('change', function(e) {
            e.preventDefault();
            const quantity = this.value;
            const productId = this.closest('.update-quantity-form').getAttribute('data-product-id');
            
            // Create a form and submit it
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/update-cart/${productId}`;
            
            const quantityInput = document.createElement('input');
            quantityInput.type = 'hidden';
            quantityInput.name = 'quantity';
            quantityInput.value = quantity;
            
            form.appendChild(quantityInput);
            document.body.appendChild(form);
            form.submit();
        });
    });
    
    // Remove from cart functionality
    document.querySelectorAll('.remove-from-cart').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            window.location.href = `/remove-from-cart/${productId}`;
        });
    });
    
    // Coupon code functionality
    const couponInput = document.getElementById('coupon-code');
    const applyCouponBtn = document.querySelector('.coupon-code button');
    
    if (couponInput && applyCouponBtn) {
        applyCouponBtn.addEventListener('click', function() {
            const code = couponInput.value.trim();
            if (code) {
                // Here you would typically make an API call to validate the coupon
                alert('Coupon code applied successfully!');
            } else {
                alert('Please enter a coupon code');
            }
        });
    }
}); 