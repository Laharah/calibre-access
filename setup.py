from setuptools import setup

setup(
    name='calibre-access',
    version='1.3.8',
    url='',
    license='MIT',
    author='laharah',
    author_email='laharah22+ca@gmail.com',
    description='Quick and dirty log parser for calibre server',
    packages=['calibre_access'],
    setup_requires=['pytest-runner'],
    install_requires=[
        'geoip2 >= 2.9.0', 
        'appdirs >= 1.4.0',
        'docopt >= 0.5.0',
        'requests',
    ],
    tests_require=[
        'pytest >= 2.8.7',
        'mock >= 1.3.0',
        "httpretty >= 1.0.2",
    ],
    entry_points={
        'console_scripts': [
            'calibre-access = calibre_access.__main__:main'
        ]
    }

)
