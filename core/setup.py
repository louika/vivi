from setuptools import setup, find_packages

setup(
    name='zeit.push',
    version='1.0.0.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/zeit.push',
    description="Sending push notifications through various providers",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'requests',
        'setuptools',
        'zope.component',
        'zope.interface',
    ],
)
