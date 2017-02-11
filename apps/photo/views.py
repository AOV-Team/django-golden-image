from apps.account import models as account_models
from apps.account import serializers as account_serializers
from apps.common import models as common_models
from apps.common.serializers import setup_eager_loading
from apps.common.views import DefaultResultsSetPagination, get_default_response, handle_jquery_empty_array, \
    LargeResultsSetPagination, MediumResultsSetPagination, remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from apps.utils.models import UserAction
from apps.utils.serializers import UserActionSerializer
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


@staff_member_required
def photo_admin(request):
    """
    View for /admin/photos/

    :param request: Request object
    :return: render()
    """
    category = request.GET.get('category')
    date = request.GET.get('date')
    feed = request.GET.get('feed')
    g = request.GET.get('g')
    i = request.GET.get('i')
    q = request.GET.get('q')
    u = request.GET.get('u')

    # Default is none
    photos = photo_models.Photo.objects.none()

    if category:
        cat = photo_models.PhotoClassification.objects\
            .filter(classification_type='category', name__icontains=category).first()

        if cat:
            photos = photos | photo_models.Photo.objects.filter(category=cat)

    if date:
        dates = date.split(' - ')

        if len(dates) == 2:
            start = datetime.strptime(dates[0], '%Y-%m-%d')
            end = datetime.strptime(dates[1], '%Y-%m-%d') + timedelta(days=1)

            photos = photos | photo_models.Photo.objects.filter(created_at__gte=start, created_at__lte=end)

    if feed:
        feed = photo_models.PhotoFeed.objects.filter(name__icontains=feed)

        if feed:
            photos = photos | photo_models.Photo.objects.filter(photo_feed=feed)

    if g:
        # Search gear
        gear = account_models.Gear.objects.filter(Q(item_make__icontains=g) | Q(item_model__icontains=g))

        for g in gear:
            photos = photos | photo_models.Photo.objects.filter(gear=g)

    if i:
        # ID
        photos = photo_models.Photo.objects.filter(pk=i)

    if q or u:
        # Search for a tag
        if q:
            tag = photo_models.PhotoClassification.objects.filter(classification_type='tag', name__icontains=q).first()

            if tag:
                photos = photos | photo_models.Photo.objects.filter(Q(tag=tag) | Q(location__icontains=q))
            else:
                photos = photos | photo_models.Photo.objects.filter(location__icontains=q)

        # User search
        # Only active users
        if u:
            try:
                age = int(u)
            except ValueError:
                age = -1

            users = account_models.User.objects\
                .filter(Q(age=age) | Q(email__icontains=u) | Q(first_name__icontains=u) |
                        Q(last_name__icontains=u) | Q(location__icontains=u) | Q(username__icontains=u), is_active=True)

            for user in users:
                photos = photos | photo_models.Photo.objects.filter(user=user)

    # Default query
    if not category and not date and not feed and not g and not i and not q and not u:
        # Build search attributes for photo
        search = {
            'public': True
        }

        photos = photo_models.Photo.objects.filter(**search)

    # Pagination
    photos = photos.filter(public=True).order_by('-id').distinct()
    paginator = Paginator(photos, 30)
    page = request.GET.get('page')

    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        photos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        photos = paginator.page(paginator.num_pages)

    # Add lists of names of feeds and tags that image is in
    # Also check if photo has been starred by user
    # Makes it easier to work with in the HTML template
    for photo in photos:
        if not getattr(photo, 'photo_feed_names', None):
            photo.photo_feed_names = list()

        if not getattr(photo, 'photo_tag_names', None):
            photo.photo_tag_names = list()

        for feed in photo.photo_feed.all():
            if feed.public:
                photo.photo_feed_names.append(feed.name)

        for tag in photo.tag.all():
            if tag.public:
                photo.photo_tag_names.append(tag.name)

        # Has user starred photo?
        photo_type = ContentType.objects.get_for_model(photo)
        interest = account_models.UserInterest.objects \
            .filter(user=request.user, interest_type='star', content_type__pk=photo_type.id, object_id=photo.id).first()

        if interest:
            photo.starred = True
        else:
            photo.starred = False

    # Categories
    categories = photo_models.PhotoClassification.objects\
        .filter(classification_type='category', public=True).order_by('name')

    # Ensure we retain query string even when paginating
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()

    context = {
        'categories': categories,
        'media_url': settings.MEDIA_URL,
        'parameters': parameters,
        'photo_feeds': photo_models.PhotoFeed.objects.filter(public=True),
        'photos': photos
    }

    return render(request, 'photos.html', context)


@staff_member_required
def photo_map_admin(request):
    """
    Map photos

    :param request:
    :return: render()
    """
    context = {}

    return render(request, 'photo_map.html', context)


class PhotoViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    pagination_class = LargeResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return images

        :return: Queryset
        """
        classification_param = self.request.query_params.get('classification')
        geo_location = self.request.query_params.get('geo_location')
        location = self.request.query_params.get('location')
        query_params = {
            'public': True
        }

        if location:
            query_params['location__iexact'] = location

        # If searching by a box of coordinates
        # Format ?geo_location=SW LONG,SW LAT,NE LONG, NE LAT
        if geo_location:
            coordinates = tuple(geo_location.split(','))

            # Check that we have 4 coordinates
            # And each coordinate needs to be a number
            if len(coordinates) != 4:
                raise ValidationError('Expecting geo_location to have 4 coordinates: "SW LONG,SW LAT,NE LONG, NE LAT"')
            else:
                try:
                    for c in coordinates:
                        float(c)
                except ValueError:
                    raise ValidationError('Expecting number format for coordinates')

            rectangle = Polygon.from_bbox(coordinates)
            query_params['coordinates__contained'] = rectangle

        if classification_param:
            try:
                # If we get classification id, use it
                # Otherwise set to 0 (will not match anything)
                try:
                    classification_id_param = int(classification_param)
                except ValueError:
                    classification_id_param = 0

                # Match either by ID or name
                classification = photo_models.PhotoClassification.objects\
                    .get(Q(id=classification_id_param) | Q(name__iexact=classification_param))

                return photo_models.Photo.objects\
                    .filter(Q(category=classification) | Q(tag=classification), **query_params).order_by('-id')
            except ObjectDoesNotExist:
                # Empty queryset
                return photo_models.Photo.objects.none()
        else:
            return photo_models.Photo.objects.filter(**query_params).order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Save photo

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        payload['user'] = authenticated_user.id

        # Image compression
        # Save original first
        if 'image' in payload:
            # Save original photo to media
            try:
                photo = Photo(payload['image'])
                remote_key = photo.save('u{}_{}_{}'
                                        .format(authenticated_user.id, common_models.get_date_stamp_str(), photo.name),
                                        custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                # Original image url
                payload['original_image_url'] = '{}{}'.format(settings.ORIGINAL_MEDIA_URL, remote_key)

                # Process image to save
                payload['image'] = photo.compress()
            except TypeError:
                raise ValidationError('Image is not of type image')

        serializer = photo_serializers.PhotoSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
        else:
            raise ValidationError(serializer.errors)

        return response


class PhotoClassificationViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MediumResultsSetPagination
    serializer_class = photo_serializers.PhotoClassificationSerializer

    def get_queryset(self):
        """
        Return classifications

        :return: Queryset
        """
        query_params = {
            'public': True
        }

        classification_type = self.request.query_params.get('classification', None)

        # Add classification if provided
        if classification_type:
            if classification_type == 'category' or classification_type == 'tag':
                query_params['classification_type'] = classification_type
            else:
                # HTTP 400
                raise ValidationError('Classification type "{}" not valid'.format(classification_type))

        return photo_models.PhotoClassification.objects.filter(**query_params)

    def post(self, request, *args, **kwargs):
        """
        Create new classification

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        payload = request.data
        payload = remove_pks_from_payload('photo_classification', payload)

        # Only tags are allowed
        if 'classification_type' in payload:
            if payload['classification_type'] == 'category':
                raise ValidationError('Cannot create a category')
        else:
            payload['classification_type'] = 'tag'

        # If trying to create private entry, deny
        if 'public' in payload:
            if not payload['public']:
                raise ValidationError('Cannot create private classification')

        serializer = photo_serializers.PhotoClassificationSerializer(data=payload)

        if serializer.is_valid():
            # If classification already exists, update.
            # Else save new
            try:
                classification = photo_models.PhotoClassification.objects.get(name__iexact=payload['name'],
                                                                              classification_type='tag')

                serializer.update(classification, serializer.validated_data)
            except ObjectDoesNotExist:
                serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
            return response
        else:
            raise ValidationError(serializer.errors)


class PhotoClassificationPhotosViewSet(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return photos for a classification

        :return: Queryset
        """
        try:
            photo_classification_id = self.kwargs.get('photo_classification_id')
            classification = photo_models.PhotoClassification.objects.get(id=photo_classification_id)

            return photo_models.Photo.objects\
                .filter(Q(category=classification) | Q(tag=classification), public=True)\
                .order_by('-id')
        except ObjectDoesNotExist:
            raise NotFound


class PhotoFeedViewSet(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = photo_models.PhotoFeed.objects.filter(public=True)
    serializer_class = photo_serializers.PhotoFeedSerializer


class PhotoFeedPhotosViewSet(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)
    photo_feed = None
    serializer_class = photo_serializers.PhotoSerializer

    @setup_eager_loading
    def get_queryset(self):
        """
        Return list of photos for requested photo feed

        :return: Queryset
        """
        try:
            photo_feed_id = self.kwargs['photo_feed_id']
            self.photo_feed = photo_models.PhotoFeed.objects.get(id=photo_feed_id)
            queryset = photo_models.Photo.objects.filter(public=True)

            if self.photo_feed.randomize:
                q_count = queryset.count()
                page_size = self.paginator.get_page_size(self.request)
                count = page_size if page_size < q_count else q_count

                queryset = queryset\
                    .filter(id__in=list(common_models.get_random_queryset_elements(queryset, count, False)),
                            photo_feed=self.photo_feed)
            else:
                queryset = queryset.filter(photo_feed=self.photo_feed)\
                    .extra(select={'creation_seq': 'photo_photo_photo_feed.id'})\
                    .order_by('-creation_seq')

            if self.photo_feed.photo_limit:
                return queryset[:self.photo_feed.photo_limit]

            return queryset
        except ObjectDoesNotExist:
            raise NotFound


class PhotoSingleViewSet(generics.RetrieveDestroyAPIView, generics.UpdateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    @setup_eager_loading
    def get_queryset(self):
        return photo_models.Photo.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        Delete a photo

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id, public=True)

            # Photo must belong to authenticated user
            if photo.user == authenticated_user:
                photo.public = False
                photo.save()

                response = get_default_response('200')
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            raise NotFound

        return response

    def get(self, request, *args, **kwargs):
        """
        Get a photo

        :param request: Request object
        :return: Response object
        """
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id, public=True)

            response = get_default_response('200')
            response.data = photo_serializers.PhotoSerializer(photo).data
        except ObjectDoesNotExist:
            raise NotFound

        return response

    def patch(self, request, *args, **kwargs):
        """

        :param request:
        :return:
        """
        # Needs to be superuser
        if request.user.is_superuser:
            photo_id = kwargs.get('pk')
            payload = request.data
            payload = remove_pks_from_payload('photo', payload)
            payload = handle_jquery_empty_array('photo_feed', payload)
            payload = remove_pks_from_payload('user', payload)

            # Cannot change image
            if 'image' in payload:
                del payload['image']

            try:
                photo = photo_models.Photo.objects.get(id=photo_id)
                serializer = photo_serializers.PhotoSerializer(photo, data=payload, partial=True)

                if serializer.is_valid():
                    serializer.save()

                    response = get_default_response('200')
                    response.data = serializer.data
                    return response
                else:
                    raise ValidationError(serializer.errors)
            except ObjectDoesNotExist:
                raise NotFound
        else:
            raise PermissionDenied


class PhotoSingleFlagsViewSet(generics.CreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.UserInterest.objects.all()
    serializer_class = UserActionSerializer

    def post(self, request, **kwargs):
        """
        Create a flag entry

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user

        try:
            photo = photo_models.Photo.objects.get(id=kwargs.get('pk'))
            photo_content_type = ContentType.objects.get_for_model(photo)
            user_action = UserAction.objects.filter(user=authenticated_user, action='photo_flag',
                                                    content_type__pk=photo_content_type.id, object_id=photo.id).first()

            if user_action:
                return get_default_response('200')
            else:
                UserAction.objects.create(user=authenticated_user, action='photo_flag', content_object=photo)

                return get_default_response('201')
        except ObjectDoesNotExist:
            raise NotFound('Photo does not exist')


class PhotoSingleStarsViewSet(generics.DestroyAPIView, generics.CreateAPIView):
    """
    /api/photos/{}/interests
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.UserInterest.objects.all()
    serializer_class = account_serializers.UserInterestSerializer

    def delete(self, request, **kwargs):
        """
        Delete photo star

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        response = get_default_response('200')
        starred_photo_id = kwargs.get('pk')

        try:
            try:
                photo = photo_models.Photo.objects.get(id=starred_photo_id)
            except ObjectDoesNotExist:
                response = get_default_response('404')
                response.data['message'] = 'Photo does not exist'
                return response

            photo_type = ContentType.objects.get_for_model(photo)
            interest = account_models.UserInterest.objects.filter(user=authenticated_user, interest_type='star',
                                                                  content_type__pk=photo_type.id,
                                                                  object_id=photo.id)

            interest.delete()
        except ObjectDoesNotExist:
            # Return 200 even if user wasn't starred
            pass

        return response

    def post(self, request, **kwargs):
        """
        Star a photo

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        response = get_default_response('400')
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id)

            # Make sure there is no existing entry
            photo_type = ContentType.objects.get_for_model(photo)
            interest = account_models.UserInterest.objects \
                .filter(user=authenticated_user, interest_type='star', content_type__pk=photo_type.id,
                        object_id=photo.id) \
                .first()

            if not interest:
                account_models.UserInterest.objects.create(content_object=photo,
                                                           user=authenticated_user, interest_type='star')
                response = get_default_response('201')
            else:
                response = get_default_response('409')
        except ObjectDoesNotExist:
            response = get_default_response('404')
            response.data['message'] = 'User you attempted to star does not exist'

        return response
