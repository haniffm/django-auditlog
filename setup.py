from distutils.core import setup

setup(
    name='django-auditlog',
    version='0.4.5.1',
    packages=['auditlog'],
    package_dir={'': 'src'},
    url='https://github.com/haniffm/django-auditlogger',
    license='MIT',
    author='Jan-Jelle Kester',
    description='Audit log app for Django',
    install_requires=[
        'django-jsonfield>=1.0.0',
    ],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],        
)
