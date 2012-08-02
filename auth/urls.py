from django.conf.urls.defaults import *
from tastypie.api import Api
from auth.api import *


v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(ProfileResource())

urlpatterns = patterns('auth.views',
    (r'^activate/([abcdef0123456789]+)$', 'activate')
)

urlpatterns += patterns('', (r'^api/', include(v1_api.urls)))

# Non-resource api endpoints
urlpatterns += patterns('auth.api',
    (r'^api/v1/validate/$', 'validate_user'),
    (r'^api/v1/unique/$', 'is_unique'),
    (r'^api/v1/signup/$', 'sign_up')
)
