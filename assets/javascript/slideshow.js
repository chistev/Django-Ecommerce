document.addEventListener("DOMContentLoaded", function () {
    var slideIndex = 0;

    function showSlides() {
        var i;
        var slides = document.getElementsByClassName("mySlides");
        var dots = document.getElementsByClassName("dot");

        for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
            dots[i].classList.remove("active");
        }

        slideIndex++;
        if (slideIndex > slides.length) {
            slideIndex = 1;
        }

        slides[slideIndex - 1].style.display = "block";
        dots[slideIndex - 1].classList.add("active");

        setTimeout(showSlides, 5000); // Change slide every 5 seconds
    }

    // Initial call to start the slideshow
    showSlides();
});

// Function to set the current slide on click
function currentSlide(n) {
    showSlides(slideIndex = n);
}
