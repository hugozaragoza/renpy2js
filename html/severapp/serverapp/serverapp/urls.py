from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('userlog/', include('userlog.urls')),
    path('admin/', admin.site.urls),
]
