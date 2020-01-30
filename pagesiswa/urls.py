from django.urls import path, include
from . import views
app_name = 'pagesiswa'

urlpatterns = [
    path('', views.redirect_site, name='redirect_site'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_siswa, name='profile'),
    path('ujian/', views.ujian, name='ujian'),
    path('review/', views.review, name='review'),
    path('dummy/', views.faker, name='dummy')
]
