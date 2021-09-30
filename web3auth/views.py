import json
import random
import string

from django.conf import settings
from django.views import View
from django.contrib.auth import get_user_model, login, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from web3auth.forms import AuthForm





class Web3AuthAPIView(View):
    http_method_names = ['get', 'post']
    MESSAGE = _(
        'Please sign this randomized token to verify your identity: '
    )

    def get(self, request):
        token = ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for i in range(32)
        )
        signable_message = self.MESSAGE + token
        request.session['login_token'] = signable_message
        return JsonResponse(
            {
                'token': signable_message,
                'success': True,
            }
        )

    def post(self, request):
        token = request.session.get('login_token')
        if not token:
            return JsonResponse(
                {
                    'error': _(
                        'No login token in session, please request token '
                        ' again by sending GET request to this url'
                    ),
                    'success': False
                }
            )
        else:
            form = AuthForm(token, request.POST)
            if form.is_valid():
                signature = form.cleaned_data.get("signature")
                address = form.cleaned_data.get("address")
                del request.session['login_token']
                try:
                    user = authenticate(
                        request, token=token,
                        address=address, signature=signature
                    )
                except ValueError as exc:
                    return JsonResponse(
                        {
                            'success': False, 'error': str(exc)
                        }
                    )
                login(request, user, 'web3auth.backend.Web3Backend')
                return JsonResponse(
                    {
                        'success': True,
                        'redirect_url': self.get_redirect_url(request)
                    }
                )
            else:
                return JsonResponse(
                    {
                        'success': False,
                        'error': json.loads(form.errors.as_json())
                    }
                )

    def get_redirect_url(self, request):
        if request.GET.get('next'):
            return request.GET.get('next')
        elif request.POST.get('next'):
            return request.POST.get('next')
        elif (referer := request.META.get('HTTP_REFERER')):
            return referer
        elif settings.LOGIN_REDIRECT_URL:
            try:
                url = reverse(settings.LOGIN_REDIRECT_URL)
            except NoReverseMatch:
                url = settings.LOGIN_REDIRECT_URL
            return url
