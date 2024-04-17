from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from ecommerce.models import Cart, Product, CartItem, Order
from django.utils import timezone


class PayOnDeliveryViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='12345')

        # Create a test cart for the user
        self.cart = Cart.objects.create(user=self.user)

        # Create some test cart items
        self.product1 = Product.objects.create(name='Test Product 1', new_price=10)
        self.product2 = Product.objects.create(name='Test Product 2', new_price=20)
        self.cart_item1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        self.cart_item2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)

    def test_pay_on_delivery(self):
        # Log in the test user
        self.client.force_login(self.user)

        # Make a POST request to pay_on_delivery view
        response = self.client.post(reverse('checkout:pay_on_delivery'))

        # Check if the order is created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, 40)  # Total amount should be sum of product prices
        self.assertEqual(order.payment_method, 'pay_on_delivery')

        # Check if cart is cleared
        self.assertEqual(CartItem.objects.count(), 0)

        # Check if the correct template is rendered
        self.assertTemplateUsed(response, 'checkout/order_success.html')

        # Check if delivery dates are calculated correctly
        order_date = timezone.now()
        delivery_start_date_expected = order_date + timedelta(days=5)
        delivery_end_date_expected = order_date + timedelta(days=10)
        delivery_start_date_actual = response.context['delivery_start_date']
        delivery_end_date_actual = response.context['delivery_end_date']

        # Allow for a small difference in time (e.g., 1 second)
        time_threshold = timedelta(seconds=1)

        self.assertAlmostEqual(delivery_start_date_actual, delivery_start_date_expected, delta=time_threshold)
        self.assertAlmostEqual(delivery_end_date_actual, delivery_end_date_expected, delta=time_threshold)