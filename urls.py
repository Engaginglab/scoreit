from django.contrib import admin
from django.conf.urls.defaults import *
from tastypie.api import Api
from handball.api import *


admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(UnionResource())
v1_api.register(ClubResource())
v1_api.register(TeamResource())
v1_api.register(UserResource())
v1_api.register(PersonResource())
v1_api.register(GameResource())

urlpatterns = patterns('',
    (r'^', include('handball.urls')),
    (r'^api/', include(v1_api.urls)),
    (r'^admin/', include(admin.site.urls))
)
