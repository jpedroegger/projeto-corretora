from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('lista_segurados/', views.lista_segurados, name='lista_segurados'),

    path('nova_apolice/<int:pk>', views.nova_apolice, name='nova_apolice'),
    path('novo_segurado/', views.novo_segurado, name='novo_segurado'),

    path('apolice/<str:pk>', views.ver_apolice, name='ver_apolice'),
    path('segurado/<int:pk>', views.ver_segurado, name='ver_segurado'),

    path('edit_apolice/<str:pk>', views.editar_apolice, name='editar_apolice'),
    path('edit_segurado/<int:pk>', views.editar_segurado, name='editar_segurado'),
    
    path('del_segurado/<int:pk>', views.deletar_segurado, name='deletar_segurado'),
    path('del_apolice/<str:pk>', views.deletar_apolice, name='deletar_apolice'),    
    
    path('relatorio', views.relatorio, name='relatorio'),
]
