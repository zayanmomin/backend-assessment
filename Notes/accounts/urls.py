from django.urls import path
from .views import register, login, user_view, logout

urlpatterns = [
    path('api/auth/signup/', register, name="register"),
    path('api/auth/login/', login, name="login"),
    path('api/auth/user/', user_view, name="user"),
    path('api/auth/logout/', logout, name="logout"),
]