class TencaException(Exception):
	pass

class NoMemberException(TencaException):
	pass

class NoSuchRequestException(TencaException):

	def __init__(self, list, token):
		super().__init__('No pending request {} on list <{}>.'.format(token, list.fqdn_listname))

class LastOwnerException(TencaException):
	
	def __init__(self, email):
		super().__init__('User <{}> is the last owner. Cannot remove.'.format(email))

def map_http_404(http_error, new_error_class=None, *args, **kwargs):
	"""Maps an `urllib.error.HTTPError` with code 404 to more tangible tenca exception.
	
	The (keyword-)arguments are passed on to the constructor of new_error_class.

	HTTPErrors with different status code than 404 will be re-raised.
	If new_error_class is None, the function will just pass over an HTTP 404,
	so you can e.g. return default values instead but still re-raise other HTTP
	errors.
	"""
	if http_error.code == 404:
		if new_error_class is not None:
			raise new_error_class(*args, **kwargs)
	else:
		raise http_error