import json
import random
import string

from django.conf import settings
from django.views import View
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods


from web3auth.forms import LoginForm, SignupForm
from web3auth.settings import app_settings


def get_redirect_url(request):
    if request.GET.get('next'):
        return request.GET.get('next')
    elif request.POST.get('next'):
        return request.POST.get('next')
    elif settings.LOGIN_REDIRECT_URL:
        try:
            url = reverse(settings.LOGIN_REDIRECT_URL)
        except NoReverseMatch:
            url = settings.LOGIN_REDIRECT_URL
        return url


class LoginApiView(View):
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

        request.session['login_token'] = token
        return JsonResponse(
            {
                'message': self.MESSAGE,
                'token': token,
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
            form = LoginForm(token, request.POST)
            if form.is_valid():
                signature = form.cleaned_data.get("signature")
                address = form.cleaned_data.get("address")
                del request.session['login_token']
                user = authenticate(
                    request, token=token, address=address, signature=signature
                )
                breakpoint()
                if user:
                    login(request, user, 'web3auth.backend.Web3Backend')
                    return JsonResponse(
                        {
                            'success': True,
                            'redirect_url': get_redirect_url(request)
                        }
                    )
                else:
                    error = _(
                        'Can\'t find a user for the provided signature '
                        'with address {}'
                    ).format(address)
                    return JsonResponse({'success': False, 'error': error})
            else:
                return JsonResponse(
                    {
                        'success': False,
                        'error': json.loads(form.errors.as_json())
                    }
                )


class SignUpApiView(View):
    http_method_names = ['post']

    def post(self, request):
        if not app_settings.WEB3AUTH_SIGNUP_ENABLED:
            return JsonResponse(
                {
                    'success': False,
                    'error': _("Sorry, signup's are currently disabled")
                }
            )
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            addr_field = app_settings.WEB3AUTH_USER_ADDRESS_FIELD
            setattr(user, addr_field, form.cleaned_data[addr_field])
            user.save()
            login(request, user, 'web3auth.backend.Web3Backend')
            return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
        else:
            return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})
