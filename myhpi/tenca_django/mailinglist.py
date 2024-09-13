from django.conf import settings
from django.urls import reverse

from . import exceptions, templates

import base64
import hashlib
import random
import string
import urllib.parse
import urllib.error

import mailmanclient


class MailingList(object):

	"""A decorator for mailmanclient.restobjects.mailinglist.MailingList"""

	# Can be extended by settings.LIST_DEFAULT_SETTINGS
	# In case of conflicting entries, settings wins.
	SHARED_LIST_DEFAULT_SETTINGS = {
		'advertised': False,
		'default_member_action': 'accept',
		'default_nonmember_action': 'accept',
		'send_welcome_message': False,
		# send_goodbye_message: False (see __init__)
	}

	# Maps Mailman Template names to Tenca Template Names
	TEMPLATE_MAPPINGS = {
		'list:member:regular:footer': 'mail_footer',
		'list:user:action:subscribe': 'subscription_message',
		'list:user:action:unsubscribe': 'unsubscription_message',
		'list:user:notice:welcome': 'creation_message',
		'list:user:notice:rejected': 'rejected_message',
	}

	FOOTER_TEMPLATE_NAME = 'list:member:regular:footer'

	def __init__(self, connection, list, hash_id):
		self.conn = connection
		self.list = list
		self.hash_id = hash_id
		if settings.DISABLE_GOODBYE_MESSAGES:
			# Note: Option not present for mailman < 3.3.3
			self.SHARED_LIST_DEFAULT_SETTINGS['send_goodbye_message'] = False

	def __repr__(self):
		return "<{} '{}'>".format(type(self).__name__, str(self.fqdn_listname))

	def _raise_nomember(self, email):
		raise exceptions.NoMemberException('{} is not a member address of {}'.format(email, self.fqdn_listname))

	def _raw_get_member(self, email):
		try:
			member = self.list.get_member(email)
		except ValueError:
			self._raise_nomember(email)
		else:
			return member

	def add_member_silently(self, email):
		"""Subscribe an email address to a mailing list, with no verification or notification send"""
		self.list.subscribe(email, pre_verified=True, pre_confirmed=True, send_welcome_message=False)

	def add_member(self, email, send_welcome_message=False, _on_retry=False):
		"""Subscribes a user and sends them a confirmation mail

		Returns the authentication token for that subscription.
		"""
		try:
			return self.list.subscribe(email, send_welcome_message=send_welcome_message)["token"]
		except urllib.error.HTTPError as e:
			 # Already pending subscriptions are retried
			if e.status == 409 and not _on_retry and settings.RETRY_CANCELS_PENDING_SUBSCRIPTION:
				try:
					token = next(t for t, e in self.pending_subscriptions().items() if e == email)
				except StopIteration: # pragma: no cover
					# This only happens in crazy race-conditions, if the request
					# was accepted/canceled between with subscribe and lookup.
					# If accepted, we expect again an error to notify.
					# If canceled, the expected action is to correctly try again
					pass
				else:
					self.cancel_pending_subscription(token)
				return self.add_member(email, send_welcome_message, _on_retry=True)
			else:
				raise e

	def toggle_membership(self, email):
		"""Adds member if not present and removes if already member.
		
		This is useful from interfaces where you don't want to hint attackers
		the current membership status of others.

		Returns a tuple of (status, token), where status is True if the user was newly
		added and False if it was removed.
		"""
		if self.is_member(email):
			return False, self.remove_member(email)
		else:
			return True, self.add_member(email)


	def configure_list(self):
		self.list.settings.update(self.SHARED_LIST_DEFAULT_SETTINGS)
		self.list.settings.update(settings.LIST_DEFAULT_SETTINGS)
		self.list.settings['subject_prefix'] = '[{}] '.format(self.list.settings['list_name'].lower())
		self.list.settings.save()

	def configure_templates(self):
		for mailman_template_name, tenca_template_name in self.TEMPLATE_MAPPINGS.items():
			self.configure_single_template(mailman_template_name, tenca_template_name)

	def configure_single_template(self, mailman_template_name, tenca_template_name):
		template_args = dict(
			fqdn_listname=self.fqdn_listname,
			action_link=self.build_action_link('$token'),
			action_abuse_link=self.build_action_abuse_link('$token'),
			invite_link=self.build_invite_link(),
			web_ui=urllib.parse.urljoin(settings.GET_SITE_URL(), reverse("tenca_dashboard"))
		)
		self.list.set_template(mailman_template_name, urllib.parse.urljoin(settings.SITE_URL, reverse("tenca_django:mailman_template", kwargs={'template_name': tenca_template_name})))

	def pending_subscriptions(self, request_type='subscription'):
		"""As of mailman<3.3.3 no unsubscriptions are delivered via REST.
		In case you updated core (but use an older version of mailmanclient),
		you can set `settings.DISABLE_GOODBYE_MESSAGES` to True to enable
		proper removal.
		"""
		if settings.DISABLE_GOODBYE_MESSAGES:
			path = 'lists/{}/requests'.format(self.fqdn_listname)
			get_params = {
				'token_owner': 'subscriber',
				'request_type': request_type
			}
			response, answer = self.conn.rest_call('{}?{}'.format(path, urllib.parse.urlencode(get_params), None, 'GET'))
			if 'entries' not in answer:
				return {}
			else:
				return {r['token']: r['email'] for r in answer['entries']}
		else:
			return {r['token']: r['email'] for r in self.list.get_requests(token_owner='subscriber')}

	def _wrap_subscription_exception(self, func, token):
		try:
			func()
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e, exceptions.NoSuchRequestException, self, token)

	def confirm_subscription(self, token):
		self._wrap_subscription_exception(
			lambda: self.list.accept_request(token),
			token)

	def cancel_pending_subscription(self, token):
		self._wrap_subscription_exception(
			lambda: self.list.moderate_request(token, 'discard'),
			token)

	def promote_to_owner(self, email):
		member = self._raw_get_member(email)
		self.list.add_owner(member.address)

	def is_owner(self, email):
		return self.list.is_owner(email)

	def is_member(self, email):
		return self.list.is_member(email)

	def demote_from_owner(self, email):
		owners = self.list.owners
		if not self.list.is_owner(email):
			raise exceptions.NoMemberException('{} is not an owner address of {}'.format(email, self.fqdn_listname))
		# FIXME: No lock here. Potential race condition
		if len(self.list.owners) == 1:
			raise exceptions.LastOwnerException(email)
		self.list.remove_owner(email)

	def _is_a_blocked_action(self, moderation_action):
		return moderation_action not in [None, '', 'accept']

	def is_blocked(self, email):
		member = self._raw_get_member(email)
		return self._is_a_blocked_action(member.moderation_action)

	def set_blocked(self, email, is_blocked):
		member = self._raw_get_member(email)
		member.moderation_action = settings.BLOCKED_MEMBER_ACTION if is_blocked else ''
		member.save()
	
	def _patched_unsubscribe(self, email, **kwargs):
		# As of mailmanclient=3.3.2, no confirmation for REST-based unsubscribe is send
		# Here, we manually issue a REST call.
		# Remove this function, as soon as this gets fixed in upstream
		data = {k: v for k, v in kwargs.items() if v is not None}
		try:
			path = 'lists/{}/member/{}'.format(self.list_id, email)
			response, answer = self.conn.rest_call(path, data, 'DELETE')
			# Possible responses and answers
			#   HTTP 202: json, i.e. with token
			#   HTTP 204: None-answer, i.e. no confirmation requested
			if response.status_code == 202:
				return answer["token"]
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e)
			self._raise_nomember(email)
			
	def remove_member_silently(self, email):
		"""Remove member with all roles, no confirmation required. Fails if last owner.

		Attention: As of mailman<3.3.3, the `send_goodbye_message` attribute of a list
		is not exposed using the REST API. Thus, this function is never silent and
		will always send a final notification when a member is successfully removed.

		If you have updated core, set `settings.DISABLE_GOODBYE_MESSAGES` to true.
		"""
		return self.remove_member(email, pre_confirmed=None)

	def remove_member(self, email, pre_confirmed=False):
		"""Remove member with all roles. Fails if last owner."""
		if self.list.is_owner(email):
			self.demote_from_owner(email)
		return self._patched_unsubscribe(email, pre_confirmed=pre_confirmed)

	def _raw_get_roster(self, roster):
		path = 'lists/{}/roster/{}'.format(self.list_id, roster)
		try:
			response, answer = self.conn.rest_call(path, method='GET')
			return answer.get('entries', [])
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e)
			return []

	def get_roster(self):
		memberships = {
			e['email']: (False, self._is_a_blocked_action(e.get('moderation_action'))) for e in self._raw_get_roster('member')
		}
		memberships.update({
			# We cannot trust the 'moderation_action' field of owners.
			# But the member-status is evaluated when receiving an email from this address.
			email: (True, memberships[email][1]) for email in (e['email'] for e in self._raw_get_roster('owner')) if email in memberships
		})
		# if you prefer all owners first (jumping in the view if changed)
		# return sorted(memberships.items(), key=lambda t: (not t[1][0], t[0])) # False < True
		return sorted(memberships.items())

	def inject_message(self, sender_address, subject, message, other_headers=None):
		other_headers = other_headers or {}
		other_headers_str = "\n".join(["%s: %s" % (k.capitalize(), str(v)) for k, v in other_headers.items()])
		if other_headers_str:
			other_headers_str += '\n'
		raw_text = ("From: {}\n"
		"To: {}\n"
		"Subject: {}\n" + other_headers_str +
		"\n"
		"{}").format(sender_address, self.fqdn_listname, subject, message)
		in_queue = self.conn.client.queues['in']
		in_queue.inject(self.list_id, raw_text)

	def propose_hash_id(self, round=0):
		"""Returns a hash, that can be used to identify this list
		
		In the unlikely case this clashes with existing ids, the round
		parameter can be used to generate a new one.

		The ids are actually predictable for a given (secret) salt.
		This has two implications:
			1. If that salt leaks, anyone can guess any invite link by listnames.
			2. Re-creating a list with the same name will result in the same
			   invite link (unless, there is a very unlike hash-collision).
			   Helpfull, if someone accidentally deletes a list and allows
			   for non-persistent caches.

		I actually like the second aspect, but if you don't or #1 worries you
		too much, consider changing `settings.USE_RANDOM_LIST_HASH`	to True.
		"""
		if settings.USE_RANDOM_LIST_HASH:
			LEN = 32
			ALPHA_NUM = string.ascii_letters + string.digits
			return "".join(random.choice(ALPHA_NUM) for _ in range(LEN))
		else:
			BAD_B64_CHARS = '+/='

			components = (settings.LIST_HASH_ID_SALT, round, self.list_id)
			hashobj = hashlib.sha256()
			hashobj.update('$'.join(map(str, components)).encode('ascii'))
			b64 = base64.b64encode(hashobj.digest()).decode('ascii')
			return b64.translate({ord(c): None for c in BAD_B64_CHARS})

	def build_invite_link(self):
		return urllib.parse.urljoin(settings.SITE_URL, self.hash_id)

	def build_action_link(self, token, action='confirm'):
		return urllib.parse.urljoin(settings.SITE_URL, '/'.join((action, self.list_id, token)))

	def build_action_abuse_link(self, token):
		return self.build_action_link(token, 'report')

	############################################################################
	## Options

	@property
	def notsubscribed_allowed_to_post(self):
		return self.list.settings['default_nonmember_action'] == 'accept'

	@notsubscribed_allowed_to_post.setter
	def notsubscribed_allowed_to_post(self, is_allowed):
		if is_allowed:
			self.list.settings['default_nonmember_action'] = 'accept'
		else:
			self.list.settings['default_nonmember_action'] = settings.DISABLED_NON_MEMBER_ACTION
		self.list.settings.save()

	@property
	def replies_addressed_to_list(self):
		return self.list.settings['reply_goes_to_list'] != 'no_munging'

	@replies_addressed_to_list.setter
	def replies_addressed_to_list(self, is_setting_reply_to):
		# Note: eemaill does not apply this setting if the sender already
		# sends a 'REPLY-TO'. But we take the Mailman approach and add both
		if is_setting_reply_to:
			# Note: I would like to use 'point_to_list', but this uses the
			# description as readable name, leaking MailmanDescriptionHashStorage data
			# This works, but is not nice.
			self.list.settings['reply_to_address'] = self.fqdn_listname
			self.list.settings['reply_goes_to_list'] = 'explicit_header'
		else:
			self.list.settings['reply_goes_to_list'] = 'no_munging'
		self.list.settings.save()

	@property
	def footer_has_subscribe_link(self):
		footer_template = next(
			(t for t in self.list.templates if t.name == self.FOOTER_TEMPLATE_NAME),
			None,
		)
		return footer_template and footer_template.uri != 'None'

	@footer_has_subscribe_link.setter
	def footer_has_subscribe_link(self, has_link):
		if has_link:
			self.configure_single_template(
				self.FOOTER_TEMPLATE_NAME,
				self.TEMPLATE_MAPPINGS[self.FOOTER_TEMPLATE_NAME],
			)
		else:
			self.list.set_template(self.FOOTER_TEMPLATE_NAME, None)

	############################################################################

	@property
	def fqdn_listname(self):
		return self.list.fqdn_listname

	@property
	def list_id(self):
		return self.list.list_id
