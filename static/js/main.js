document.addEventListener('DOMContentLoaded', function() {
    // Add to cart functionality
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const quantity = this.querySelector('input[name="quantity"]').value;
            const productId = this.getAttribute('data-product-id');
            
            // Create a form and submit it
            const newForm = document.createElement('form');
            newForm.method = 'POST';
            newForm.action = `/add-to-cart/${productId}`;
            
            const quantityInput = document.createElement('input');
            quantityInput.type = 'hidden';
            quantityInput.name = 'quantity';
            quantityInput.value = quantity;
            
            newForm.appendChild(quantityInput);
            document.body.appendChild(newForm);
            newForm.submit();
        });
    });
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000);
    });
}); 