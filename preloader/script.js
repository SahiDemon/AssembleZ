window.addEventListener('load', function() {
    // Show the preloader
    var preloader = document.querySelector('.loader-container');
    preloader.style.display = 'block';

    // Hide the preloader after 3 seconds or when the website finishes loading
    var hidePreloader = function() {
        preloader.style.display = 'none';
    };

    setTimeout(hidePreloader, 3000);
});