from setuptools import setup, find_packages


setup(
    name='zeit.content.image',
    version='2.21.0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Image, ImageGroup",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'Pillow',
        'ZODB',
        'filemagic',
        'gocept.form',
        'gocept.httpserverlayer',
        'gocept.jasmine',
        'gocept.selenium',
        'grokcore.component',
        'js.backbone',
        'js.cropper',
        'js.handlebars',
        'lxml',
        'persistent',
        'pytz',
        'requests',
        'setuptools',
        'transaction',
        'z3c.conditionalviews',
        'z3c.traverser',
        'zc.form',
        'zc.sourcefactory',
        'zc.table',
        'zeit.cms >= 3.0.dev0',
        'zeit.connector>=2.4.0.dev0',
        'zeit.edit>=2.11.3.dev0',
        'zeit.wysiwyg',
        'zope.app.appsetup',
        'zope.app.container',
        'zope.app.file',
        'zope.app.generations',
        'zope.app.pagetemplate',
        'zope.browserpage',
        'zope.cachedescriptors',
        'zope.component',
        'zope.file',
        'zope.formlib',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.testbrowser',
        'zope.testing',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_content_image=zeit.content.image.browser.resources:lib',
            'zeit_content_image_test=zeit.content.image.browser.resources:test_lib',
        ],
    },
)
