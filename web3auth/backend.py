from typing import Optional
from typing import Optional

from django.contrib.auth import get_user_model, backends
from django.conf import settings

from web3auth.utils import recover_to_addr

User = get_user_model()


class Web3Backend(backends.ModelBackend):

    def authenticate(
            self,
            request,
            address,
            token,
            signature
    ) -> Optional[User]:
        # check if the address the user has provided matches the signature
        if address != recover_to_addr(token, signature):
            raise ValueError('Wallet address does not match signature')
        else:
            # get address field for the user model
            address_field = getattr(
                settings, 'WEB3AUTH_USER_ADDRESS_FIELD', 'username')
            kwargs = {
                f"{address_field}__iexact": address
            }
            # try to get user with provided data
            user = User.objects.filter(**kwargs).first()
            if user is None:
                # create the user if it does not exist
                user = User.objects.create(**{address_field: address})
            return user
