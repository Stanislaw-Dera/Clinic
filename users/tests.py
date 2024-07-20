from django.contrib.messages import get_messages
from django.test import TestCase, Client

from users.models import User


# Create your tests here.

class UsersTest(TestCase):
    def setUp(self):
        # create users
        u1 = User.objects.create_user(
            email='testuser@example.com',
            name='Test',
            surname='User',
            password='testpassword'
        )

    def test_user_creation(self):
        """User creation"""
        u1 = User.objects.get(email='testuser@example.com')

        self.assertTrue(u1.email == 'testuser@example.com')
        self.assertTrue(u1.name == 'Test')
        self.assertTrue(u1.surname == 'User')
        # password

    # def test_same_user_creation(self):
    #     """Creating the same user"""
    #     u1 = User.objects.get(email='testuser@example.com')

        # u2 = User.objects.create_user(
        #     email='testuser@example.com',
        #     name='Test',
        #     surname='User',
        #     password='testpassword'
        # )
        #  UNIQUE constraint failed: users_user.email

    def test_registering(self):
        """User registration"""
        u1 = User.objects.get(email='testuser@example.com')

        c = Client()
        response = c.post("/register/", {
            "email": u1.email,
            "activation_code": u1.activation_code,
            "password": u1.password,
            "confirm_password": u1.password})

        self.assertEqual(response.status_code, 302)

        response = c.post("/register/", {
            "email": "no u",
            "activation_code": u1.activation_code,
            "password": u1.password,
            "confirm_password": u1.password})

        # messages = list(get_messages(response.wsgi_request))
        # print("messages: ", messages)

        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """User loging in"""
        u1 = User.objects.get(email='testuser@example.com')

        c = Client()
        response = c.post("/login/", {
            "email": u1.email,
            "password": "testpassword"})

        self.assertEqual(response.status_code, 302)

        response = c.post("/login/", {
            "email": u1.email,
            "password": "lorem ipsum"})

        # messages = list(get_messages(response.wsgi_request))
        # print("messages: ", messages)

        self.assertEqual(response.status_code, 200)