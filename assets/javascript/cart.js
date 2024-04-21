$(document).ready(function () {

// Add to cart button click event
$('.add-to-cart-btn').click(function (e) {
    e.preventDefault();
    var productId = $(this).data('product-id');
    var addToCartUrl = $(this).data('add-to-cart-url');

    console.log("Product ID:", productId);
    console.log("Add to Cart URL:", addToCartUrl);
    
     addToCart(productId, addToCartUrl);     
    
     // Show the hidden buttons
    $(this).closest('.product-card').find('.add-to-cart-btn').hide();
    $(this).closest('.product-card').find('.d-flex.justify-content-between').show();
});

// Function to add a product to the cart
 function addToCart(productId, addToCartUrl) {
    $.ajax({
        type: 'POST',
        url: addToCartUrl,
        data: {
            'product_id': productId,
        },
        dataType: 'json',
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); // Include CSRF token in request headers
        },
        success: function (data) {
            console.log("Cart update success. Product ID:", productId, "Quantity:", data.product_quantity);
            
            // Update the product count span
            updateProductCount(productId, data.product_quantity);
            // If the quantity becomes zero, hide the quantity div and show the "Add to Cart" button
        if (data.product_quantity === 1) {
            $('.remove-product-btn[data-product-id="' + productId + '"]').show();
            $('.add-product[data-product-id="' + productId + '"]').show();
            $('.product-count[data-product-id="' + productId + '"]').show();
            $('.add-to-cart-btn[data-product-id="' + productId + '"]').hide();         
        }
            // Update the cart count in the UI
            updateCartCount(cartCountUrl);
            
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
            // Handle errors if any
        }
    });
}


// Function to update the product count span
function updateProductCount(productId, count) {
$('.product-count[data-product-id="' + productId + '"]').text(count);
}



// Function to update cart count
 function updateCartCount(cartCountUrl) {
    $.ajax({
        type: 'GET',
        url: cartCountUrl,
        dataType: 'json',
        success: function (data) {
            $('#cart-count').text(data.count);
            
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
            // Handle errors if any
        }
    });
}

 // Retrieve cart count URL from the data attribute
  var cartCountUrl = $('#cartCountUrl').data('url');
// Call updateCartCount initially to load the initial cart count
 updateCartCount(cartCountUrl);

// Decrement product quantity on click
 $('.remove-product-btn').click(function (e) {
e.preventDefault(); // Prevent default button behavior
var productId = $(this).data('product-id');
var removeCartUrl = $(this).data('remove-from-cart-url');
removeFromCart(productId, removeCartUrl);
});


// Function to remove a product from the cart
 function removeFromCart(productId, removeCartUrl) {
$.ajax({
    type: 'POST',
    url: removeCartUrl,
    data: {
        'product_id': productId,
    },
    dataType: 'json',
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); // Include CSRF token in request headers
    },
    success: function (data) {
        
        // Update the product count span
        updateProductCount(productId, data.product_quantity);

        // If the quantity becomes zero, hide the quantity div and show the "Add to Cart" button
        if (data.product_quantity === 0) {
            $('.remove-product-btn[data-product-id="' + productId + '"]').hide();
            $('.add-product[data-product-id="' + productId + '"]').hide();
            $('.product-count[data-product-id="' + productId + '"]').hide();
            $('.add-to-cart-btn[data-product-id="' + productId + '"]').show();         
        }        
        updateCartCount(cartCountUrl);  // Update cart count after removing the product      
    },
    error: function (xhr, errmsg, err) {
        console.log(xhr.status + ": " + xhr.responseText);
        // Handle errors if any
    }
});
console.log(removeCartUrl)
}
 


// Increment product quantity on click
 $('.add-product').click(function (e) {
e.preventDefault(); // Prevent default button behavior
var productId = $(this).data('product-id');
 var addToCartUrl = $(this).closest('.product-card').find('.add-to-cart-btn').data('add-to-cart-url');
 var addToCartUrl = $(this).data('add-to-cart-url');
console.log(productId, addToCartUrl)
addToCart(productId, addToCartUrl);
});


// Function to get CSRF token from cookies
 function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
});

