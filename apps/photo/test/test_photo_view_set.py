from apps.account import models as account_models
from apps.common.models import get_date_stamp_str
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import override_settings, TestCase
from factory import DjangoModelFactory
from os.path import getsize
from rest_framework.test import APIClient
from rest_framework_tracking.models import APIRequestLog
import re
import time


class TestPhotoViewSetGET(TestCase):
    """
    Test GET api/photos
    """

    def setUp(self):
        """
            Method to create re-usable data for unit tests

        :return: None
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1',
                                                       location="Boise", social_name="@theaov")
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        for number in range(1, 13):
            photo1 = photo_models.Photo(coordinates=Point(-116, 43),
                                        image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                                        user=user)
            photo1.save()
            photo1.gear.add(gear_1, gear_2)
            photo1.category.add(category)
            photo1.votes = number
            photo1.photo_feed.add(1)
            photo1.save()

    def tearDown(self):
        """
            Removes unnecessary test data after each unit test

        :return: None
        """

        account_models.User.objects.all().delete()
        photo_models.Photo.objects.all().delete()
        photo_models.PhotoVote.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')

    def test_photo_view_set_get_successful(self):
        """
        Test that we can get photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        gear_1 = account_models.Gear.objects.get(item_make='Canon', item_model='EOS 5D Mark II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos')
        results = request.data['results']

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 12)
        self.assertEquals(len(results[1]['gear']), 2)
        self.assertEquals(results[1]['gear'][0], gear_1.id)
        self.assertEquals(results[1]['latitude'], 43.0)
        self.assertEquals(results[1]['longitude'], -116.0)
        self.assertEquals(results[1]['votes'], 11)
        self.assertEquals(results[1]['rank']['Night'], 2)
        self.assertEquals(results[1]['rank']['overall'], 2)
        self.assertEqual(results[1]['votes_behind']['Night'], 1)
        self.assertIsNotNone(results[0]['image_blurred'])
        self.assertIsNotNone(results[0]['scaled_render'])
        self.assertIsNotNone(results[0]['image_medium'])
        self.assertIsNotNone(results[0]['image_small'])
        self.assertIsNotNone(results[0]['image_small_2'])
        self.assertIsNotNone(results[0]['image_tiny_246'])
        self.assertIsNotNone(results[0]['image_tiny_272'])
        self.assertEquals(results[0]['user_details']['location'], user.location)
        self.assertEquals(results[0]['user_details']['social_name'], user.social_name)
        self.assertEquals(results[0]['user_details']['username'], user.username)
        self.assertEquals(results[0]['votes'], 12)
        self.assertEquals(results[0]['rank']['Night'], 1)
        self.assertEquals(results[0]['rank']['overall'], 1)

    def test_photo_view_set_get_public(self):
        """
        Test that we get public photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos')
        results = request.data['results']

        self.assertEquals(len(results), 12)

    def test_photo_view_set_get_classification(self):
        """
        Test that we get photos filtered by category

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?classification=night')
        results = request.data['results']

        self.assertEquals(len(results), 12)

    def test_photo_view_set_get_classification_does_not_exist(self):
        """
        Test that we get empty result set if classification does not exist

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?classification=other')
        results = request.data['results']

        self.assertEquals(len(results), 0)

    def test_photo_view_set_get_classification_id(self):
        """
        Test that we get photos filtered by category (using ID)

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Night', classification_type="category")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?classification={}'.format(category.id))
        results = request.data['results']

        self.assertEquals(len(results), 12)

    def test_photo_view_set_get_filtered(self):
        """
        Test that we get photos filtered by category and location

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Night', classification_type="category")

        for photo in photo_models.Photo.objects.all().iterator():
            photo.location = "boise"
            photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?classification={}&location=boise'.format(category.id))
        results = request.data['results']

        self.assertEquals(len(results), 12)

    def test_photo_view_set_get_geo_location(self):
        """
        Test that we get photos filtered by a box of coordinates

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        photo_models.Photo.objects.all().delete()

        photo1 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                                    location='boise', user=user)
        photo1.geo_location = 'POINT (-116.21 43.62)'
        photo1.save()

        photo2 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.geo_location = 'POINT (-116.25 43.61699)'
        photo2.save()

        photo3 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo3.geo_location = 'POINT (-118.25 45.61699)'
        photo3.save()

        photo4 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo4.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=-118,42,-115,44')
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_view_set_get_geo_missing_coordinate(self):
        """
        Test that we get 400 if geo_location is not properly formatted (missing a coord)

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=-118,42,-115')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_get_geo_bad_type(self):
        """
        Test that we get 400 if geo_location is a string

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=a,b,c,d')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_get_location(self):
        """
        Test that we get photos filtered by location

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        
        # Delete the setUp function objects to create specific entities for this test
        photo_models.Photo.objects.all().delete()

        photo1 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                                    location='boise', user=user)
        photo1.save()

        photo2 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?location=Boise')
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_view_set_get_renders_only(self):
        """
        Test that we can get photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?data=renders')
        results = request.data['results']

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 12)
        self.assertNotIn('gear', results[0])
        self.assertNotIn('latitude', results[0])
        self.assertNotIn('longitude', results[0])
        self.assertNotIn('votes', results[0])
        self.assertNotIn('votes_behind', results[0])
        self.assertNotIn('user', results[0])
        self.assertNotIn('user_details', results[0])
        self.assertNotIn('category', results[0])
        self.assertNotIn('comments', results[0])
        self.assertIn('image', results[0])
        self.assertIn('image_blurred', results[0])
        self.assertIn('image_medium', results[0])
        self.assertIn('image_small', results[0])
        self.assertIn('image_small_2', results[0])
        self.assertIn('image_tiny_246', results[0])
        self.assertIn('image_tiny_272', results[0])

    def test_photo_view_set_get_details_only(self):
        """
        Test that we can get photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?data=details')
        results = request.data['results']

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 12)
        self.assertIn('gear', results[0])
        self.assertIn('latitude', results[0])
        self.assertIn('longitude', results[0])
        self.assertIn('votes', results[0])
        self.assertIn('votes_behind', results[0])
        self.assertIn('user', results[0])
        self.assertIn('user_details', results[0])
        self.assertIn('category', results[0])
        self.assertIn('comments', results[0])
        self.assertNotIn('image', results[0])
        self.assertNotIn('image_blurred', results[0])
        self.assertNotIn('image_medium', results[0])
        self.assertNotIn('image_small', results[0])
        self.assertNotIn('image_small_2', results[0])
        self.assertNotIn('image_tiny_246', results[0])
        self.assertNotIn('image_tiny_272', results[0])


class TestPhotoViewSetPOST(TestCase):
    """
    Test POST api/photos
    """
    def setUp(self):
        account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        photo_models.PhotoClassification.objects.create_or_update(name='Landscape', classification_type='category')

        # Gear
        account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

    def tearDown(self):
        APIRequestLog.objects.all().delete()
        account_models.User.objects.all().delete()
        photo_models.PhotoClassification.objects.all().delete()
        account_models.Gear.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_successful(self):
        """
        Test that we can save a photo.
        Saves locally.

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.get(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.get(item_make='Sony', item_model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'geo_location': 'POINT ({} {})'.format(-116.2023436, 43.6169233),
                'image': i,
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['latitude'], 43.6169233)
        self.assertEquals(result['longitude'], -116.2023436)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)

        # Test that original uploaded image is saved (before resized and compressed)
        matched_images = test_helpers.find_file_by_pattern(settings.MEDIA_ROOT, '*_md-portrait.jpg')
        original_image = matched_images[0] if matched_images is not None else matched_images

        if original_image is not None:
            if not re.match('^u{}_'.format(user.id) + get_date_stamp_str().split('_')[0] + '_[0-9]{6}_md-portrait\.jpg$',
                            original_image):
                self.fail('Original image not matched!')
        else:
            self.fail('Original image not found!')

        # Sleep so other image-related unit tests don't get jacked up
        time.sleep(1)

        # Test that compression worked
        self.assertGreater(getsize(image), getsize('{}/{}'.format(settings.MEDIA_ROOT, str(photos[0].image))))

    def test_photo_view_set_post_remote_successful(self):
        """
        Test that we can save a photo. Must save remotely.

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.get(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.get(item_make='Sony', item_model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['user'], user.id)
        self.assertNotIn('original_image_url', result)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertEquals(photos[0].image.width, 2048)

    def test_photo_view_set_post_remote_no_gear_successful(self):
        """
        Test that we can save a photo w/out gear. Must save remotely.

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(len(result['gear']), 0)
        self.assertEquals(result['user'], user.id)
        self.assertIn('image_blurred', result)
        self.assertIn('scaled_render', result)
        self.assertNotIn('original_image_url', result)
        self.assertIn('image', result)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_bad_geo_location(self):
        """
        Test that we get a 403 if geo_location is not in "POINT (long, lat)" format

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/cover.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'geo_location': '{} {}'.format(-116.2023436, 43.6169233),
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 400)

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_long_geo_location(self):
        """
        Test that we get a 403 if geo_location is not in "POINT (long, lat)" format

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/cover.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'geo_location': 'POINT ({} {})'.format(-97.72594869999999, 30.258850199999998),
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 200)


    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_bad_request_fields_missing(self):
        """
        Test that we get 400 if required fields are missing

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')

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

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_bad_request_image_missing(self):
        """
        Test that we get 400 if image missing

        :return: None
        """
        # Test data
        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

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

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_with_tags_successful(self):
        """
            Unit test to verify posting an image with tags included works correctly

        :return: No return
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.get(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.get(item_make='Sony', item_model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'geo_location': 'POINT ({} {})'.format(-116.2023436, 43.6169233),
                'image': i,
                'tags': "#Pretty #Boise #Personal"
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['latitude'], 43.6169233)
        self.assertEquals(result['longitude'], -116.2023436)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)
        self.assertEqual(photos[0].tag.count(), 3)

        # Test that original uploaded image is saved (before resized and compressed)
        matched_images = test_helpers.find_file_by_pattern(settings.MEDIA_ROOT, '*_md-portrait.jpg')
        original_image = matched_images[0] if matched_images is not None else matched_images

        if original_image is not None:
            if not re.match('^u{}_'.format(user.id) + get_date_stamp_str().split('_')[
                0] + '_[0-9]{6}_md-portrait\.jpg$',
                            original_image):
                self.fail('Original image not matched!')
        else:
            self.fail('Original image not found!')

        # Sleep so other image-related unit tests don't get jacked up
        time.sleep(1)

        # Test that compression worked
        self.assertGreater(getsize(image), getsize('{}/{}'.format(settings.MEDIA_ROOT, str(photos[0].image))))


    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_with_tags_no_hash_successful(self):
        """
           Unit test to verify tags submitted with no hashtag work appropriately

        :return: No return
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.get(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.get(item_make='Sony', item_model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'geo_location': 'POINT ({} {})'.format(-116.2023436, 43.6169233),
                'image': i,
                'tags': "Pretty Boise Personal"
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['latitude'], 43.6169233)
        self.assertEquals(result['longitude'], -116.2023436)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)
        self.assertEqual(photos[0].tag.count(), 3)

        # Test that original uploaded image is saved (before resized and compressed)
        matched_images = test_helpers.find_file_by_pattern(settings.MEDIA_ROOT, '*_md-portrait.jpg')
        original_image = matched_images[0] if matched_images is not None else matched_images

        if original_image is not None:
            if not re.match('^u{}_'.format(user.id) + get_date_stamp_str().split('_')[
                0] + '_[0-9]{6}_md-portrait\.jpg$',
                            original_image):
                self.fail('Original image not matched!')
        else:
            self.fail('Original image not found!')

        # Sleep so other image-related unit tests don't get jacked up
        time.sleep(1)

        # Test that compression worked
        self.assertGreater(getsize(image), getsize('{}/{}'.format(settings.MEDIA_ROOT, str(photos[0].image))))

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_with_new_tag_name_successful(self):
        """
            Unit test to verify that if a Tag Classification doesn't exist, it gets created.
        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        self.assertFalse(photo_models.PhotoClassification.objects.filter(name="RandomTagThatCan'tExistYet",
                                                                         classification_type="tag").exists())

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'image': i,
                'tags': "RandomTagThatCan'tExistYet"
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)
        self.assertEquals(result['tag'][0]["name"], "RandomTagThatCan'tExistYet")

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)
        self.assertEqual(photos[0].tag.count(), 1)
        self.assertTrue(photo_models.PhotoClassification.objects.filter(name="RandomTagThatCan'tExistYet",
                                                                         classification_type="tag").exists())

        # Test that original uploaded image is saved (before resized and compressed)
        matched_images = test_helpers.find_file_by_pattern(settings.MEDIA_ROOT, '*_md-portrait.jpg')
        original_image = matched_images[0] if matched_images is not None else matched_images

        if original_image is not None:
            if not re.match('^u{}_'.format(user.id) + get_date_stamp_str().split('_')[
                0] + '_[0-9]{6}_md-portrait\.jpg$',
                            original_image):
                self.fail('Original image not matched!')
        else:
            self.fail('Original image not found!')

        # Sleep so other image-related unit tests don't get jacked up
        time.sleep(1)

        # Test that compression worked
        self.assertGreater(getsize(image), getsize('{}/{}'.format(settings.MEDIA_ROOT, str(photos[0].image))))

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_app_request_example_successful(self):
        """
            Unit test to verify that if a Tag Classification doesn't exist, it gets created.
        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.create(name='Landscape', classification_type='category', pk=17)

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': 17,
                'image': i,
                'tags': "#Nature #People",
                "magazine_authorized": "true",
                "public": "true"
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], 17)
        self.assertEquals(result['user'], user.id)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)
        self.assertEqual(photos[0].tag.count(), 2)

        # Test that original uploaded image is saved (before resized and compressed)
        matched_images = test_helpers.find_file_by_pattern(settings.MEDIA_ROOT, '*_md-portrait.jpg')
        original_image = matched_images[0] if matched_images is not None else matched_images

        if original_image is not None:
            if not re.match('^u{}_'.format(user.id) + get_date_stamp_str().split('_')[
                0] + '_[0-9]{6}_md-portrait\.jpg$',
                            original_image):
                self.fail('Original image not matched!')
        else:
            self.fail('Original image not found!')

        # Sleep so other image-related unit tests don't get jacked up
        time.sleep(1)

        # Test that compression worked
        self.assertGreater(getsize(image), getsize('{}/{}'.format(settings.MEDIA_ROOT, str(photos[0].image))))


    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_behind_the_shot_successful(self):
        """
            Unit test verifying serializer works correctly with new BTS fields

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.get(email='mrtest@mypapaya.io', username='aov1')
        category = photo_models.PhotoClassification.objects.get(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.get(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.get(item_make='Sony', item_model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'geo_location': 'POINT ({} {})'.format(-116.2023436, 43.6169233),
                'image': i,
                'bts_lens': 'lens test',
                'bts_shutter': 'shutter test',
                'bts_iso': 'iso test',
                'bts_aperture': 'aperture test',
                'bts_camera_settings': 'camera settings test',
                'bts_time_of_day': 'time of day test'
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['latitude'], 43.6169233)
        self.assertEquals(result['longitude'], -116.2023436)
        self.assertEquals(result['bts_lens'], 'lens test')
        self.assertEquals(result['bts_shutter'], 'shutter test')
        self.assertEquals(result['bts_iso'], 'iso test')
        self.assertEquals(result['bts_aperture'], 'aperture test')
        self.assertEquals(result['bts_camera_settings'], 'camera settings test')
        self.assertEquals(result['bts_time_of_day'], 'time of day test')

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)

