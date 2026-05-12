import re

def validate_email(email: str) -> str | None:
    if not email.strip():
        return "Email cannot be empty."
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email.strip()):
        return "Enter a valid email address."
    return None

def validate_password(password: str) -> str | None:
    if not password:
        return "Password cannot be empty."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least 1 uppercase letter."
    if len(re.findall(r'[a-zA-Z]', password)) < 2:
        return "Password must contain at least 2 letters."
    if not re.search(r'[-!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least 1 special character."
    return None

def validate_name(value: str, field_label: str) -> str | None:
    if not value.strip():
        return f"{field_label} cannot be empty."
    if len(value.strip()) < 2:
        return f"{field_label} must be at least 2 characters."
    if not re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s\-]+$', value.strip()):
        return f"{field_label} can only contain letters."
    return None

def validate_phone(phone: str) -> str | None:
    if not phone.strip():
        return "Phone number cannot be empty."
    # Accepts formats: +905551234567 / 05551234567 / 5551234567
    if not re.match(r'^(\+90|0)?[5][0-9]{9}$', phone.strip()):
        return "Enter a valid Turkish phone number."
    return None