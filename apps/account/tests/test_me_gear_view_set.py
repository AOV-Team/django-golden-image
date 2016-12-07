from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeGearViewSetDELETE(TestCase):
    """
    Test DELETE /api/me/gear
    """
    def test_me_gear_view_set_delete_successful(self):
        """
        Test that we can delete a user's gear

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/me/gear')

        self.assertEquals(request.status_code, 200)

        # Check profile entry
        updated_profile = account_models.Profile.objects.get(user=user)

        self.assertEquals(updated_profile.gear, None)

    def test_me_gear_view_set_delete_no_profile(self):
        """
        Test that we still get 200 OK even if user has no profile (gear)

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/me/gear')

        self.assertEquals(request.status_code, 200)


class TestMeGearViewSetGET(TestCase):
    """
    Test GET /api/me/gear
    """
    def test_me_gear_view_set_get_successful(self):
        """
        Test that we can get user's gear

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/gear')
        results = request.data

        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]['name'], 'Canon T3i')

    def test_me_gear_view_set_get_empty(self):
        """
        Test that we get empty list if no gear

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/gear')
        results = request.data

        self.assertIsInstance(results, list)
        self.assertEquals(len(results), 0)

    def test_me_gear_view_set_get_no_profile(self):
        """
        Test that we get empty list even if no profile

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/gear')
        results = request.data

        self.assertIsInstance(results, list)
        self.assertEquals(len(results), 0)


class TestMeGearViewSetPATCH(TestCase):
    """
    Test PATCH /api/me/gear
    """
    def test_me_gear_view_set_patch_successful(self):
        """
        Test that we can update user's gear

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')
        results = request.data

        self.assertEquals(len(results), 2)
        self.assertIn('link', results[0])
        self.assertEquals(results[1]['name'], 'Tripod')

    def test_me_gear_view_set_patch_bad_request(self):
        """
        Test that we get a 400 if we pass bad data

        :return:
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'model': 'Tripod'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Check profile entry
        updated_gear = account_models.Gear(account_models.Profile.objects.get(user=user)).all

        self.assertEquals(len(updated_gear), 1)
        self.assertEquals(updated_gear[0]['name'], 'Canon T3i')

    def test_me_gear_view_set_patch_empty(self):
        """
        Test that we can update an empty gear list

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i'
            },
            {
                'name': 'Nifty Fifty'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')
        self.assertEquals(request.status_code, 200)

        # Check profile entry
        updated_gear = account_models.Gear(account_models.Profile.objects.get(user=user)).all

        self.assertEquals(len(updated_gear), 2)
        self.assertEquals(updated_gear[0]['name'], 'Canon T3i')
        self.assertEquals(updated_gear[0]['name'], 'Nifty Fifty')

    def test_me_gear_view_set_patch_link_new(self):
        """
        Test that we get HTTP 403 if user attempts to create a new link.
        User can PATCH links but they have to match existing links.
        User cannot set or update links via API

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')

        self.assertEquals(request.status_code, 403)

        # Check profile entry
        updated_gear = account_models.Gear(account_models.Profile.objects.get(user=user)).all

        self.assertEquals(updated_gear[0]['link'],
                          'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y')
        self.assertNotIn('link', updated_gear[1])

    def test_me_gear_view_set_patch_link_original(self):
        """
        User can PATCH links as long as they are the same as what's already in the db

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Check profile entry
        updated_gear = account_models.Gear(account_models.Profile.objects.get(user=user)).all

        self.assertEquals(updated_gear[0]['link'],
                          'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y')
        self.assertEquals(updated_gear[1]['link'],
                          'https://www.amazon.com/gp/product/B002FGTWOC/')

    def test_me_gear_view_set_patch_no_profile(self):
        """
        Test that we get a HTTP 403 if user tries to set gear and the profile doesn't exist

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')

        self.assertEquals(request.status_code, 403)

    def test_me_gear_view_set_patch_over_limit(self):
        """
        Test that we get an HTTP 400 if user is over the limit

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = [
            {
                'name': 'Canon T3i'
            },
            {
                'name': 'Tripod'
            },
            {
                'name': 'Nifty Fifty'
            },
            {
                'name': 'Camera Bag'
            },
            {
                'name': 'Polarizing Filter'
            },
            {
                'name': 'Mic'
            },
            {
                'name': 'Battery Pack'
            },
            {
                'name': 'Bulb'
            },
            {
                'name': 'Charger'
            }
        ]

        request = client.patch('/api/me/gear', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Check profile entry
        updated_gear = account_models.Gear(account_models.Profile.objects.get(user=user)).all

        self.assertEquals(len(updated_gear), 1)
        self.assertEquals(updated_gear[0]['name'], 'Canon T3i')

    def test_me_gear_view_set_patch_set_empty_data(self):
        """


        :return:
        """


# class TestMeGearViewSetPOST(TestCase):
#     """
#     Test POST /api/me/gear
#     """
#     def test_me_gear_view_set_post_successful(self):
#         """
#         Test that we can add user's gear
#
#         :return: None
#         """
#         # Create test data
#         user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
#         profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')
#
#     def test_me_gear_view_set_post_empty_data(self):
#         """
#
#
#         :return:
#         """
#
#     def test_me_gear_view_set_post_bad_request(self):
#         """
#
#
#         :return:
#         """
#
#     def test_me_gear_view_set_post_link(self):
#         """
#
#
#         :return:
#         """
#
#     def test_me_gear_view_set_post_no_profile(self):
#         """
#
#
#         :return:
#         """
#
#     def test_me_gear_view_set_post_over_limit(self):
#         """
#
#
#         :return:
#         """