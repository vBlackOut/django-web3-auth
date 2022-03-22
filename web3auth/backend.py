from abc import abstractmethod, ABC
from typing import Optional

from django.contrib.auth import get_user_model, backends
from django.conf import settings

from web3auth.utils import recover_to_addr

User = get_user_model()

DEFAULT_ADDRESS_FIELD = 'username'
ADDRESS_FIELD = getattr(
    settings, 'WEB3AUTH_USER_ADDRESS_FIELD', DEFAULT_ADDRESS_FIELD)
DEFAULT_ENS_FIELD = 'ens_name'
ENS_FIELD = getattr(
    settings, 'WEB3AUTH_USER_ENS_FIELD', DEFAULT_ENS_FIELD)


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
            kwargs = {
                f"{ADDRESS_FIELD}__iexact": address
            }
            # try to get user with provided data
            user = User.objects.filter(**kwargs).first()
            if user is None:
                # create the user if it does not exist
                return self.create_user(address)
            return user

    def create_user(self, address):
        user = self._gen_user(address)
        fields = [field.name for field in User._meta.fields]
        if (
                ADDRESS_FIELD != DEFAULT_ADDRESS_FIELD
                and 'username' in fields
        ):
            user.username = user.generate_username()
        user.save()
        return user

    def _gen_user(self, address: str) -> User:
        return User(**{ADDRESS_FIELD: address})


class ENSWeb3BaseBackend(Web3Backend, ABC):
    """
    Abstract auth backend that supplies the ENS domain name in the User account
    To make use of this backend you need to define a `fetch_ens` method in a
    backend of your own, one that calls your own web3 client to fetch
    the domain record from the user's wallet address.
    """

    def authenticate(
            self,
            request,
            address,
            token,
            signature
    ) -> Optional[User]:
        user = super().authenticate(request, address, token, signature)
        new_ens_name = self.fetch_ens(user.address)
        if user.ens_name != new_ens_name:
            user.ens_name = new_ens_name
            user.save(update_fields=['ens_name'])
        return user

    def _gen_user(
            self,
            address: str,
    ) -> User:
        return User(
            **{
                ADDRESS_FIELD: address,
                ENS_FIELD: self.fetch_ens(address)
            }
        )

    @abstractmethod
    def fetch_ens(self, address: str) -> str:
        raise NotImplemented
