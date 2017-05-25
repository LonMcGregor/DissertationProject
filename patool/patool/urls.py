from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from patool import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^student/', include('student.urls')),
    url(r'^teacher/', include('teacher.urls')),
    url(r'^test_match/', include('test_match.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^file/', include('file_viewer.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^$', views.default_index, name='site_root'),
] + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
