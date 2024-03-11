
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/matricula/', include('matricula.api.routers')),
    path('api/usuarios/', include('users.api.routers')),
]
