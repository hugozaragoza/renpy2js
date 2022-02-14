from django.urls import path

from . import views

urlpatterns = [
    
    # ex: /userlog/
    path('', views.index, name='index'),
    
    # ex: /userlog/USER_NAME/log/MESSAGE
    path('<str:user>/log/<str:msg>', views.log, name='log'),
]