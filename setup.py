from setuptools import setup, find_packages


with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()


def main():
    pkg_setup = {
        'name': 'django-web3-auth',
        'version': '0.0.1',
        'description': 'Django authentication using an Ethereum wallet',
        'long_description': LONG_DESCRIPTION,
        'long_description_content_type': 'text/markdown',
        'author': 'Teodor Ivanov',
        'author_email': 'tdrivanov@gmail.com',
        'packages': find_packages(exclude=['*tests*']),
        'python_requires': '>=3.9',
        'install_requires': [
            'ethereum==2.3.*',
            'eth_utils==1.10.*',
        ],
        'extras_require': {},
        'include_package_data': True,
        'license': 'MIT',
        'project_urls': {
            'Source': 'https://github.com/krilarite/django-web3-auth',
        },
    }
    setup(**pkg_setup)


if __name__ == '__main__':
    main()
