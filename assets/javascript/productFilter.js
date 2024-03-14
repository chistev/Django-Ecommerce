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
}

document.addEventListener("DOMContentLoaded", function() {

    // Get all product cards
    var productCards = document.querySelectorAll('.product-card');
    
    // Add click event listener to each product card
    productCards.forEach(function(card) {
        card.addEventListener('click', function() {
            // Get the product ID from data-product-id attribute
            var productId = this.getAttribute('data-product-id');
            console.log("Clicked product ID:", productId);
            
            // Redirect to the product detail page
            window.location.href = '/product_detail/' + productId + '/';
        });
    });

    // Get the minimum and maximum prices from Django template
    var minPrice = parseFloat(document.body.getAttribute('data-min-price'));
    var maxPrice = parseFloat(document.body.getAttribute('data-max-price'));

    // Check if the slider element already has a noUiSlider instance
    var priceSlider = document.getElementById('priceSlider');
    if (!priceSlider.classList.contains('noUi-target')) {
        // Initialize the slider only if it's not already initialized
        noUiSlider.create(priceSlider, {
            start: [minPrice, maxPrice], // Initial values for the handles
            connect: true,  // Connect the handles with a colored bar
            range: {
                'min': minPrice,
                'max': maxPrice
            }
        });
    }

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
        // Store the user's preference in localStorage
        localStorage.setItem("preferredView", "stacked");
    });

    gridIcon.addEventListener("click", function() {
        toggleView('grid');
        // Store the user's preference in localStorage
        localStorage.setItem("preferredView", "grid");
    });

    
    var minPriceInput = document.getElementById('minPriceInput');
    var maxPriceInput = document.getElementById('maxPriceInput');

    // Update the priceSlider when the input values change
    minPriceInput.addEventListener('input', updatePriceSlider);
    maxPriceInput.addEventListener('input', updatePriceSlider);

    // Update the input fields when the slider handles are moved
    priceSlider.noUiSlider.on('update', updateInputFields);

    // Clear input fields when the user starts editing
    minPriceInput.addEventListener('focus', clearInputField);
    maxPriceInput.addEventListener('focus', clearInputField);

    

    function updatePriceSlider() {
        var minValue = parseFloat(minPriceInput.value);
        var maxValue = parseFloat(maxPriceInput.value);
        priceSlider.noUiSlider.set([minValue, maxValue]);
    }

    function updateInputFields(values, handle) {
        var value = Math.round(values[handle]);
        if (handle === 0) {
            minPriceInput.value = value;
        } else if (handle === 1) {
            maxPriceInput.value = value;
        }
    }

    function clearInputField() {
        this.value = '';
    }

    // Function to update product list after filtering
    function updateProductList(products) {
        var productItemsContainer = document.getElementById('productItemsContainer');
        // Clear existing product items
        productItemsContainer.innerHTML = '';

        // Append new product items for both grid and stacked views
        products.forEach(product => {
            
            
            var discountHTML = '';

            // Create HTML for discount information
            if (product.discount_percentage !== 0) {
                discountHTML = `
                    <div class="d-flex">
                        <div class="slashed-price text-white ms-2" style="text-decoration: line-through; font-size: 13px;">N&nbsp;${product.formatted_old_price}</div>
                        <span class="badge bg-danger ms-2">${product.discount_percentage}%</span>
                    </div>
                `;
            }
            
            // Create grid view item
            var gridProductItem = createProductItem('grid-view', ['col-lg-3'], `
            <div class="position-relative product-card" data-product-id="${product.id}">
            <a href="/product_detail/${product.id}/">
                        <img src="${product.image_url}" alt="${product.name}" class="top-selling-image img-fluid">
                        <div class="item-name">&nbsp;&nbsp;${product.name}</div>
                        <div class="item-price text-white">&nbsp;&nbsp;N&nbsp;${product.formatted_price}</div>
                        ${discountHTML} <!-- Render the discount HTML here -->
                        <div class="rating">
                            <div class="static-stars ms-2">
                            <span class="star">&#9733;</span>
                            <span class="star">&#9733;</span>
                            <span class="star">&#9733;</span>
                            <span class="star">&#9733;</span>
                            <span class="star">&#9733;</span>
                            <span class="text-white">(12)</span>
                        </div>
                        </div>
                        
                        <div class="d-flex justify-content-center">
                            <a href="" class="btn btn-primary mt-2 mb-2 hide-cart-button" style="width: 90%;">Add To Cart</a>
                        </div>
                    </a>
                </div>
        `);


        // Create stacked view item
        var stackedProductItem = createProductItem('stacked-view', ['col-lg-12'], `
        <div class="position-relative product-card" onclick="window.location.href = '/product_detail/${product.id}/'">
                    <div class="row"> 
                        <div class="col-4">
                            <img src="${product.image_url}" alt="${product.name}" class="top-selling-image img-fluid">
                        </div>
                        <div class="col-4">
                            <div class="item-name">&nbsp;&nbsp;${product.name}</div>
                            <div class="rating">
                                <div class="static-stars ms-2">
                                    <span class="star">&#9733;</span>
                                    <span class="star">&#9733;</span>
                                    <span class="star">&#9733;</span>
                                    <span class="star">&#9733;</span>
                                    <span class="star">&#9733;</span>
                                    <span class="text-white">(12)</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-4 d-flex flex-column justify-content-between">
                            <div class="ms-auto">
                                <div class="item-price text-white">&nbsp;&nbsp;N&nbsp;${product.formatted_price}</div>
                                ${discountHTML} <!-- Render the discount HTML here -->
                            </div>
                            <div class="">
                                <a href="" class="btn btn-primary mt-2 mb-2" style="width: 90%;">Add To Cart</a>
                            </div>
                        </div>
                    </div>
                </div>
        `);

        productItemsContainer.appendChild(gridProductItem);
        productItemsContainer.appendChild(stackedProductItem);
    });

        // Ensure the view remains intact after filtering
        var preferredView = localStorage.getItem("preferredView") || "grid";
        toggleView(preferredView);
        
    }

        function createProductItem(viewClass, additionalClasses, innerHTML) {
            var item = document.createElement('div');
            // Add common classes for both grid and stacked views
            item.classList.add('col-md-4', viewClass);
            // Add additional classes specific to each view type
            additionalClasses.forEach(cls => item.classList.add(cls));
            item.innerHTML = innerHTML;
            return item;
        }

        // Add event listener to the apply filter button
        var applyFilterBtn = document.getElementById('applyFilterBtn');
        applyFilterBtn.addEventListener('click', function(event) {
            event.preventDefault();

            var minPrice = document.getElementById('minPriceInput').value;
            var maxPrice = document.getElementById('maxPriceInput').value;

            // Store filter criteria in localStorage
            localStorage.setItem("minPrice", minPrice);
            localStorage.setItem("maxPrice", maxPrice);

            // Send an AJAX request to fetch filtered products
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/products/?min_price=' + minPrice + '&max_price=' + maxPrice, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var products = JSON.parse(xhr.responseText);
                    updateProductList(products);
                }
            };
            xhr.send();
        });

        // Read filter parameters from URL on page load
        var urlParams = new URLSearchParams(window.location.search);
        var minPriceParam = urlParams.get('min_price');
        var maxPriceParam = urlParams.get('max_price');
        
        // Set the initial values for the price slider and input fields
        var initialMinPrice = minPriceParam || parseFloat(document.body.getAttribute('data-min-price'));
        var initialMaxPrice = maxPriceParam || parseFloat(document.body.getAttribute('data-max-price'));
        priceSlider.noUiSlider.set([initialMinPrice, initialMaxPrice]);
        minPriceInput.value = initialMinPrice;
        maxPriceInput.value = initialMaxPrice;

        // Function to fetch and update products based on filter parameters
        function fetchAndDisplayFilteredProducts() {
            var minPrice = minPriceInput.value;
            var maxPrice = maxPriceInput.value;

            // Update the URL with filter parameters
            var newUrl = window.location.origin + window.location.pathname + `?min_price=${minPrice}&max_price=${maxPrice}`;
            history.replaceState(null, null, newUrl);

            // Send an AJAX request to fetch filtered products
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/products/?min_price=' + minPrice + '&max_price=' + maxPrice, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var products = JSON.parse(xhr.responseText);
                    updateProductList(products);
                }
            };
            xhr.send();
        }

        applyFilterBtn.addEventListener('click', function(event) {
            event.preventDefault();
            fetchAndDisplayFilteredProducts();
        });
        // Fetch and display filtered products on page load if filter parameters are present
        if (minPriceParam && maxPriceParam) {
            fetchAndDisplayFilteredProducts();
        }
    });