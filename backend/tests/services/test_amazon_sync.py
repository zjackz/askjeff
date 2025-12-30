from datetime import date
from uuid import uuid4
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.amazon_sync_service import AmazonSyncService
from app.models.amazon_ads import AmazonStore, InventorySnapshot

def test_sync_inventory(db: Session):
    # 1. Setup Data
    user_id = 1
    store = AmazonStore(
        id=uuid4(),
        user_id=user_id,
        store_name="Test Store",
        marketplace_id="US", 
        seller_id="SELLER",
        sp_api_refresh_token="ref_token"
    )
    db.add(store)
    db.commit()

    # 2. Mock Clients
    with patch("app.services.amazon_sync_service.SpApiClient") as MockSpClient:
        mock_sp = MockSpClient.return_value
        mock_sp.get_inventory_summary.return_value = {
            "payload": {
                "inventorySummaries": [
                    {
                        "sellerSku": "SKU-001",
                        "asin": "ASIN-001",
                        "inventoryDetails": {
                            "fulfillableQuantity": 10,
                            "inboundQuantity": {"totalQuantity": 5}
                        }
                    }
                ]
            }
        }
        
        # 3. Execute
        service = AmazonSyncService(db)
        # Mock internal clients too (because init creates new instances)
        service.sp_client = mock_sp
        
        service.sync_inventory(store, "US")
        
        # 4. Verify
        snapshot = db.query(InventorySnapshot).filter_by(sku="SKU-001").first()
        assert snapshot is not None
        assert snapshot.fba_inventory == 10
        assert snapshot.inbound_inventory == 5
        assert snapshot.store_id == store.id

def test_sync_all_trigger(db: Session):
    store = AmazonStore(
        id=uuid4(), 
        user_id=1, 
        marketplace_id="US", 
        seller_id="S2", 
        sp_api_refresh_token="rt",
        advertising_api_refresh_token="art"
    )
    db.add(store)
    db.commit()
    
    with patch.object(AmazonSyncService, 'sync_inventory') as mock_inv, \
         patch.object(AmazonSyncService, 'sync_business_report') as mock_biz, \
         patch.object(AmazonSyncService, 'sync_ads_report') as mock_ads:
        
        service = AmazonSyncService(db)
        # Mock internal clients
        service.sp_client = MagicMock()
        service.ads_client = MagicMock()
        
        service.sync_all(store.id)
        
        assert mock_inv.called
        assert mock_biz.called
        assert mock_ads.called

