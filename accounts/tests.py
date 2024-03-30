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
