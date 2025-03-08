"""
General utilities for the MPESA functions
"""

from __future__ import print_function
from .exceptions import MpesaConfigurationException, IllegalPhoneNumberException, MpesaConnectionError, MpesaError
from tmapp.models import AccessToken
import requests
from django.utils import timezone
from decouple import config, UndefinedValueError
import os
from requests import Response
from django.conf import settings
import base64
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from typing import Optional


class MpesaResponse(Response):
	request_id: str = ''
	response_code: str = ''
	response_description: str = ''
	customer_message: str = ''
	conversation_id: str = ''
	originator_conversation_id: str = ''
	error_code: str = ''
	error_message: str = ''
	merchant_request_id: str = ''
	checkout_request_id: str = ''


def mpesa_response(r: requests.Response) -> MpesaResponse:
	"""
	Create MpesaResponse object from requests.Response object

	Arguments:
		r (requests.Response) -- The response to convert
	"""
	r.__class__ = MpesaResponse
	json_response = r.json()
	r.request_id = json_response.get('requestId', '')
	r.response_code = json_response.get('ResponseCode', '')
	r.response_description = json_response.get('ResponseDescription', '')
	r.customer_message = json_response.get('CustomerMessage', '')
	r.conversation_id = json_response.get('ConversationID', '')
	r.originator_conversation_id = json_response.get('OriginatorConversationID', '')
	r.error_code = json_response.get('errorCode', '')
	r.error_message = json_response.get('errorMessage', '')
	r.merchant_request_id = json_response.get('MerchantRequestID', '')
	r.checkout_request_id = json_response.get('CheckoutRequestID', '')
	return r


def mpesa_config(key: str) -> str:
	"""
	Get Mpesa configuration variable with the matching key

	Arguments:
		key (str) -- The configuration key

	Returns:
		str: Mpesa configuration variable with the matching key

	Raises:
		MpesaConfigurationException: Key not found
	"""
	value = getattr(settings, key, None)
	if value is None:
		try:
			value = config(key)
		except UndefinedValueError:
			raise MpesaConfigurationException(f'Mpesa environment not configured properly - {key} not found')
	return value


def api_base_url() -> str:
	"""
	Gets the base URL for making API calls

	Returns:
		str: The base URL depending on development environment (sandbox or production)

	Raises:
		MpesaConfigurationException: Environment not sandbox or production
	"""
	mpesa_environment = mpesa_config('MPESA_ENVIRONMENT')

	if mpesa_environment == 'development':
		return 'https://darajasimulator.azurewebsites.net/'
	elif mpesa_environment == 'sandbox':
		return 'https://sandbox.safaricom.co.ke/'
	elif mpesa_environment == 'production':
		return 'https://api.safaricom.co.ke/'
	else:
		raise MpesaConfigurationException('Mpesa environment not configured properly - MPESA_ENVIRONMENT should be sandbox or production')


def generate_access_token_request(consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None) -> requests.Response:
	"""
	Make a call to OAuth API to generate access token

	Arguments:
		consumer_key (str) -- (Optional) The Consumer Key to use
		consumer_secret (str) -- (Optional) The Consumer Secret to use

	Returns:
		requests.Response: Response object with the response details

	Raises:
		MpesaConnectionError: Connection error
	"""
	url = api_base_url() + 'oauth/v1/generate?grant_type=client_credentials'
	consumer_key = consumer_key or mpesa_config('MPESA_CONSUMER_KEY')
	consumer_secret = consumer_secret or mpesa_config('MPESA_CONSUMER_SECRET')

	try:
		r = requests.get(url, auth=(consumer_key, consumer_secret))
		r.raise_for_status()
	except requests.exceptions.ConnectionError:
		raise MpesaConnectionError('Connection failed')
	except requests.exceptions.RequestException as ex:
		raise MpesaError(f'Error generating access token: {ex}')

	return r


def generate_access_token() -> AccessToken:
	"""
	Parse generated OAuth access token, then updates database access token value

	Returns:
		AccessToken: The AccessToken object from the database

	Raises:
		MpesaError: Error generating access token
	"""
	r = generate_access_token_request()
	if r.status_code != 200:
		r = generate_access_token_request()
		if r.status_code != 200:
			raise MpesaError('Unable to generate access token')

	token = r.json().get('access_token')
	if not token:
		raise MpesaError('Access token not found in response')

	AccessToken.objects.all().delete()
	access_token = AccessToken.objects.create(token=token)

	return access_token


def mpesa_access_token() -> str:
	"""
	Generate access token if the current one has expired or if token is non-existent
	Otherwise return existing access token

	Returns:
		str: A valid access token
	"""
	access_token = AccessToken.objects.first()
	if not access_token:
		access_token = generate_access_token()
	else:
		delta = timezone.now() - access_token.created_at
		if delta.total_seconds() // 60 > 50:
			access_token = generate_access_token()

	return access_token.token


def format_phone_number(phone_number: str) -> str:
	"""
	Format phone number into the format 2547XXXXXXXX

	Arguments:
		phone_number (str) -- The phone number to format

	Raises:
		IllegalPhoneNumberException: If phone number is too short
	"""
	if len(phone_number) < 9:
		raise IllegalPhoneNumberException('Phone number too short')
	return '254' + phone_number[-9:]


def encrypt_security_credential(credential: str) -> str:
	"""
	Generate an encrypted security credential from a plaintext value

	Arguments:
		credential (str) -- The plaintext credential display
	"""
	mpesa_environment = mpesa_config('MPESA_ENVIRONMENT')

	if mpesa_environment in ('development', 'sandbox', 'production'):
		certificate_name = f'{mpesa_environment}.cer'
	else:
		raise MpesaConfigurationException('Mpesa environment not configured properly - MPESA_ENVIRONMENT should be sandbox or production')

	certificate_path = os.path.join(settings.BASE_DIR, 'certs', certificate_name)
	return encrypt_rsa(certificate_path, credential)


def encrypt_rsa(certificate_path: str, input: str) -> str:
	"""
	Encrypt input using RSA encryption with the provided certificate

	Arguments:
		certificate_path (str) -- The path to the certificate file
		input (str) -- The input string to encrypt

	Returns:
		str: The encrypted string
	"""
	message = input.encode('ascii')
	with open(certificate_path, "rb") as cert_file:
		cert = x509.load_pem_x509_certificate(cert_file.read())
		encrypted = cert.public_key().encrypt(message, PKCS1v15())
		output = base64.b64encode(encrypted).decode('ascii')

	return output
