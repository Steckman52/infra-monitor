from src.scanning.normalization import normalize_template


def test_uuid_replaced_as_one_token():
    text = "User 123e4567-e89b-12d3-a456-426614174000 not found"
    assert normalize_template(text) == "User <UUID> not found"


def test_hex_address_replaced():
    assert normalize_template("segfault at 0x1a2b3c") == "segfault at <HEX>"


def test_quoted_string_replaced():
    assert normalize_template('Invalid value "abc123"') == "Invalid value <STR>"


def test_bare_digits_replaced():
    result = normalize_template("Connection refused: db:5432 attempt 3")
    assert result == "Connection refused: db:<NUM> attempt <NUM>"


def test_order_prevents_uuid_fragmentation():
    # If digits were substituted before UUID detection, this would become a
    # mess of separate <NUM> tokens instead of one clean <UUID> token.
    text = "id=123e4567-e89b-12d3-a456-426614174000"
    result = normalize_template(text)
    assert result.count("<UUID>") == 1
    assert "<NUM>" not in result
