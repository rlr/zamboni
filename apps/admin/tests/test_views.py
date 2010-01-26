import test_utils

from nose.tools import eq_

from caching import cache

from amo.urlresolvers import reverse
from addons.models import Addon
from files.models import Approval
from versions.models import Version


class TestFlagged(test_utils.TestCase):
    fixtures = ['admin/tests/flagged']

    def setUp(self):
        self.client.login(username='jbalogh@mozilla.com', password='password')
        cache.clear()

    def test_get(self):
        url = reverse('admin.flagged')
        response = self.client.get(url, follow=True)

        addons = dict((a.id, a) for a in response.context['addons'])
        eq_(len(addons), 3)

        # 1. an addon should have latest version and approval attached
        addon = Addon.objects.get(id=1)
        eq_(addons[1], addon)
        eq_(addons[1].version, Version.objects.filter(addon=addon).latest())
        eq_(addons[1].approval, Approval.objects.filter(addon=addon).latest())

        # 2. missing approval is ok
        addon = Addon.objects.get(id=2)
        eq_(addons[2], addon)
        eq_(addons[2].version, Version.objects.filter(addon=addon).latest())
        assert not hasattr(addons[2], 'approval')

        # 3. missing approval is ok
        addon = Addon.objects.get(id=3)
        eq_(addons[3], addon)
        eq_(addons[3].approval, Approval.objects.filter(addon=addon).latest())
        assert not hasattr(addons[3], 'version')

    def test_post(self):
        # Do a get first so the query is cached.
        url = reverse('admin.flagged')
        self.client.get(url, follow=True)

        response = self.client.post(url, {'addon_id': ['1', '2']}, follow=True)
        self.assertRedirects(response, url)

        assert not Addon.objects.get(id=1).adminreview
        assert not Addon.objects.get(id=2).adminreview

        addons = response.context['addons']
        eq_(len(addons), 1)
        eq_(addons[0], Addon.objects.get(id=3))