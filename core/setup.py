from setuptools import setup, find_packages


setup(
    name='vivi.core',
    version='4.13.1.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi core",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'BTrees',
        'Jinja2',
        'Pillow',
        'SilverCity',
        'ZConfig',
        'ZODB',
        'beautifulsoup4',
        'bugsnag',
        'cssselect',
        'cssutils',
        'celery >= 4.0',
        'celery_longterm_scheduler',
        'docutils',
        'docker',
        'elasticsearch >=2.0.0, <3.0.0',
        'fanstatic',
        'fb',
        'feedparser',
        'filemagic',
        'gocept.cache >= 2.1',
        'gocept.fckeditor[fanstatic]>=2.6.4.1-2',
        'gocept.form[formlib]>=0.7.5',
        'gocept.httpserverlayer>=1.4.0.dev0',
        'gocept.jasmine',
        'gocept.jslint>=0.2',
        'gocept.lxml>=0.2.1',
        'gocept.mochikit>=1.4.2.2',
        'gocept.pagelet',
        'gocept.runner>0.5.3',
        'gocept.selenium>=2.4.0',
        'gocept.testing>=1.4.0.dev0',
        'grokcore.component',
        'grokcore.view',
        'guppy',
        'iso8601>=0.1.2',
        'js.backbone',
        'js.cropper',
        'js.handlebars',
        'js.jquery',
        'js.jqueryui',
        'js.mochikit',
        'js.select2',
        'js.underscore',
        'js.vanderlee_colorpicker',
        'lxml>=2.0.2',
        'martian',
        'mock',
        'persistent',
        'plone.testing[zca,zodb]',
        'pypandoc',
        'pyramid_dogpile_cache2',
        'pytest',
        'pytz',
        'requests',
        'requests-mock',
        'redis',
        'repoze.vhm',
        'setuptools',
        'sprout',
        'suds',
        'tblib',
        'transaction',
        'tweepy',
        'urbanairship >= 1.0',
        'webob',
        'werkzeug',
        'xlrd',
        'xml-compare',
        'z3c.celery >= 1.2.0.dev0',
        'z3c.conditionalviews>=1.0b2.dev-r91510',
        'z3c.flashmessage',
        'z3c.menu.simple>=0.5.1',
        'z3c.noop',
        'z3c.traverser',
        'zc.datetimewidget',
        'zc.form',
        'zc.iso8601',
        'zc.queue',
        'zc.relation',
        'zc.resourcelibrary',
        'zc.set',
        'zc.sourcefactory',
        'zc.table',
        'zdaemon',
        'zeit.optivo',
        'zope.annotation',
        'zope.app.authentication',
        'zope.app.applicationcontrol',
        'zope.app.appsetup',
        'zope.app.basicskin',
        'zope.app.broken',
        'zope.app.component>=3.4.0b3',
        'zope.app.container',
        'zope.app.content',
        'zope.app.dependable',
        'zope.app.error',
        'zope.app.exception',
        'zope.app.file',
        'zope.app.form>=3.6.0',
        'zope.app.generations',
        'zope.app.interface',
        'zope.app.http',
        'zope.app.keyreference',
        'zope.app.localpermission',
        'zope.app.locking',
        'zope.app.pagetemplate',
        'zope.app.preference',
        'zope.app.principalannotation',
        'zope.app.publication',
        'zope.app.publisher',
        'zope.app.renderer',
        'zope.app.rotterdam',
        'zope.app.schema',
        'zope.app.security',
        'zope.app.securitypolicy',
        'zope.app.tree',
        'zope.app.testing',
        'zope.app.wsgi',
        'zope.app.zapi',  # undeclared by z3c.menu.simple
        'zope.app.zopeappgenerations',
        'zope.authentication',
        'zope.browser',
        'zope.browserpage',
        'zope.cachedescriptors',
        'zope.configuration',
        'zope.component',
        'zope.container>=3.8.1',
        'zope.copypastemove',
        'zope.deferredimport',  # undeclared by zc.form
        'zope.dottedname',
        'zope.dublincore',
        'zope.error',
        'zope.event',
        'zope.exceptions',
        'zope.file',
        'zope.formlib',
        'zope.i18n>3.4.0',
        'zope.index',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location>=3.4.0b2',
        'zope.login',
        'zope.password',
        'zope.pluggableauth',
        'zope.principalannotation',
        'zope.proxy',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.securitypolicy',
        'zope.sendmail',
        'zope.session',
        'zope.site',
        'zope.testbrowser',
        'zope.testing>=3.8.0',
        'zope.traversing',
        'zope.viewlet',
        'zope.xmlpickle',
    ],
    entry_points={
        'console_scripts': [
            'brightcove-import-playlists = zeit.brightcove.update:import_playlists',
            'dump_references = zeit.cms.relation.migrate:dump_references',
            'load_references = zeit.cms.relation.migrate:load_references',
            'refresh-cache = zeit.connector.invalidator:invalidate_whole_cache',
            'set-properties = zeit.connector.restore:set_props_from_file',
            'search-elastic=zeit.find.cli:search_elastic',
            'update-topiclist=zeit.retresco.connection:update_topiclist',
            'tms-reindex-object=zeit.retresco.update:reindex',
            'facebook-access-token = zeit.push.facebook:create_access_token',
            'ua-payload-doc = zeit.push.urbanairship:print_payload_documentation',
            'vgwort-order-tokens = zeit.vgwort.token:order_tokens',
            'vgwort-report = zeit.vgwort.report:report_new_documents',

            'zopeshell = zeit.cms.application:zope_shell',
        ],
        'paste.app_factory': [
            'main=zeit.cms.application:APPLICATION',
        ],
        'paste.filter_factory': [
            'bugsnag=zeit.cms.application:bugsnag_filter',
        ],
        'fanstatic.libraries': [
            'zeit_addcentral=zeit.addcentral.resources:lib',
            'zeit_campus=zeit.campus.browser.resources:lib',
            'zeit_cmp=zeit.cmp.browser.resources:lib',

            'zeit_cms=zeit.cms.browser.resources:lib_css',
            'zeit_cms_js=zeit.cms.browser.resources:lib_js',
            'zeit_cms_content=zeit.cms.content.browser.resources:lib',
            'zeit_cms_workingcopy=zeit.cms.workingcopy.browser.resources:lib',
            'zeit_cms_tagging=zeit.cms.tagging.browser.resources:lib',
            'zeit_cms_clipboard=zeit.cms.clipboard.browser.resources:lib',

            'zeit_content_article=zeit.content.article.edit'
            '.browser.resources:lib',
            'zeit_content_article_recension=zeit.content.article'
            '.browser.resources:lib',
            'zeit_content_author=zeit.content.author.browser.resources:lib',
            'zeit_content_cp=zeit.content.cp.browser.resources:lib',
            'zeit_content_gallery=zeit.content.gallery.browser.resources:lib',
            'zeit_content_image=zeit.content.image.browser.resources:lib',
            'zeit_content_image_test=zeit.content.image.browser.resources:test_lib',
            'zeit_content_link=zeit.content.link.browser.resources:lib',
            'zeit_content_volume=zeit.content.volume.browser.resources:lib',

            'zeit_edit=zeit.edit.browser.resources:lib_css',
            'zeit_edit_js=zeit.edit.browser.resources:lib_js',
            'zeit_find=zeit.find.browser.resources:lib',
            'zeit_imp=zeit.imp.browser.resources:lib',
            'zeit_newsletter=zeit.newsletter.browser.resources:lib',
            'zeit_push=zeit.push.browser.resources:lib',
            'zeit_seo=zeit.seo.browser.resources:lib',
            'zeit_workflow=zeit.workflow.browser.resources:lib',
            'zeit_wysiwyg=zeit.wysiwyg.browser.resources:lib',

            'zc_table=zeit.cms.browser.resources:zc_table',
            'zc_datetimewidget=zeit.cms.browser.resources:zc_datetimewidget',
        ],
    }
)
