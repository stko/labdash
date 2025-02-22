from setuptools import setup

setup(
    name='labdash',
    version='0.0.2',
    description='Generic Diagnostic Program with Web UI',
    license='LGPL',
    packages=['labdash'],
    install_requires=[
        'python-can',
        'oyaml',
        'bitstring',
	'flask',
	'flask-sockets',
	'lxml',
	'python-can',
	'canopen'
    ],
    author='Steffen Köhler',
    author_email='steffen@koehlers.de',
    keywords=['canbus',"diagnostics","webUI"],
    url='https://github.com/stko/labdash'
)
