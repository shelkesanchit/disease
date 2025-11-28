document.addEventListener("DOMContentLoaded", () => {
  // Price range slider
  const priceRange = document.getElementById("price-range")
  const minPrice = document.getElementById("min-price")
  const maxPrice = document.getElementById("max-price")
  const resetButton = document.getElementById("reset-filters")
  const filterForm = document.getElementById("filter-form")

  if (priceRange && maxPrice) {
    // Update max price when slider changes
    priceRange.addEventListener("input", function () {
      maxPrice.value = this.value
    })

    // Update slider when max price changes
    maxPrice.addEventListener("input", function () {
      priceRange.value = this.value
    })
  }

  // Reset filters
  if (resetButton && filterForm) {
    resetButton.addEventListener("click", (e) => {
      e.preventDefault()

      // Reset price inputs
      if (minPrice && maxPrice && priceRange) {
        minPrice.value = 0
        maxPrice.value = 100
        priceRange.value = 100
      }

      // Reset checkboxes
      const checkboxes = filterForm.querySelectorAll('input[type="checkbox"]')
      checkboxes.forEach((checkbox) => {
        checkbox.checked = false
      })

      // Preserve search query if exists
      const searchParam = new URLSearchParams(window.location.search).get("search")
      if (searchParam) {
        window.location.href = `${window.location.pathname}?search=${searchParam}`
      } else {
        window.location.href = window.location.pathname
      }
    })
  }

  // Ensure only one category checkbox is checked at a time
  const categoryCheckboxes = document.querySelectorAll('input[name="category"]')

  categoryCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      if (this.checked) {
        categoryCheckboxes.forEach((cb) => {
          if (cb !== this) {
            cb.checked = false
          }
        })
      }
    })
  })
})

