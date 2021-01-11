# noinspection PyProtectedMember
import json
import string
from datetime import datetime
from random import choice
from urllib.parse import urlparse

import django.middleware.csrf
import requests
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import DisallowedHost
from django.utils.http import is_same_domain
from jwcrypto import jws, jwt, jwk
from rest_framework.authentication import BaseAuthentication

import config
from api.models import User

html_color_list = [
    'AliceBlue',
    'Aqua',
    'Aquamarine',
    'Beige',
    'Bisque',
    'Black',
    'BlanchedAlmond',
    'Blue',
    'BlueViolet',
    'Brown',
    'BurlyWood',
    'CadetBlue',
    'Chartreuse',
    'Chocolate',
    'Coral',
    'CornflowerBlue',
    'Cornsilk',
    'Crimson',
    'Cyan',
    'DarkBlue',
    'DarkCyan',
    'DarkGoldenRod',
    'DarkGray',
    'DarkGrey',
    'DarkGreen',
    'DarkKhaki',
    'DarkMagenta',
    'DarkOliveGreen',
    'DarkOrange',
    'DarkOrchid',
    'DarkRed',
    'DarkSalmon',
    'DarkSeaGreen',
    'DarkSlateBlue',
    'DarkSlateGray',
    'DarkSlateGrey',
    'DarkTurquoise',
    'DarkViolet',
    'DeepPink',
    'DeepSkyBlue',
    'DimGray',
    'DimGrey',
    'DodgerBlue',
    'FireBrick',
    'ForestGreen',
    'Fuchsia',
    'Gainsboro',
    'Gold',
    'GoldenRod',
    'Gray',
    'Grey',
    'Green',
    'GreenYellow',
    'HotPink',
    'IndianRed ',
    'Indigo  ',
    'Ivory',
    'Khaki',
    'Lavender',
    'LawnGreen',
    'Lime',
    'LimeGreen',
    'Linen',
    'Magenta',
    'Maroon',
    'MediumAquaMarine',
    'MediumBlue',
    'MediumOrchid',
    'MediumPurple',
    'MediumSeaGreen',
    'MediumSlateBlue',
    'MediumSpringGreen',
    'MediumTurquoise',
    'MediumVioletRed',
    'MidnightBlue',
    'MintCream',
    'MistyRose',
    'Moccasin',
    'Navy',
    'OldLace',
    'Olive',
    'OliveDrab',
    'Orange',
    'OrangeRed',
    'Orchid',
    'PaleGoldenRod',
    'PaleGreen',
    'PaleTurquoise',
    'PaleVioletRed',
    'PapayaWhip',
    'PeachPuff',
    'Peru',
    'Pink',
    'Plum',
    'PowderBlue',
    'Purple',
    'RebeccaPurple',
    'Red',
    'RosyBrown',
    'RoyalBlue',
    'SaddleBrown',
    'Salmon',
    'SandyBrown',
    'SeaGreen',
    'Sienna',
    'Silver',
    'SkyBlue',
    'SlateBlue',
    'SlateGray',
    'SlateGrey',
    'Snow',
    'SpringGreen',
    'SteelBlue',
    'Tan',
    'Teal',
    'Thistle',
    'Tomato',
    'Turquoise',
    'Violet',
    'Wheat',
    'Yellow',
    'YellowGreen',
]


def get_random_id():
    """Time based random id"""
    x, base = int((datetime.now().timestamp() - datetime(2020, 10, 1).timestamp()) * 1000), 62
    digs = string.digits + string.ascii_letters
    if x == 0:
        return digs[0]
    if x < 0:
        sign = -1
    else:
        sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)


def get_colors(amount=1):
    c = []
    while len(c) < amount:
        cc = choice(html_color_list)
        while cc in c:
            cc = choice(html_color_list)
        c.append(cc)
    return c


class JsonFileManagement:
    def __init__(self, directory):
        self.dir = directory
        with open(self.dir, 'r+') as config:
            try:
                self.config = json.loads(config.read())
            except json.JSONDecodeError:
                self.config = {}

    def write(self, key, value):
        self.config[key] = value
        with open(self.dir, 'w+') as config:
            config.write(json.dumps(self.config))

    def read(self, key, default=None):
        value = self.config.get(key, None)
        if value is None:
            self.write(key, default)
            return default
        return value


def jwt_reader(jwt_str):
    key = config.jwt_secret
    try:
        st = jwt.JWT(key=key, jwt=jwt_str)
        return json.loads(st.claims)
    except (jws.InvalidJWSSignature, jws.InvalidJWSObject):
        return None


def jwt_writer(**kwargs):
    key = jwk.JWK(**config.jwt_secret)
    token = jwt.JWT(header={'alg': 'HS256'}, claims=kwargs)
    token.make_signed_token(key)
    return token.serialize()


def is_valid_jwt_header(request):
    if request.headers.get('x-auth-token', False):
        jwt_str = request.headers['x-auth-token']
        try:
            st = jwt.JWT(key=jwk.JWK(**config.jwt_secret), jwt=jwt_str)
            data = json.loads(st.claims)
            try:
                return User.objects.get(username=data.get('username'), email=data.get('email'))
            except User.DoesNotExist:
                return None
        except (jws.InvalidJWSSignature, jws.InvalidJWSObject, ValueError):
            return None
    return None


def cur_user(request):
    return request.user


def get_or_create(model, **kwargs):
    model.objects.get_or_create(**kwargs)
    return model.objects.get(**kwargs)


def get_url_content(url):
    while True:
        try:
            return requests.get(url).content
        except (TimeoutError, ConnectionError):
            pass


class ModelBackendWithJwt(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            username = json.loads(request.body).get('username')
            password = json.loads(request.body).get('password')
        except json.JSONDecodeError:
            pass
        if request.headers.get('x-auth-token', False):
            if is_valid_jwt_header(request):
                return is_valid_jwt_header(request)

        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class RestAuthenticateWithJwt(BaseAuthentication):
    def authenticate_header(self, request):
        if request.headers.get('x-auth-token', False):
            if is_valid_jwt_header(request):
                return is_valid_jwt_header(request)

    def authenticate(self, request):
        if request.headers.get('x-auth-token', False):
            if is_valid_jwt_header(request):
                return is_valid_jwt_header(request), None
        username, password = None, None
        try:
            username = json.loads(request.body).get('username')
            password = json.loads(request.body).get('password')
        except json.JSONDecodeError:
            pass
        if username:
            try:
                user = User._default_manager.get_by_natural_key(username)
            except User.DoesNotExist:
                User().set_password(password)
            else:
                if user.check_password(password):
                    return user, None


class JwtCsrfMiddleWare(django.middleware.csrf.CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, 'csrf_processing_done', False):
            return None
        if getattr(callback, 'csrf_exempt', False):
            return None
        # Only 5 lines of changes compared to actual CsrfViewMiddleware
        is_valid_jwt = is_valid_jwt_header(request)
        if is_valid_jwt or str(request.META.get('PATH_INFO')) in settings.SAFE_URL:
            if is_valid_jwt:
                request.user = is_valid_jwt  # Login user
            return self._accept(request)
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                return self._accept(request)
            if request.is_secure():
                referer = request.META.get('HTTP_REFERER')
                if referer is None:
                    return self._reject(request, django.middleware.csrf.REASON_NO_REFERER)
                referer = urlparse(referer)
                if '' in (referer.scheme, referer.netloc):
                    return self._reject(request, django.middleware.csrf.REASON_MALFORMED_REFERER)
                if referer.scheme != 'https':
                    return self._reject(request, django.middleware.csrf.REASON_INSECURE_REFERER)
                good_referer = (
                    settings.SESSION_COOKIE_DOMAIN
                    if settings.CSRF_USE_SESSIONS
                    else settings.CSRF_COOKIE_DOMAIN
                )
                if good_referer is not None:
                    server_port = request.get_port()
                    if server_port not in ('443', '80'):
                        good_referer = '%s:%s' % (good_referer, server_port)
                else:
                    try:
                        good_referer = request.get_host()
                    except DisallowedHost:
                        pass
                good_hosts = list(settings.CSRF_TRUSTED_ORIGINS)
                if good_referer is not None:
                    good_hosts.append(good_referer)
                if not any(is_same_domain(referer.netloc, host) for host in good_hosts):
                    reason = django.middleware.csrf.REASON_BAD_REFERER % referer.geturl()
                    return self._reject(request, reason)
            csrf_token = self._get_token(request)
            if csrf_token is None:
                return self._reject(request, django.middleware.csrf.REASON_NO_CSRF_COOKIE)
            request_csrf_token = ""
            if request.method == "POST":
                try:
                    request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
                except OSError:
                    pass
            if request_csrf_token == "":
                request_csrf_token = request.META.get(settings.CSRF_HEADER_NAME, '')
            request_csrf_token = django.middleware.csrf._sanitize_token(request_csrf_token)
            if not django.middleware.csrf._compare_salted_tokens(request_csrf_token, csrf_token):
                return self._reject(request, django.middleware.csrf.REASON_BAD_TOKEN)
        return self._accept(request)


class NoCsrfMiddleWare(django.middleware.csrf.CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        return self._accept(request)
