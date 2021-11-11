from django.conf import settings
from django.urls import path, include

from web3auth import views

app_name = 'web3auth'


urlpatterns = [
    path('web3auth/', views.Web3AuthAPIView.as_view(), name='web3auth_api'),
]

if getattr(settings, 'MOCK_LOGIN', False) and settings.DEBUG:
    urlpatterns += [
        path(
            'mocklogin/',views.MockLoginView.as_view(), name='web3auth_mock'
        ),
    ]
