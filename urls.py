from django.contrib import admin
from django.conf.urls.defaults import *


admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('handball.urls')),
    (r'^admin/', include(admin.site.urls))
)
