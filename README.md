This is my second web project. The first was a blog ([source code](https://github.com/chistev/Django-Blog), [Live environment](https://chistev.pythonanywhere.com/)).
This website was built with Django for the backend; and HTML, Vanilla Css and Bootstrap, Vanilla Javascript and JQuery for the frontend.

**PROJECT SUMMARY**
Both authenticated and non-authenticated users can add and remove from cart, although checking out is reserved for authenticated users and payment is through Flutterwave. Authemticated users can also save products to their wishlist for later.

**RUNNING THE PROJECT**

You must have Python installed on your computer. You can install the project dependencies with -
`pip install -r requirements.txt`

you can run the project with this command -
`python manage.py runserver`

**Note** if you want payments to work you will need to enter your own Flutterwave API key into the .env file in the base directory. Also if you want the email reset to work you would also need to include your own Brevo API key in the .env file.

**FUNCTIONALITIES**

**1. User Authentication and Registration:**
* Users can register with a unique email and password.
* Registration includes personal details like first name and last name.
* Users can log in with their email and password.
* Forgot password functionality sends a security code to the user's email for password reset.

  ![Screenshot 2024-04-26 114544](https://github.com/chistev/Django-Ecommerce/assets/115540580/51810d34-b9c5-4cc0-87b7-721343d9f5f6)

**2. Account Management::**
* Users can view and edit their basic details.

  ![Screenshot 2024-04-26 120556](https://github.com/chistev/Django-Ecommerce/assets/115540580/5552e355-28f1-40a8-b807-8470668bafa7)

* Users can change their passwords and delete their accounts.

  ![Screenshot 2024-04-26 121046](https://github.com/chistev/Django-Ecommerce/assets/115540580/922476b4-39c0-4d39-99b5-f03c8489ea01)

  ![Screenshot 2024-04-26 120840](https://github.com/chistev/Django-Ecommerce/assets/115540580/f831efc0-d355-448c-a3db-b4b1b96395ea)
  
* Address book management allows users to add and edit addresses for shipping.

**3. Order Management::**
* Users can view their active and cancelled orders.
  
  ![Screenshot 2024-04-26 123253](https://github.com/chistev/Django-Ecommerce/assets/115540580/fc5dfb05-1b8e-4ee9-89cb-529bffc59834)

* Detailed order views provide information about order items, delivery dates, and payment methods.
  
  ![Screenshot 2024-04-26 123416](https://github.com/chistev/Django-Ecommerce/assets/115540580/ce648ca4-4340-4737-9556-fe630cc172c6)

**4. Saved Items::**
* Users can save products for later viewing.
  ![Screenshot 2024-04-26 131929](https://github.com/chistev/Django-Ecommerce/assets/115540580/6915fd09-e1d7-452a-b482-feba8f0f6c69)

**5. Cart Management::**
* Users can view their cart contents.
* Cart items are displayed with product details, quantities, prices, and discounts.
* Subtotal is calculated based on the sum of product prices multiplied by quantities.

  ![Screenshot 2024-04-26 142039](https://github.com/chistev/Django-Ecommerce/assets/115540580/e547a864-582e-45d7-a756-7f9534f76719)

**6. Authentication Handling:**
* Authenticated users' carts are stored in the database.
* Anonymous users' carts are stored in session data.

**7. Adding and Removing Items:**
* Users can add and remove items from the cart.
* Products can be removed individually or all at once.
* Quantity updates are reflected in real-time.

**8. Responsive UI:**
* Empty cart messages are displayed when appropriate.
  
![Screenshot 2024-04-26 142528](https://github.com/chistev/Django-Ecommerce/assets/115540580/629e1176-cfaf-42b1-8324-2328217afdea)


**9. Error Handling::**
  * Proper error messages are returned for invalid requests or missing products.

**9. Delivery Management:**
* Estimates delivery dates based on the order date.
* Calculates delivery fees based on total order value.

**10. Payment Methods:**
* Supports two payment methods: "Pay on Delivery" and "Bank Transfer".
  
  ![Screenshot 2024-04-26 144338](https://github.com/chistev/Django-Ecommerce/assets/115540580/31a1f6f5-91f9-4f9c-b54c-22f90cea698f)

* Redirects users to payment gateways accordingly.

**11. Order Processing:**
* Processes "Pay on Delivery" orders immediately.
* For bank transfers, initiates orders upon successful payment verification.
* Handles order creation, item allocation, and cart clearance.

**12. External Payment Integration:**
* Integrates with Flutterwave for payment processing.
* Generates payment links and verifies transactions asynchronously via webhooks.

**13. Error Handling:**
* Provides error messages for invalid requests or payment failures.
* Ensures data integrity and security throughout the checkout process.

**14. Homepage:**
* Displays top-selling products based on order history.

**14. Product Categories:**
* Segregates products into categories like Supermarket, Home & Office, Computing, and Gaming.
* Renders category-specific pages with product listings.
* Supports breadcrumb navigation for easy category exploration.

**15. Product Details:**
* Shows detailed information about each product.
* Allows users to view product descriptions, prices, and images.
* Tracks user activity, including recently viewed products.

  ![Screenshot 2024-04-26 150749](https://github.com/chistev/Django-Ecommerce/assets/115540580/57769b97-2e5e-40ca-9b2d-3a7a46576d3c)

**16. Search Functionality:**
* Facilitates product search using keywords.
* Displays search results with matching products and descriptions.
* Provides autocomplete suggestions for efficient search input.
