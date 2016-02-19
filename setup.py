import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'zeroc-ice',
    'gevent',
    'futures',
    'pyramid_mako',
    'PasteDeploy==1.5.0',
    'APScheduler==2.1.1',
    'Beaker==1.6.4',
    'Chameleon==2.11',
    'Mako==0.8.1',
    'MarkupSafe==0.18',
    'pymysql',
    'Paste==1.7.5.1',
    'PasteDeploy==1.5.0',
    'Pygments==1.6',
    'SQLAlchemy==0.8.3',
    'Tempita==0.5.1',
    'celery==3.0.21',
    'celery-with-redis==3.0',
    'elasticsearch==1.1.0',
    'envoy==0.0.2',
    'hiredis==0.1.3',
    'intstr==0.11',
    'kombu==2.5.12',
    'msgpack-python==0.4.2',
    'pyOpenSSL==0.13',
    'pymongo==2.6.3',
    'pyramid==1.4.3',
    'pyramid-beaker==0.8',
    'pyramid-debugtoolbar==1.0.6',
    'pyramid-tm==0.7',
    'python-dateutil==2.1',
    'pyzmq==13.1.0',
    'qiniu==6.1.2',
    'raven==3.4.1',
    'redis==2.10.1',
    'repoze.lru==0.6',
    'repoze.tm2==2.0',
    'requests==1.2.3',
    'rfc3987==1.3.4',
    'six==1.3.0',
    'thrift==0.9.1',
    'torndb==0.1',
    'transaction==1.4.1',
    'uWSGI==1.9.14',
    'ujson==1.33',
    'venusian==1.0a8',
    'waitress==0.8.6',
    'wsgiref==0.1.2',
    'zope.deprecation==4.0.2',
    'zope.interface==4.0.5',
    'zope.sqlalchemy==0.7.2',
    'statsd',
    'supervisor',
    'Pillow'
    ]

setup(name='hichao',
      version='5.2',
      description='hichao',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='hichao',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = hichao:main
      [console_scripts]
      initialize_hichao_db = hichao.scripts.initializedb:main
      """,
      )
