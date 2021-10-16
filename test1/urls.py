from django.urls import path
from . import views

app_name = 'test1'

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/', views.html_dom_ajax, name='html_dom_ajax'),
]