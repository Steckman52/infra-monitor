from src.scanning.adr_secrets import check_for_secrets, describe_secret_warning


def test_private_key_header_detected():
    assert check_for_secrets("-----BEGIN RSA PRIVATE KEY-----\nMIIEow...\n") is True


def test_aws_access_key_detected():
    assert check_for_secrets("Our key is AKIAABCDEFGHIJKLMNOP for testing.") is True


def test_generic_credential_assignment_detected():
    assert check_for_secrets("password: SuperSecret123!") is True
    assert check_for_secrets('api_key = "abcd1234efgh5678"') is True


def test_ordinary_prose_not_flagged():
    assert check_for_secrets("We decided to use SQLite for local storage.") is False


def test_describe_secret_warning_matches_each_pattern():
    assert describe_secret_warning("-----BEGIN RSA PRIVATE KEY-----\n...\n") == (
        "Content resembles a private key"
    )
    assert describe_secret_warning("AKIAABCDEFGHIJKLMNOP") == "Content resembles an AWS access key"
    assert describe_secret_warning("password: SuperSecret123!") == (
        "Content resembles a generic credential assignment"
    )


def test_describe_secret_warning_is_none_for_ordinary_prose():
    assert describe_secret_warning("We decided to use SQLite for local storage.") is None
