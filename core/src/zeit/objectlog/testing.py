import os
import persistent
import re
import zeit.cms.testing
import zope.app.testing.functional


ObjectLogLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ObjectLogLayer', allow_teardown=True)


FORMATTED_DATE_REGEX = re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d')
checker = zeit.cms.testing.OutputChecker([
    (FORMATTED_DATE_REGEX, '<formatted date>')])


class Content(persistent.Persistent):
    pass
