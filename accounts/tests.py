from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from django.test import TestCase, RequestFactory, Client
from django.urls import reverse, resolve


from accounts.models import CustomUser, Address, PersonalDetails, State, City
from accounts.views import change_password, delete_account


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


class MyAccountViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(email='test@example.com', password='testpassword')
        self.personal_details = PersonalDetails.objects.create(user=self.user, first_name='John', last_name='Doe')
        state = State.objects.create(name='Test State')
        city = City.objects.create(name='Test City', state=state)
        self.address = Address.objects.create(user=self.user, first_name='First', last_name='Last',
                                              address='123 Street', city=city, state=state)
        self.url = reverse('accounts:my_account')

    def test_my_account_view(self):
        # Login the user
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/my_account.html')
        self.assertEqual(response.context['current_path'], resolve(response.request['PATH_INFO']).url_name)
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['personal_details'], self.personal_details)
        self.assertQuerysetEqual(response.context['user_addresses'], Address.objects.filter(user=self.user))


class DeleteAccountViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create(email='test@example.com', password=make_password('testpassword'))

    def test_post_delete_account_correct_password(self):
        url = reverse('accounts:delete_account')
        data = {
            'confirm_delete': '1',
            'Password': 'testpassword'  # Correct password
        }

        request = self.factory.post(url, data)
        request.user = self.user

        # Create a session to store messages
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Attach message storage to request
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = delete_account(request)
        self.assertTrue(response.url.startswith(reverse('ecommerce:index')))

        # Check if success message is displayed
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your account has been successfully deleted.')

    def test_post_delete_account_incorrect_password(self):
        url = reverse('accounts:delete_account')
        data = {
            'confirm_delete': '1',
            'Password': 'incorrectpassword'  # Incorrect password
        }

        request = self.factory.post(url, data)
        request.user = self.user

        # Create a session to store messages
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Attach message storage to request
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = delete_account(request)
        self.assertEqual(response.status_code, 200)

        # Check if error message is displayed
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Incorrect password. Please try again.')

