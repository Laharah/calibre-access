from setuptools import setup

setup(
    name='calibre-access',
    version='0.23.1',
    url='',
    license='MIT',
    author='laharah',
    author_email='laharah22+ca@gmail.com',
    description='Quick and dirty log parser for calibre server',
    py_modules=['calibre_access'],
    install_requires=[
        'pygeoip >= 0.3',
        'appdirs >= 1.4.0',
        'docopt >= 0.5.0'
    ],
    entry_points={
        'console_scripts': [
            'calibre-access = calibre_access:main'
        ]
    }

)
