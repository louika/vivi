from setuptools import setup, find_packages

setup(
    name='zeit.content.article',
    version='3.21.9.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Article",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'gocept.filestore',
        'gocept.form[formlib]>=0.7.2',
        'gocept.httpserverlayer',
        'gocept.jslint>=0.2',
        'gocept.lxml>=0.2.1',
        'gocept.mochikit>=1.3.2',
        'gocept.pagelet',
        'gocept.selenium>=2.4.0',
        'grokcore.component>=2.2',
        'iso8601>=0.1.2',
        'lovely.remotetask',
        'lxml>=2.0.2',
        'mock',
        'rwproperty>=1.0',
        'setuptools',
        'sprout',
        'z3c.conditionalviews',
        'z3c.etestbrowser',
        'z3c.flashmessage',
        'z3c.menu.simple>=0.5.1',
        'z3c.traverser',
        'zc.datetimewidget',
        'zc.form',
        'zc.recipe.egg>=1.1.0dev-r84019',
        'zc.relation',
        'zc.resourcelibrary',
        'zc.set',
        'zc.sourcefactory',
        'zc.table',
        'zdaemon',
        'zeit.cms>=2.94.0.dev0',
        'zeit.connector>=2.3.1.dev0',
        'zeit.content.author>=2.7.1.dev0',
        'zeit.content.cp>=0.33.0',
        'zeit.content.image>=2.13.6.dev0',
        'zeit.content.infobox',
        'zeit.content.gallery',
        'zeit.content.portraitbox',
        'zeit.content.text>=2.0.2.dev0',
        'zeit.content.video',
        'zeit.content.volume>=1.1.0.dev0',
        'zeit.edit>=2.14.0.dev0',
        'zeit.objectlog>=0.2',
        'zeit.push>=1.19.0.dev0',
        'zeit.wysiwyg>=1.41.0dev',
        'zope.app.appsetup',
        'zope.app.component>=3.4.0b3',
        'zope.app.container',
        'zope.app.generations',
        'zope.app.zopeappgenerations',
        'zope.copypastemove',
        'zope.i18n>3.4.0',
        'zope.index',
        'zope.location>=3.4.0b2',
    ],
    entry_points={
        'console_scripts': [
            'run-cds-import=zeit.content.article.cds:import_main',
        ],
        'fanstatic.libraries': [
            'zeit_content_article=zeit.content.article.edit'
            '.browser.resources:lib',
            'zeit_content_article_recension=zeit.content.article'
            '.browser.resources:lib',
        ],
    },
)
