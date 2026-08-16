import jwt
import datetime
from django.conf import settings

def generate_jwt(user):
    """
    Generates a local JWT token for the authenticated user.
    """
    payload = {
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        'role': 'Administrator' if user.is_superuser else 'Creator',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt(token):
    """
    Decodes and verifies the local JWT token.
    Returns the payload if valid, otherwise raises an exception.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')
