import setuptools
import distutils.core

setuptools.setup(
    name='brave-history',
    version="1.2.0",
    author='@readwithai',
    long_description_content_type='text/markdown',
    author_email='talwrii@gmail.com',
    description='Search brave history from the command-line',
    license='BSD',
    keywords='brave,history,cli,command-line',
    url='',
    install_requires=["pytz", "tzlocal"],
    packages=["brave_history"],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['brave-history=brave_history.main:main']
    }
)
