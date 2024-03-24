
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

