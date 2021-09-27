from django.db import models
from django import forms

from web3auth.utils import validate_eth_address, validate_eth_transaction


class EthAddressField(models.CharField):

    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 42
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True
        super().__init__(*args, **kwargs)
        self.validators.append(validate_eth_address)


class EthAddressFormField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 42
        super().__init__(*args, **kwargs)
        self.validators.append(validate_eth_address)


class EthTransactionField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 64
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True
        super().__init__(*args, **kwargs)
        self.validators.append(validate_eth_transaction)


class EthTransactionFormField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 64
        super().__init__(*args, **kwargs)
        self.validators.append(validate_eth_transaction)
