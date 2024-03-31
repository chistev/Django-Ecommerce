from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.urls import reverse
from accounts.models import CustomUser


class LoginOrRegisterViewTest(TestCase):
    def test_get_request(self):
        url = reverse('accounts:login_or_register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_or_register.html')

    def setUp(self):
        self.factory = RequestFactory()

    def test_post_existing_user(self):
        email = 'existing@example.com'
        CustomUser.objects.create(email=email)
        url = reverse('accounts:login_or_register')
        data = {'email': email}

        # Create a POST request using the test client
        response = self.client.post(url, data)

        # Assert that the view redirected correctly
        self.assertRedirects(response, reverse('accounts:login', kwargs={'email': email}))

    def test_post_new_user(self):
        email = 'new@example.com'
        url = reverse('accounts:login_or_register')
        data = {'email': email}

        # Create a POST request using the test client
        response = self.client.post(url, data)

        # Assert that the view redirected correctly
        self.assertRedirects(response, reverse('accounts:register', kwargs={'email': email}))


class RegisterViewTest(TestCase):
    def test_register_invalid_form_shows_errors(self):
        data = {
            'email': 'invalid_email',  # Invalid email format
            'password1': 'password',
            'password2': 'password',
        }
        response = self.client.post(reverse('accounts:register', kwargs={'email': 'example@example.com'}), data)
        self.assertEqual(response.status_code, 200)  # Form submission fails, returns status 200
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)  # Check if one error message is displayed
        self.assertIn('Email', str(messages[0]))  # Check if the error message contains 'Email'