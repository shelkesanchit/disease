document.addEventListener("DOMContentLoaded", () => {
  // Payment method toggle
  const paymentMethods = document.querySelectorAll('input[name="payment_method"]')
  const creditCardFields = document.getElementById("credit-card-fields")

  if (paymentMethods.length && creditCardFields) {
    paymentMethods.forEach((method) => {
      method.addEventListener("change", function () {
        if (this.value === "credit-card") {
          creditCardFields.style.display = "block"
        } else {
          creditCardFields.style.display = "none"
        }
      })
    })
  }

  // Form validation
  const checkoutForm = document.getElementById("checkout-form")

  if (checkoutForm) {
    checkoutForm.addEventListener("submit", function (e) {
      // Basic validation
      const requiredFields = this.querySelectorAll("[required]")
      let isValid = true

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          isValid = false
          field.classList.add("error")
        } else {
          field.classList.remove("error")
        }
      })

      // Credit card validation if credit card is selected
      const creditCardRadio = document.getElementById("credit-card")

      if (creditCardRadio && creditCardRadio.checked) {
        const cardNumber = document.getElementById("card_number")
        const expiryDate = document.getElementById("expiry_date")
        const cvv = document.getElementById("cvv")

        if (cardNumber && !validateCardNumber(cardNumber.value)) {
          isValid = false
          cardNumber.classList.add("error")
        }

        if (expiryDate && !validateExpiryDate(expiryDate.value)) {
          isValid = false
          expiryDate.classList.add("error")
        }

        if (cvv && !validateCVV(cvv.value)) {
          isValid = false
          cvv.classList.add("error")
        }
      }

      if (!isValid) {
        e.preventDefault()
        showNotification("Please fill in all required fields correctly", "error")

        // Scroll to first error
        const firstError = document.querySelector(".error")
        if (firstError) {
          firstError.scrollIntoView({ behavior: "smooth", block: "center" })
        }
      } else {
        // Show loading state
        const submitButton = this.querySelector('button[type="submit"]')
        if (submitButton) {
          submitButton.disabled = true
          submitButton.innerHTML = "Processing..."
        }
      }
    })

    // Add error styles if not already in CSS
    if (!document.getElementById("error-styles")) {
      const style = document.createElement("style")
      style.id = "error-styles"
      style.textContent = `
                .error {
                    border-color: #f44336 !important;
                }
            `
      document.head.appendChild(style)
    }
  }

  // Helper validation functions
  function validateCardNumber(cardNumber) {
    // Basic validation - remove spaces and check if it's a 16-digit number
    const cleaned = cardNumber.replace(/\s+/g, "")
    return /^\d{16}₹/.test(cleaned)
  }

  function validateExpiryDate(expiryDate) {
    // Check if in MM/YY format
    if (!/^\d{2}\/\d{2}₹/.test(expiryDate)) {
      return false
    }

    const [month, year] = expiryDate.split("/")
    const currentDate = new Date()
    const currentYear = currentDate.getFullYear() % 100 // Get last 2 digits
    const currentMonth = currentDate.getMonth() + 1 // 1-12

    // Convert to numbers
    const monthNum = Number.parseInt(month, 10)
    const yearNum = Number.parseInt(year, 10)

    // Check if month is valid
    if (monthNum < 1 || monthNum > 12) {
      return false
    }

    // Check if date is in the future
    if (yearNum < currentYear || (yearNum === currentYear && monthNum < currentMonth)) {
      return false
    }

    return true
  }

  function validateCVV(cvv) {
    // Check if it's a 3 or 4 digit number
    return /^\d{3,4}₹/.test(cvv)
  }

  // Notification function
  function showNotification(message, type = "success") {
    const notification = document.createElement("div")
    notification.className = `notification ₹{type}`
    notification.textContent = message

    document.body.appendChild(notification)

    setTimeout(() => {
      notification.classList.add("show")
    }, 10)

    setTimeout(() => {
      notification.classList.remove("show")
      setTimeout(() => {
        notification.remove()
      }, 300)
    }, 3000)
  }
})

