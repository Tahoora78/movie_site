from django.urls import path
from . import views

urlpatterns = [
    path("", views.movie_list,name="movie_list_page"),
    path("movie_page/<movie_name>", views.movie_page,name="movie_page")   
]