"""
See
https://github.com/NHSDigital/pytest-nhsd-apim/blob/main/tests/test_examples.py
for more ideas on how to test the authorization of your API.
"""
import requests
import pytest
from os import getenv


@pytest.mark.smoketest
def test_ping(nhsd_apim_proxy_url):
    resp = requests.get(f"{nhsd_apim_proxy_url}/_ping")
    assert resp.status_code == 200


@pytest.mark.smoketest
def test_wait_for_ping(nhsd_apim_proxy_url):
    retries = 0
    resp = requests.get(f"{nhsd_apim_proxy_url}/_ping")
    deployed_commitId = resp.json().get("commitId")

    while (deployed_commitId != getenv('SOURCE_COMMIT_ID')
            and retries <= 30
            and resp.status_code == 200):
        resp = requests.get(f"{nhsd_apim_proxy_url}/_ping")
        deployed_commitId = resp.json().get("commitId")
        retries += 1

    if resp.status_code != 200:
        pytest.fail(f"Status code {resp.status_code}, expecting 200")
    elif retries >= 30:
        pytest.fail("Timeout Error - max retries")

    assert deployed_commitId == getenv('SOURCE_COMMIT_ID')


@pytest.mark.smoketest
def test_status(nhsd_apim_proxy_url, status_endpoint_auth_headers):
    old_header = status_endpoint_auth_headers["apikey"]
    status_endpoint_auth_headers = {"X-Api-Key": old_header}

    resp = requests.get(
        f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers
    )
    assert resp.status_code == 200
    # Make some additional assertions about your status response here!


@pytest.mark.smoketest
def test_wait_for_status(nhsd_apim_proxy_url, status_endpoint_auth_headers):
    old_header = status_endpoint_auth_headers["apikey"]
    status_endpoint_auth_headers = {"X-Api-Key": old_header}
    retries = 0
    resp = requests.get(f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers)
    deployed_commitId = resp.json().get("commitId")

    while (deployed_commitId != getenv('SOURCE_COMMIT_ID')
            and retries <= 30
            and resp.status_code == 200
            and resp.json().get("version")):
        resp = requests.get(f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers)
        deployed_commitId = resp.json().get("commitId")
        retries += 1

    if resp.status_code != 200:
        pytest.fail(f"Status code {resp.status_code}, expecting 200")
    elif retries >= 30:
        pytest.fail("Timeout Error - max retries")
    elif not resp.json().get("version"):
        pytest.fail("version not found")

    assert deployed_commitId == getenv('SOURCE_COMMIT_ID')


# Use the pytest.mark.nhsd_apim_authorization fixture automate the
# hassle of getting valid access tokens and/or API keys to access your
# API.
@pytest.mark.nhsd_apim_authorization({"access": "application", "level": "level0"})
def test_app_level0_access(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """
    Test you have correctly configured an endpoint for application-level0 access.
    """
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAA", nhsd_apim_auth_headers)
    resp = requests.get(nhsd_apim_proxy_url + "/test-auth/app/level0")
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBB", resp)
    assert resp.status_code == 401  # unauthorized

    resp = requests.get(
        nhsd_apim_proxy_url + "/test-auth/app/level0", headers=nhsd_apim_auth_headers
    )
    print("CCCCCCCCCCCCCCCCCCCCCCCCCCC", resp)
    assert resp.status_code == 200  # authorized
