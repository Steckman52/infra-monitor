import shutil


def test_broken_and_secret_leak_appear_with_correct_shape(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})
    adrs = {a["title"]: a for a in client.get("/api/adrs").json()}
    secret_leak_id = adrs["Secret Leak Decision"]["id"]

    issues = client.get("/api/adr-issues").json()

    parse_failure = next(i for i in issues if i["type"] == "parse_failure")
    assert "broken.md" in parse_failure["path"]
    assert parse_failure["reason"]

    secret_warning = next(i for i in issues if i["type"] == "secret_warning")
    assert "secret-leak.md" in secret_warning["path"]
    assert secret_warning["adr_id"] == secret_leak_id
    assert secret_warning["reason"]


def test_secret_leak_still_appears_normally_in_adr_list(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})

    adrs = client.get("/api/adrs").json()

    assert any(a["title"] == "Secret Leak Decision" for a in adrs)


def test_rescan_after_fixing_broken_md_removes_the_parse_failure(tmp_path, client, fixtures_dir):
    scratch = tmp_path / "adr-repo"
    shutil.copytree(fixtures_dir / "adr-repo", scratch)

    client.post("/api/scan", json={"roots": [str(scratch)]})
    issues_before = client.get("/api/adr-issues").json()
    assert any(i["type"] == "parse_failure" and "broken.md" in i["path"] for i in issues_before)

    broken_path = scratch / "docs" / "adr" / "broken.md"
    original = broken_path.read_text(encoding="utf-8")
    broken_path.write_text("# Now Has A Title\n\n" + original, encoding="utf-8")

    client.post("/api/scan", json={"roots": [str(scratch)]})
    issues_after = client.get("/api/adr-issues").json()
    adrs_after = client.get("/api/adrs").json()

    assert not any(i["type"] == "parse_failure" and "broken.md" in i["path"] for i in issues_after)
    assert any(a["title"] == "Now Has A Title" for a in adrs_after)
