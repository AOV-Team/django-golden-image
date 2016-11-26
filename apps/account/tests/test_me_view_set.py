from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeViewSetGET(TestCase):
    """
    Test /api/me
    """
    def test_me_view_set_get_successful(self):
        """
        Successful /api/me GET

        :return:
        """
        # Create data
        user = account_models.User.objects.create_user(email='test@test.com', social_name='aeon', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me')
        result = request.data['result']

        self.assertEquals(result['email'], user.email)
        self.assertEquals(result['social_name'], user.social_name)
        self.assertEquals(result['username'], user.username)


class TestMeViewSetPATCH(TestCase):
    """
    Test PATCH /api/me
    """
    def test_me_view_set_patch_successful(self):
        """
        Test that we can update user's data

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'age': 22
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data['result']

        self.assertEquals(result['age'], 22)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.age, 22)

    def test_me_view_set_patch_sanitize_successful(self):
        """
        Test that payload is sanitized (PK doesn't change)

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test2@test.com', social_name='aeon',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'id': 222,
            'age': 22
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data['result']

        self.assertEquals(result['age'], 22)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.id, user.id)
        self.assertEquals(updated_user.age, 22)

    def test_me_view_set_patch_sanitize_uneditable(self):
        """
        Test that payload is sanitized (cannot change superuser status, etc)

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'age': 22,
            'is_superuser': True
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data['result']

        self.assertEquals(result['age'], 22)
        self.assertEquals(result['is_superuser'], False)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.age, 22)
        self.assertEquals(updated_user.is_superuser, False)
