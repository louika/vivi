# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'cmscontentiterable.txt',
        'feed.txt',
        'rule.txt',
        'teaser.txt',
        package=zeit.content.cp)
