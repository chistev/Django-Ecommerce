document.addEventListener("DOMContentLoaded", function() {
    // Function to add mx-auto class based on window width
    function addMxAutoClass() {
        var maxWidth = 768; // Set your maximum width here
        var currentWidth = window.innerWidth;

        if (currentWidth <= maxWidth) {
            document.querySelector('.small-screen').classList.add('mx-auto');
        } else {
            document.querySelector('.small-screen').classList.remove('mx-auto');
        }
    }

    // Call the function when the page loads
    window.addEventListener('load', function() {
        addMxAutoClass();
    });

    // Call the function when the window is resized
    window.addEventListener('resize', function() {
        addMxAutoClass();
    });
});
