from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
   path('', views.home,name="home"),
   path('signup',views.signup,name="signup"),
   path('signin',views.signin,name="signin"),
   path('signout',views.signout,name="signout"),
   path('base',views.base,name="base"), 
   path('Page',views.Page,name="Page"),
   path('activate/<uidb64>/<token>',views.activate,name="activate"), 
   ]