// Function to toggle between grid and stacked views
function toggleView(view) {
    var gridItems = document.querySelectorAll('.grid-view');
    var stackedItems = document.querySelectorAll('.stacked-view');
    var stackIcon = document.getElementById('stackIcon');
    var gridIcon = document.getElementById('gridIcon');

    if (view === 'stacked') {
        gridItems.forEach(item => item.style.display = 'none');
        stackedItems.forEach(item => item.style.display = 'block');
        stackIcon.classList.add('text-primary');
        gridIcon.classList.remove('text-primary');
    } 
    else if (view === 'grid') {
        gridItems.forEach(item => item.style.display = 'block');
        stackedItems.forEach(item => item.style.display = 'none');
        stackIcon.classList.remove('text-primary');
        gridIcon.classList.add('text-primary');
    }

    // Store the user's preference in localStorage
    localStorage.setItem("preferredView", view);
}

document.addEventListener("DOMContentLoaded", function() {

    // Get all product cards
    var productCards = document.querySelectorAll('.product-card');
    
    // Add click event listener to each product card
    productCards.forEach(function(card) {
        card.addEventListener('click', function(event) {
            // Check if the clicked element or its ancestor has the class 'remove-product-btn'
            if (!event.target.classList.contains('add-to-cart-btn') && !event.target.closest('.remove-product-btn') && !event.target.closest('.add-product')) {
                // Get the product ID from data-product-id attribute
                var productId = this.getAttribute('data-product-id');
                console.log("Clicked product ID:", productId);
                
                // Redirect to the product detail page
                window.location.href = '/product_detail/' + productId + '/';
            }
        });
    });

    // Retrieve the user's preferred view from localStorage
    // Set the default view to grid if no preference is stored
    var preferredView = localStorage.getItem("preferredView") || "grid";
    // Apply the preferred view
    toggleView(preferredView);

    // Add event listeners to the toggle buttons
    var stackIcon = document.getElementById('stackIcon');
    var gridIcon = document.getElementById('gridIcon');

    stackIcon.addEventListener("click", function() {
        toggleView('stacked');
    });

    gridIcon.addEventListener("click", function() {
        toggleView('grid');
    });
});
