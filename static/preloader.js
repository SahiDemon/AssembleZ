
window.addEventListener('load', function() {
    // Wait for a few seconds after the site is loaded before sliding up the preloader
    setTimeout(function() {
        // Add the 'slide-up' class to initiate the slide-up animation
        document.querySelector('.preloader').classList.add('slide-up');

        // Optional: Remove the preloader from the DOM after it slides out of view
        setTimeout(() => {
            document.querySelector('.preloader').remove();
        }, 1000); // Matches the CSS transition duration
    }, 2000); // Adjust this delay as needed
});





document.getElementById('contactForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Elements for displaying messages
    var formLoading = document.getElementById('formLoading');
    var formAlertSuccess = document.getElementById('formAlertSuccess');
    var formAlertDanger = document.getElementById('formAlertDanger');

    // Show the loading message
    formLoading.style.display = 'block';
    formAlertSuccess.style.display = 'none';
    formAlertDanger.style.display = 'none';

    var form = this;
    var formData = new FormData(form);

    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'Accept': 'application/json'
        },
    }).then(response => {
        formLoading.style.display = 'none'; // Hide loading message
        if (response.ok) {
            formAlertSuccess.style.display = 'block'; // Show success message
            form.reset(); // Optionally reset the form

            // Remove success message after a timeout
            setTimeout(() => {
                formAlertSuccess.style.display = 'none';
            }, 10000); // Adjust the timeout duration as needed
        } else {
            formAlertDanger.style.display = 'block'; // Show error message
        }
    }).catch(error => {
        formLoading.style.display = 'none'; // Hide loading message
        formAlertDanger.style.display = 'block'; // Show error message
        console.error('Form submission error:', error);
    });
});



function filterProducts() {
    var input, filter, products, i, txtValue;
    input = document.getElementById('searchBox');
    filter = input.value.toUpperCase();
    products = document.getElementById("productList");
    product = products.getElementsByTagName('div');
  
    // Loop through all product divs, and hide those who don't match the search query
    for (i = 0; i < product.length; i++) {
      txtValue = product[i].textContent || product[i].innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        product[i].style.display = "";
      } else {
        product[i].style.display = "none";
      }
    }
  }


function updatePriceLabel() {
    var slider = document.getElementById('priceSlider');
    var label = document.getElementById('priceLabel');

    // Calculate the actual price based on the slider value. Replace this with your own calculation.
    var minPrice = 5000;
    var maxPrice = 999999;
    var price = minPrice + (slider.value / 100) * (maxPrice - minPrice);

    label.textContent = 'Price Range: LKR ' + Math.floor(price);
}

