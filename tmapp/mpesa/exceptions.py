"""
Exceptions raised during usage of the MPESa API
"""

class MpesaError(Exception):
	"""
	Raised for a general error regarding the library.
	"""
	pass

class IllegalPhoneNumberException(MpesaError):
	"""
	Raised when the phone number is in an illegal format.
	"""
	pass

class MpesaConnectionError(MpesaError):
	"""
	Raised when there is a connection error.
	"""
	pass

class MpesaConfigurationException(MpesaError):
	"""
	Raised when Mpesa environment variables are not configured properly.
	"""
	pass

class MpesaInvalidParameterException(MpesaError):
	"""
	Raised when an invalid parameter is passed in a function call.
	"""
	pass
