import sys
import os
from datetime import date
from unittest.mock import MagicMock, patch

# Add JDC to path
current_dir = os.path.dirname(os.path.abspath(__file__))
jdc_path = os.path.abspath(os.path.join(current_dir, "../../packages/jeff-data-core"))
sys.path.append(jdc_path)

# Add Backend App to path (for DB config)
backend_path = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(backend_path)

from jeff_data_core.core.engine import JeffDataEngine
from jeff_data_core.connectors.amazon_ads import AmazonAdsConnector, AmazonAdsConfig
from jeff_data_core.storage.postgres import PostgresStorage

def test_jdc_flow():
    print(">>> Starting JDC Integration Test")

    # 1. Setup Storage
    # Use environment variable injected into the container
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Adapt for psycopg 3 driver
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
        
    print(f">>> Connecting to DB: {db_url}")
    storage = PostgresStorage(connection_string=db_url)

    # 2. Setup Connector (Mocked)
    config = AmazonAdsConfig(
        name="test_amazon",
        client_id="mock_id",
        client_secret="mock_secret",
        refresh_token="mock_token",
        profile_id="mock_profile"
    )
    
    connector = AmazonAdsConnector(config)
    
    # Mock validate_credentials
    connector.validate_credentials = MagicMock(return_value=True)
    
    # Mock fetch_data to yield sample records
    sample_records = [
        {
            "campaignId": "12345",
            "campaignName": "Test Campaign",
            "query": "running shoes",
            "impressions": 100,
            "clicks": 10,
            "cost": 5.0,
            "sales14d": 50.0
        },
        {
            "campaignId": "12345",
            "campaignName": "Test Campaign",
            "query": "blue shoes",
            "impressions": 200,
            "clicks": 5,
            "cost": 2.0,
            "sales14d": 0.0
        }
    ]
    connector.fetch_data = MagicMock(return_value=iter(sample_records))

    # 3. Run Engine
    engine = JeffDataEngine(storage_backend=storage)
    
    print(">>> Running Sync...")
    result = engine.run_sync(
        connector=connector,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 7)
    )
    
    print(f">>> Sync Result: {result}")

    # 4. Verify Data in DB
    # We query the jdc_raw_data_logs table directly using SQLAlchemy
    from jeff_data_core.storage.postgres import RawDataLog
    session = storage.Session()
    logs = session.query(RawDataLog).filter_by(source="amazon_ads").all()
    
    print(f">>> Found {len(logs)} records in Raw Data Log.")
    
    for log in logs:
        print(f"    - ID: {log.id}, Type: {log.data_type}, Payload: {log.payload}")
        
    session.close()

    if len(logs) >= 2:
        print(">>> TEST PASSED: Data successfully flowed from Connector to Storage.")
    else:
        print(">>> TEST FAILED: Data missing.")

if __name__ == "__main__":
    test_jdc_flow()
