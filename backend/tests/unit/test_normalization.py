from src.scanning.normalization import normalize_template


def test_uuid_replaced_as_one_token():
    text = "User 123e4567-e89b-12d3-a456-426614174000 not found"
    assert normalize_template(text) == "User <UUID> not found"


def test_hex_address_replaced():
    assert normalize_template("segfault at 0x1a2b3c") == "segfault at <HEX>"


def test_quoted_data_replaced_but_the_quotes_remain():
    # The quotes are kept so the template still reads like the line it came
    # from (`msg="<STR>"` rather than `msg=<STR>`).
    assert normalize_template('Invalid value "abc123"') == 'Invalid value "<STR>"'


def test_a_quoted_human_message_is_not_erased():
    # In most real loggers the message IS the quoted part. Collapsing every
    # quoted run merged unrelated failures into one group, which is what
    # made occurrence_count meaningless.
    distinct = {
        normalize_template('request failed: "no route to host"'),
        normalize_template('request failed: "permission denied"'),
    }
    assert len(distinct) == 2


def test_identifiers_are_normalized_so_repeats_group_together():
    # Request ids, pod names and tenant paths vary per occurrence; without
    # these rules one incident became thousands of single-occurrence rows.
    same = {
        normalize_template(f"[req {rid}] upstream timeout")
        for rid in ("d41d8cd98f00b204e9800998ecf8427e", "a1b2c3d4e5f60718293a4b5c6d7e8f90")
    }
    assert len(same) == 1


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
