
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
