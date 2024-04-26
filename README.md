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
