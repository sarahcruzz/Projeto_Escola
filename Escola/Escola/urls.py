
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('App_Escola.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('usuarios/', include('App_User.urls')),

]
