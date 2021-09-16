from django.urls import path, include

from web3auth import views

app_name = 'web3auth'


urlpatterns = [
    path('web3auth/', views.Web3AuthAPIView.as_view(), name='web3auth_api'),
]
