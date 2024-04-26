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

**1. Account Management::**
* Users can view and edit their basic details.

  ![Screenshot 2024-04-26 120556](https://github.com/chistev/Django-Ecommerce/assets/115540580/5552e355-28f1-40a8-b807-8470668bafa7)

* Users can change their passwords and delete their accounts.

  ![Screenshot 2024-04-26 121046](https://github.com/chistev/Django-Ecommerce/assets/115540580/922476b4-39c0-4d39-99b5-f03c8489ea01)

  ![Screenshot 2024-04-26 120840](https://github.com/chistev/Django-Ecommerce/assets/115540580/f831efc0-d355-448c-a3db-b4b1b96395ea)
  
* Address book management allows users to add and edit addresses for shipping.
  
