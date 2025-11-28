document.addEventListener("DOMContentLoaded", function() {
  // Select all product sliders on the page
  const sliders = document.querySelectorAll(".product-slider");
  
  sliders.forEach(function(slider) {
    // Get elements
    const container = slider.querySelector(".product-slider-container");
    const prevBtn = slider.querySelector(".slider-prev");
    const nextBtn = slider.querySelector(".slider-next");
    const productCards = slider.querySelectorAll(".product-card");
    
    // Skip initialization if any required element is missing
    if (!container || !prevBtn || !nextBtn || productCards.length === 0) return;
    
    // Calculate card width including margins
    const cardWidth = productCards[0].offsetWidth;
    
    // Set container styles for horizontal scrolling
    container.style.display = "flex";
    container.style.overflowX = "hidden";
    container.style.scrollBehavior = "smooth";
    container.style.position = "relative";
    
    // Make sure product cards display properly
    productCards.forEach(function(card) {
      card.style.flex = "0 0 auto";
      card.style.marginRight = "15px"; // Add margin between cards
    });
    
    // Initial button state
    updateButtonStates();
    
    // Button click handlers
    prevBtn.addEventListener("click", function() {
      const scrollAmount = Math.floor(container.clientWidth / cardWidth) * cardWidth;
      container.scrollLeft -= scrollAmount;
      setTimeout(updateButtonStates, 500); // Update after scroll animation
    });
    
    nextBtn.addEventListener("click", function() {
      const scrollAmount = Math.floor(container.clientWidth / cardWidth) * cardWidth;
      container.scrollLeft += scrollAmount;
      setTimeout(updateButtonStates, 500); // Update after scroll animation
    });
    
    // Update button visibility based on scroll position
    function updateButtonStates() {
      // Check if we can scroll left
      prevBtn.classList.toggle("disabled", container.scrollLeft <= 10);
      
      // Check if we can scroll right
      const maxScrollLeft = container.scrollWidth - container.clientWidth - 10;
      nextBtn.classList.toggle("disabled", container.scrollLeft >= maxScrollLeft);
    }
    
    // Add scroll event listener
    container.addEventListener("scroll", function() {
      updateButtonStates();
    });
    
    // Update on window resize
    window.addEventListener("resize", function() {
      updateButtonStates();
    });
  });
  
  // Add styles for disabled buttons
  const style = document.createElement("style");
  style.textContent = `
    .slider-arrow {
      cursor: pointer;
      background: #f8f9fa;
      border: 1px solid #dee2e6;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      z-index: 10;
    }
    
    .slider-prev {
      left: -20px;
    }
    
    .slider-next {
      right: -20px;
    }
    
    .slider-arrow.disabled {
      opacity: 0.3;
      cursor: not-allowed;
    }
    
    .product-slider {
      position: relative;
      padding: 0 25px;
      margin: 20px 0;
    }
    
    .product-slider-container {
      width: 100%;
      overflow-x: hidden;
    }
  `;
  document.head.appendChild(style);
});