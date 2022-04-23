import string

from django import forms
from django.contrib.auth import get_user_model
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

from .fields import EthAddressFormField
from .utils import validate_eth_address, recover_to_addr


class AuthForm(forms.Form):
    signature = forms.CharField(max_length=132)
    address = EthAddressFormField()

    def __init__(self, token, *args, **kwargs):
        self.token = token
        super().__init__(*args, **kwargs)

    def clean_signature(self):
        sig = self.cleaned_data['signature']
        if any([
            len(sig) != 132,
            sig[130:] != '1b' and sig[130:] != '1c',
            not all(c in string.hexdigits for c in sig[2:])
        ]):
            raise forms.ValidationError(_('Invalid signature'))
        return sig

    def clean(self):
        cleaned_data = super().clean()
        signature = cleaned_data.get('signature')
        address = cleaned_data.get('address')
        if address != recover_to_addr(self.token, signature):
            raise forms.ValidationError(
                _('Address used for signing does not match wallet address')
            )
