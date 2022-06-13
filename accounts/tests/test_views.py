from django.urls import reverse
from rest_framework.test import APIClient, APITestCase


class TestViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {
            'username': 'test_us4er2',
            'email': 'test@hmail.com',
            'first_name': 'test',
            'last_name': 'user',
            'password': 'test_password',
            'password2': 'test_password',
        }

    def test_user_signup_view_for_correct_field_values(self):
        url = reverse('register')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'test_us4er2')
        self.assertEqual(response.data['user']['email'], 'test@hmail.com')

        # password field is set to write_only and hence should not be present in the response
        self.assertNotIn('password', response.data['user'])

        # An authentication token is returned in addition to the user
        #  details, checking for the presence of the token in the response
        self.assertIn('token', response.data)
        # save the token to use for subsequent requests
        self.token = response.data['token']

    def test_user_signup_with_unmatched_passwords_produces_400_error(self):
        """
        Test that a user cannot sign up with unmatched passwords
        """
        url = reverse('register')
        data = self.data.update({'password2': 'wrong_password'})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signup_without_required_name_length_produces_400_error(self):
        """
        Test that a user cannot sign up with a username or email that is less than 5 characters
        """
        url = reverse('register')
        data = self.data.update({'first_name': 'te', 'last_name': 'us'})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_user_logout_produces_401_error(self):
        logout_url = reverse('logout')
        response = self.client.post(logout_url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_user_logout_with_wrong_token_produces_401_error(self):
        """
        Test that a user cannot log out with a wrong token
        """
        logout_url = reverse('logout')
        wrong_authentication_token = 'somerandomstring'
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + wrong_authentication_token
        )
        response = self.client.post(logout_url, format='json')
        self.assertEqual(response.status_code, 401)
