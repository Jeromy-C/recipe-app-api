from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    samplePayload = {
        'email': 'test@test.com',
        'password': 'testpass',
        'name': 'Test Name'
    }

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        res = self.client.post(CREATE_USER_URL, self.samplePayload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.samplePayload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        create_user(**self.samplePayload)

        res = self.client.post(CREATE_USER_URL, self.samplePayload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = self.samplePayload
        payload['password'] = 'pw'
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_creat_token_for_user(self):
        create_user(**self.samplePayload)
        res = self.client.post(TOKEN_URL, self.samplePayload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(email='test@test.com', password='wrong')
        res = self.client.post(TOKEN_URL, self.samplePayload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        res = self.client.post(TOKEN_URL, self.samplePayload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
