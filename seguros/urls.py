from django.urls import path
from . import views
from .views import ApoliceListView, ClientListView, ClientCreateView, ClientDetailView


urlpatterns = [
    path('', ApoliceListView.as_view(), name='index'),
    
    path('clients/', ClientListView.as_view(), name='clients_list'),
    path('clients/new', ClientCreateView.as_view(), name='clients_create'),
    path('clients/<int:pk>', ClientDetailView.as_view(), name='ver_segurado'),

    path('nova_apolice/<int:pk>', views.nova_apolice, name='nova_apolice'),

    path('apolice/<str:pk>', views.ver_apolice, name='ver_apolice'),

    path('edit_apolice/<str:pk>', views.editar_apolice, name='editar_apolice'),
    path('edit_segurado/<int:pk>', views.editar_segurado, name='editar_segurado'),
    
    path('del_segurado/<int:pk>', views.deletar_segurado, name='deletar_segurado'),
    path('del_apolice/<str:pk>', views.deletar_apolice, name='deletar_apolice'),    
    
    path('relatorio', views.relatorio, name='relatorio'),
]
