from auth.forms import SignUpForm
import sha
import datetime
from random import random
import pytz
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from tastypie.serializers import Serializer
from tastypie.utils.mime import determine_format
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.models import ApiKey
from tastypie import fields
from auth.models import Profile
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import Authentication, ApiKeyAuthentication


class ApiKeyResource(ModelResource):
    class Meta:
        allowed_methods = []
        queryset = ApiKey.objects.all()


class UserResource(ModelResource):
    auth_profile = fields.OneToOneField('auth.api.ProfileResource', 'auth_profile', full=True)
    handball_profile = fields.OneToOneField('handball.api.PersonResource', 'handball_profile', blank=True, null=True, full=True)
    api_key = fields.OneToOneField(ApiKeyResource, 'api_key', full=True)

    class Meta:
        allowed_methods = ['get']
        queryset = User.objects.all()
        excludes = ['email', 'password']


class ProfileResource(ModelResource):
    user = fields.OneToOneField(UserResource, 'user')

    class Meta:
        queryset = Profile.objects.all()
        authorization = Authorization()
        authentication = Authentication()
        excludes = ['activation_key', 'key_expires']
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'first_name': ['exact'],
            'last_name': ['exact']
        }

    # def dehydrate(self, bundle):
    #     bundle.data['display_name'] = str(bundle.obj)
    #     return bundle


def sign_up(request):
    form = SignUpForm(request.POST)
    serializer = Serializer()
    format = determine_format(request, serializer,
        default_format='application/json')

    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']

        user = User.objects.create(username=username, first_name=first_name,
            last_name=last_name, email=email, is_active=False)
        user.set_password(password)
        user.save()

        auth_profile = user.get_profile()

        # Build the activation key
        salt = sha.new(str(random())).hexdigest()[:5]
        activation_key = sha.new(salt + user.username).hexdigest()
        key_expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(2)

        # User is unactive until visiting activation link
        auth_profile.activation_key = activation_key
        auth_profile.key_expires = key_expires
        activation_link = 'http://127.0.0.1:8000/auth/activate/' + activation_key

        auth_profile.save()

        subject = _('Welcome to ScoreIt!')
        message = _('To activate, please click the following link:\n' + activation_link)
        sender = _('noreply@score-it.de')
        recipients = [email]
        send_mail(subject, message, sender, recipients)

        user_resource = UserResource()
        bundle = user_resource.build_bundle(obj=user, request=request)
        user_resource.full_dehydrate(bundle)

        return HttpResponse(user_resource.serialize(None, bundle, 'application/json'))
    else:
        return HttpResponseBadRequest(serializer.serialize(form.errors, format, {}))


def validate_user(request):
    """
    Checks a user's basic auth credentials and, if valid, returns the users data
    """

    # if not request.META.get('HTTP_AUTHORIZATION'):
    #     return HttpResponseBadRequest('No HTTP_AUTHORIZATION header found')

    # try:
    #     (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()
    #     if auth_type.lower() != 'basic':
    #         return HttpResponseBadRequest('Wrong auth type. Use basic auth!')
    #     user_pass = base64.b64decode(data)
    # except:
    #     return HttpResponseBadRequest('Could not decode auth credentials.')

    # bits = user_pass.split(':', 1)

    # if len(bits) != 2:
    #     return HttpResponseBadRequest('Could not decode auth credentials.')

    # user = authenticate(username=bits[0], password=bits[1])

    username = request.POST['username']
    password = request.POST['password']

    if not username or not password:
        return HttpResponseBadRequest()

    user = authenticate(username=username, password=password)

    if user is None:
        return HttpResponseNotFound('User does not exist or password incorrect.')
    if not user.is_active:
        return HttpResponseNotFound('This user has not been activated yet!')

    user_resource = UserResource()
    bundle = user_resource.build_bundle(obj=user, request=request)
    user_resource.full_dehydrate(bundle)
    # auth_profile = user.get_profile()

    # profile_resource = ProfileResource()
    # bundle = profile_resource.build_bundle(obj=auth_profile, request=request)
    # profile_resource.full_dehydrate(bundle)
    # bundle.data['api_key'] = user.api_key.key

    return HttpResponse(user_resource.serialize(None, bundle, 'application/json'))


def is_unique(request):
    data = {}

    if 'user_name' in request.GET:
        username = request.GET['user_name']

        try:
            User.objects.get(username=username)
            unique = False
        except User.DoesNotExist:
            unique = True
        except User.MultipleObjectsReturned:
            unique = False

        data['user_name'] = unique

    if 'email' in request.GET:
        email = request.GET['email']

        try:
            User.objects.get(email=email)
            unique = False
        except User.DoesNotExist:
            unique = True
        except User.MultipleObjectsReturned:
            unique = False

        data['email'] = unique

    serializer = Serializer()

    format = determine_format(request, serializer, default_format='application/json')

    return HttpResponse(serializer.serialize(data, format, {}))
