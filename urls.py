from django.contrib import admin
from django.conf.urls.defaults import *


admin.autodiscover()

urlpatterns = patterns('',
    (r'^auth/', include('auth.urls')),
    (r'^handball/', include('handball.urls')),
    (r'^admin/', include(admin.site.urls))
)
