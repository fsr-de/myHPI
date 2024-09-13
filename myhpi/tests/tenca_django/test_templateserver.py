import urllib.error
import urllib.parse
import urllib.request

from django.test import TestCase


class TemplateRequestTest(TestCase):
    """Access via HTTP as given in `settings.TEMPLATE_SERVER_ADDRESS`"""

    def url(self, path):
        return "{}/{}".format(tenca.settings.TEMPLATE_SERVER_ADDRESS, path)

    def open(self, path, **kwargs):
        fragments = urllib.parse.urlencode(kwargs)
        if fragments:
            fragments = "?" + fragments
        urllib.request.urlopen(self.url(path) + fragments)

    def read(self, url):
        return urllib.request.urlopen(url).read().decode("utf-8")

    def testNonExistentTemplateGives404(self):
        assert self.client.get("/lists/templates/no_such_template").status_code == 404

    # def testAllTemplates(self):
    # 	template_keys = (
    # 		'invite_link',
    # 		'fqdn_listname',
    # 		'action_link',
    # 		'action_abuse_link',
    # 		'web_ui',
    # 	)
    # 	template_args = {k: 'Placeholder' for k in template_keys}
    # 	for template_name in tenca.templates.templates_dict:
    # 		self.assertEqual(
    # 			tenca.templates.substitute(template_name, **template_args),
    # 			self.read(tenca.templates.http_substitute_url(template_name, **template_args))
    # 		)
