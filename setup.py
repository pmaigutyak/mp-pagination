
from setuptools import setup, find_packages


version = '0.3.0'
url = 'https://github.com/pmaigutyak/mp-pagination'

setup(
    name='django-mp-pagination',
    version=version,
    description='Django pagination app',
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='{}/archive/{}.tar.gz'.format(url, version),
    packages=find_packages(),
    include_package_data=True,
    license='MIT'
)
