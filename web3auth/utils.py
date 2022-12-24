import sha3

from py_ecc.secp256k1 import ecdsa_raw_recover
from eth_utils import is_hex_address, is_hex

from django.core.exceptions import ValidationError
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _


from rlp.utils import ALL_BYTES


try:
    import coincurve
except ImportError:
    import warnings
    warnings.warn('could not import coincurve', ImportWarning)
    coincurve = None


def zpad(x, l):
    """ Left zero pad value `x` at least to length `l`.

    >>> zpad('', 1)
    '\x00'
    >>> zpad('\xca\xfe', 4)
    '\x00\x00\xca\xfe'
    >>> zpad('\xff', 1)
    '\xff'
    >>> zpad('\xca\xfe', 2)
    '\xca\xfe'
    """
    return b'\x00' * max(0, l - len(x)) + x

def int_to_32bytearray(i):
    o = [0] * 32
    for x in range(32):
        o[31 - x] = i & 0xff
        i >>= 8
    return o


def bytearray_to_bytestr(value):
    return bytes(value)


def ascii_chr(n):
    return ALL_BYTES[n]


def encode_int32(v):
    return v.to_bytes(32, byteorder='big')


def ecrecover_to_pub(rawhash, v, r, s):
    if coincurve and hasattr(coincurve, "PublicKey"):
        try:
            pk = coincurve.PublicKey.from_signature_and_message(
                zpad(bytearray_to_bytestr(int_to_32bytearray(r)), 32) + zpad(bytearray_to_bytestr(int_to_32bytearray(s)), 32) +
                ascii_chr(v - 27),
                rawhash,
                hasher=None,
            )
            pub = pk.format(compressed=False)[1:]
        except BaseException:
            pub = b"\x00" * 64
    else:
        result = ecdsa_raw_recover(rawhash, (v, r, s))
        if result:
            x, y = result
            pub = encode_int32(x) + encode_int32(y)
        else:
            raise ValueError('Invalid VRS')
    assert len(pub) == 64
    return pub


def sig_to_vrs(sig):
    #    sig_bytes = bytes.fromhex(sig[2:])
    r = int(sig[2:66], 16)
    s = int(sig[66:130], 16)
    v = int(sig[130:], 16)
    return v, r, s


def hash_personal_message(msg):
    padded = "\x19Ethereum Signed Message:\n" + str(len(msg)) + msg
    return sha3.keccak_256(bytes(padded, 'utf8')).digest()


def recover_to_addr(msg, sig):
    msghash = hash_personal_message(msg)
    vrs = sig_to_vrs(sig)
    address = '0x' + sha3.keccak_256(
        ecrecover_to_pub(msghash, *vrs)).hexdigest()[24:]
    return address


def validate_eth_address(value):
    if not is_hex_address(value):
        raise ValidationError(
            _('%(value)s is not a valid Ethereum address'),
            params={'value': value},
        )


def validate_eth_transaction(value):
    if not all(
        [
            isinstance(value, str),
            is_hex(value),
        ]
    ):
        raise ValidationError(
            _('%(value)s is not a valid Ethereum transaction id'),
            params={'value': value},
        )
