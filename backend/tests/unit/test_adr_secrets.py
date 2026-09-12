from src.scanning.adr_secrets import check_for_secrets


def test_private_key_header_detected():
    assert check_for_secrets("-----BEGIN RSA PRIVATE KEY-----\nMIIEow...\n") is True


def test_aws_access_key_detected():
    assert check_for_secrets("Our key is AKIAABCDEFGHIJKLMNOP for testing.") is True


def test_generic_credential_assignment_detected():
    assert check_for_secrets("password: SuperSecret123!") is True
    assert check_for_secrets('api_key = "abcd1234efgh5678"') is True


def test_ordinary_prose_not_flagged():
    assert check_for_secrets("We decided to use SQLite for local storage.") is False
