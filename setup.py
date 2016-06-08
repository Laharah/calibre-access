from setuptools import setup

setup(
    name='calibre-access',
    version='1.0.4',
    url='',
    license='MIT',
    author='laharah',
    author_email='laharah22+ca@gmail.com',
    description='Quick and dirty log parser for calibre server',
    py_modules=['calibre_access', 'utilities'],
    setup_requires=['pytest-runner'],
    install_requires=[
        'pygeoip >= 0.3',
        'appdirs >= 1.4.0',
        'docopt >= 0.5.0',
        'requests',
    ],
    tests_require=[
        'pytest >= 2.8.7',
        'mock >= 1.3.0',
        'httpretty >= 0.8.14',
    ],
    entry_points={
        'console_scripts': [
            'calibre-access = calibre_access:main'
        ]
    }

)
