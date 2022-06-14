from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import CustomUser


class TestCustomUser(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='test_user',
            email='test@gmail.com',
            first_name='test',
            last_name='user',
            password='test_password',
        )

    def test_string_representation(self):
        self.assertEqual(str(self.user), self.user.email)

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, 'test_password')

    def test_user_flags(self):
        """
        Test that the newly created user is not a staff member
        """
        self.assertEqual(self.user.is_staff, False)
        self.assertEqual(self.user.is_superuser, False)
        self.assertEqual(self.user.is_active, True)
        self.assertEqual(self.user.is_admin, False)

    def test_user_has_email(self):
        self.assertEqual(self.user.email, 'test@gmail.com')

    def test_creating_user_with_same_username_raises_error(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='test_user',
                email='test@yahoo.com',
                first_name='test',
                last_name='user',
                password='test_password',
            )

    def test_creating_user_without_first_name_and_lastname_raises_error(self):
        """
        Test that a user cannot be created without a first name or last name
        Returns:

        """
        # A user must not have blank first or last names
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user(
                username='tes4t_user',
                email='randomemail@gmail.com',
                password='test_password',
            )
