import time
import gzip
import json
import logging
from typing import Any, Dict, Generator, Optional
from datetime import date
import httpx
from pydantic import Field

from jeff_data_core.connectors.base import BaseConnector, ConnectorConfig

logger = logging.getLogger(__name__)

class AmazonAdsConfig(ConnectorConfig):
    """Configuration for Amazon Ads Connector"""
    client_id: str
    client_secret: str
    refresh_token: str
    profile_id: str
    region: str = "NA"  # NA, EU, FE
    
    # API Endpoints based on region
    @property
    def base_url(self) -> str:
        if self.region == "EU":
            return "https://advertising-api-eu.amazon.com"
        elif self.region == "FE":
            return "https://advertising-api-fe.amazon.com"
        return "https://advertising-api.amazon.com"
        
    @property
    def token_url(self) -> str:
        return "https://api.amazon.com/auth/o2/token"

class AmazonAdsConnector(BaseConnector):
    """
    Connector for Amazon Ads API.
    Focuses on fetching Search Term Reports for Sponsored Products.
    """
    
    def __init__(self, config: AmazonAdsConfig):
        super().__init__(config)
        self.config: AmazonAdsConfig = config
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self.client = httpx.Client(timeout=self.config.timeout)

    @property
    def source_type(self) -> str:
        return "amazon_ads"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token."""
        if not self._access_token or time.time() > self._token_expires_at:
            self._refresh_access_token()
            
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Amazon-Advertising-API-ClientId": self.config.client_id,
            "Amazon-Advertising-API-Scope": self.config.profile_id,
            "Content-Type": "application/json"
        }

    def _refresh_access_token(self):
        """Exchanges refresh token for a new access token."""
        logger.info("Refreshing Amazon Ads access token...")
        response = self.client.post(
            self.config.token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.config.refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
        )
        response.raise_for_status()
        data = response.json()
        self._access_token = data["access_token"]
        # Set expiration slightly before actual expiry (usually 3600s)
        self._token_expires_at = time.time() + data.get("expires_in", 3600) - 60

    def validate_credentials(self) -> bool:
        """Test connection by refreshing token and checking profile."""
        try:
            self._refresh_access_token()
            # Optional: Call a lightweight endpoint like /v2/profiles to verify profile_id
            return True
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False

    def fetch_data(self, start_date: date, end_date: date, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Fetches Sponsored Products Search Term Report.
        
        Args:
            start_date: Report start date
            end_date: Report end date (Amazon usually limits this range)
            **kwargs: Additional args like 'report_type'
        """
        report_type = kwargs.get("report_type", "spSearchTerm")
        
        # 1. Request Report
        report_id = self._request_report(start_date, end_date, report_type)
        if not report_id:
            return

        # 2. Poll for Completion
        download_url = self._wait_for_report(report_id)
        if not download_url:
            return

        # 3. Download and Yield Data
        yield from self._download_and_parse(download_url)

    def _request_report(self, start_date: date, end_date: date, report_type: str) -> Optional[str]:
        """Initiates a report generation request."""
        url = f"{self.config.base_url}/reporting/reports"
        
        # Payload for SP Search Term Report (v3 API structure)
        payload = {
            "name": f"AskJeff_Sync_{report_type}_{start_date}",
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": ["campaign", "adGroup"],
                "columns": [
                    "campaignId", "campaignName", 
                    "adGroupId", "adGroupName",
                    "keywordId", "keywordText", 
                    "matchType", 
                    "query",  # This is the Search Term
                    "impressions", "clicks", "cost", "spend", 
                    "sales14d", "orders14d", "unitsSold14d"
                ],
                "reportTypeId": "spSearchTerm",
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON"
            }
        }
        
        try:
            response = self.client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            report_id = response.json().get("reportId")
            logger.info(f"Report requested. ID: {report_id}")
            return report_id
        except Exception as e:
            logger.error(f"Failed to request report: {e}")
            # Log response body for debugging
            if 'response' in locals():
                logger.error(f"Response: {response.text}")
            return None

    def _wait_for_report(self, report_id: str, max_retries: int = 20) -> Optional[str]:
        """Polls the report status until it's COMPLETED."""
        url = f"{self.config.base_url}/reporting/reports/{report_id}"
        
        for i in range(max_retries):
            try:
                response = self.client.get(url, headers=self._get_headers())
                response.raise_for_status()
                data = response.json()
                status = data.get("status")
                
                if status == "COMPLETED":
                    return data.get("url")
                elif status == "FAILURE":
                    logger.error(f"Report generation failed: {data}")
                    return None
                
                logger.debug(f"Report status: {status}. Waiting...")
                time.sleep(2 * (i + 1))  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Error polling report status: {e}")
                
        logger.error(f"Report generation timed out after {max_retries} attempts.")
        return None

    def _download_and_parse(self, download_url: str) -> Generator[Dict[str, Any], None, None]:
        """Downloads GZIP JSON report and yields records."""
        try:
            # Download directly (no auth headers needed for S3 link usually, but check API docs)
            # Usually Amazon report URLs are pre-signed S3 URLs.
            response = self.client.get(download_url)
            response.raise_for_status()
            
            # Decompress and parse
            content = gzip.decompress(response.content)
            data = json.loads(content)
            
            # Amazon v3 reports usually wrap data in a list directly or under a key
            # If format is GZIP_JSON, it's typically a JSON list of objects.
            if isinstance(data, list):
                for record in data:
                    yield record
            else:
                logger.warning(f"Unexpected report format: {type(data)}")
                
        except Exception as e:
            logger.error(f"Failed to download/parse report: {e}")
