from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.formulario_novo_user, name='cad_usuario'),
    path('salva_usuario', views.salva_usuario, name='salva_usuario'),
]