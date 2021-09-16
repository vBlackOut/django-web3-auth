from django.urls import path, include

from web3auth import views

app_name = 'web3auth'




urlpatterns = [
    path('login_api/', views.LoginApiView.as_view(), name='web3auth_login_api'),
    path('signup_api/', views.SignUpApiView.as_view(), name='web3auth_signup_api'),
]
