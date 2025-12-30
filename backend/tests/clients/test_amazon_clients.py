import pytest
import responses
from unittest.mock import patch, MagicMock
from app.clients.amazon.base_client import AmazonBaseClient
from app.clients.amazon.sp_api_client import SpApiClient
from app.clients.amazon.ads_api_client import AdsApiClient

@pytest.fixture
def mock_settings():
    with patch("app.clients.amazon.base_client.settings") as mock:
        mock.amazon_client_id = "test_client_id"
        mock.amazon_client_secret = "test_secret"
        mock.amazon_refresh_token = "test_refresh_token"
        mock.is_testing = True
        yield mock

@pytest.fixture
def base_client(mock_settings):
    client = AmazonBaseClient()
    # 手动设置 token 以跳过自动刷新
    client.access_token = "test_access_token"
    client.token_expiry = 9999999999
    return client

@responses.activate
def test_refresh_access_token(mock_settings):
    client = AmazonBaseClient(refresh_token="custom_refresh")
    
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "new_token", "expires_in": 3600},
        status=200
    )
    
    token = client._refresh_access_token()
    assert token == "new_token"
    assert client.access_token == "new_token"
    assert "grant_type=refresh_token" in responses.calls[0].request.body

@responses.activate
def test_sp_api_inventory(mock_settings):
    client = SpApiClient()
    client.access_token = "valid_token"
    client.token_expiry = 9999999999
    
    responses.add(
        responses.GET,
        "https://sellingpartnerapi-na.amazon.com/fba/inventory/v1/summaries",
        json={"payload": {"inventorySummaries": []}},
        status=200
    )
    
    resp = client.get_inventory_summary(marketplace_id="US_MARKETPLACE")
    assert "payload" in resp
    assert responses.calls[0].request.headers["x-amz-access-token"] == "valid_token"

@responses.activate
def test_ads_api_campaigns(mock_settings):
    client = AdsApiClient(profile_id="12345")
    client.access_token = "valid_token"
    client.token_expiry = 9999999999
    
    responses.add(
        responses.POST,
        "https://advertising-api.amazon.com/sp/campaigns/list",
        json={"campaigns": [{"campaignId": 1}]},
        status=200
    )
    
    campaigns = client.list_campaigns()
    assert len(campaigns) == 1
    # 验证 Header
    headers = responses.calls[0].request.headers
    assert headers["Amazon-Advertising-API-Scope"] == "12345"
    assert headers["Amazon-Advertising-API-ClientId"] == "test_client_id"
    assert headers["Content-Type"] == "application/vnd.spCampaign.v3+json"

@responses.activate
def test_ads_api_reporting(mock_settings):
    client = AdsApiClient(profile_id="12345")
    client.access_token = "valid_token"
    client.token_expiry = 9999999999
    
    # Mock Request Report
    responses.add(
        responses.POST,
        "https://advertising-api.amazon.com/reporting/reports",
        json={"reportId": "REPORT-123"},
        status=200
    )
    
    # Mock Get Status
    responses.add(
        responses.GET,
        "https://advertising-api.amazon.com/reporting/reports/REPORT-123",
        json={"status": "COMPLETED", "url": "http://download"},
        status=200
    )
    
    report_id = client.request_report("2023-01-01", ["campaignName", "spend"])
    assert report_id == "REPORT-123"
    
    status = client.get_report_status("REPORT-123")
    assert status["status"] == "COMPLETED"

@responses.activate
def test_sp_api_reporting(mock_settings):
    client = SpApiClient()
    client.access_token = "valid_token"
    client.token_expiry = 9999999999
    
    responses.add(
        responses.POST,
        "https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports",
        json={"reportId": "SP-REPORT-123"},
        status=202
    )
    
    report_id = client.create_report(
        report_type="GET_SALES_AND_TRAFFIC_REPORT",
        marketplace_ids=["US"]
    )
    assert report_id == "SP-REPORT-123"


@responses.activate
def test_retry_logic(mock_settings):
    client = AmazonBaseClient()
    client.access_token = "valid_token" 
    client.token_expiry = 9999999999
    
    # 第一次 429，第二次 200
    responses.add(responses.GET, "https://example.com", status=429)
    responses.add(responses.GET, "https://example.com", status=200, json={"ok": True})
    
    with patch("time.sleep") as mock_sleep: # 避免实际等待
        resp = client._make_request("GET", "https://example.com")
        assert resp["ok"] is True
        assert mock_sleep.called
