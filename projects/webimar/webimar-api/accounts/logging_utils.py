# Safe logging utilities
import json

def safe_log_request_data(request_data, sensitive_fields=None):
    """
    Safely log request data without exposing sensitive information
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'password', 'password1', 'password2', 'old_password', 'new_password',
            'token', 'refresh_token', 'access_token',
            'email_verification_token', 'password_reset_token'
        ]
    
    safe_data = {}
    for key, value in request_data.items():
        if key.lower() in [field.lower() for field in sensitive_fields]:
            safe_data[key] = '***HIDDEN***'
        else:
            safe_data[key] = value
    
    return safe_data

def safe_log_dict(data_dict, sensitive_fields=None):
    """
    Safely log dictionary data without exposing sensitive information
    """
    if isinstance(data_dict, dict):
        return safe_log_request_data(data_dict, sensitive_fields)
    else:
        return data_dict
