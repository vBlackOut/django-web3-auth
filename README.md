# django-web3-auth

django-web3-auth is a pluggable Django app that enables login/signup via an Ethereum wallet (specifically MetaMask).  
The user authenticates themselves by digitally signing the session key with their wallet's private key.
  
Use with django >= 3.2.0, python >= 3.9

## Quickstart
Install django-web3-auth with pip:
```bash
pip install git+ssh://git@github.com/krilarite/django-web3-auth.git
```
Add it to your INSTALLED_APPS:
```python
INSTALLED_APPS = [
    ...
    'web3auth',
    ...
]
```
Set 'web3auth.backend.Web3Backend' as your authentication backend:
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'web3auth.backend.Web3Backend'
]
```
Set a field from the User model for storing the users' ETH address:
```python
WEB3AUTH_USER_ADDRESS_FIELD = 'username'
```
Add Django-Web3-Auth's URL patterns:
```python
from web3auth import urls as web3auth_urls

urlpatterns = [
    ...
    path('', include(web3auth_urls)),
    ...
]
```
Add some javascript to handle login:
```html
  <script src="{% static 'web3auth/js/web3.js' %}"></script>
  <script src="{% static 'web3auth/js/web3auth.js' %}"></script>
```
Implement a login button:
```html
<button type="button" onclick="connectWallet()">Connect wallet</button>
<script>
async function connectWallet() {
    var authUrl = "{% url 'web3auth:web3auth_api' %}";
    await authWeb3(authUrl, console.log, console.log, console.log, console.log, console.log, function (resp) {
        window.location.replace(resp.redirect_url);
    });
};
</script>
```
MetaMask will prompt you to sign a message and you'll be logged in afterwards.


## Contributing
Clone the project
```bash
git clone git@github.com:krilarite/django-web3-auth.git
```
Set up a virtualenv
```
mkvirtualenv -p /usr/bin/python3.9 -a `pwd` django-web3-auth
pip install -r requirements.txt
```
Use the example project for testing
```bash
cd example
python manage.py migrate
python manage.py runserver
```
Navigate to `localhost:8000/login` and you'll see a login page.
