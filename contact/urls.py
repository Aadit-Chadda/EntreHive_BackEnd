from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.create_contact_inquiry, name='create-inquiry'),
]

