from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import PhotoFile
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoViewSetGET(TestCase):
    """
    Test GET api/photos
    """
    def test_photo_view_set_get_successful(self):
        """
        Test that we can get photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo1 = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()

        photo2 = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos')
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_view_set_get_public(self):
        """
        Test that we get public photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo1 = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), public=False, user=user)
        photo1.save()

        photo2 = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos')
        results = request.data['results']

        self.assertEquals(len(results), 1)


class TestPhotoViewSetPOST(TestCase):
    """
    Test POST api/photos
    """
    def test_photo_view_set_post_successful(self):
        """
        Test that we can save a photo

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects\
            .create_or_update(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'category': category.id,
                'image': image
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)

    def test_photo_view_set_post_bad_request_fields_missing(self):
        """
        Test that we get 400 if required fields are missing

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'image': image
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_post_bad_request_image_missing(self):
        """
        Test that we get 400 if image missing

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'category': category
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 400)
