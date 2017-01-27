from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from patool import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^student/', include('student.urls')),
    url(r'^teacher/', include('teacher.urls')),
    url(r'^prepdb', views.populate_database, name='prepdb'),
    url(r'^$', views.default_index, name='site_root'),
] + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
