import pytest
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import date
from app.services.ads_import_service import AdsImportService
from app.models.amazon_ads import ProductCost, AdsMetricSnapshot

@pytest.fixture
def store_id(db: Session):
    from app.models.amazon_ads import AmazonStore
    from app.models.user import User
    from uuid import uuid4
    
    user = User(username="import_test_user", hashed_password="pw")
    db.add(user)
    db.commit()
    
    store = AmazonStore(
        id=uuid4(),
        user_id=user.id,
        store_name="Import Test Store",
        marketplace_id="ATVPDKIKX0DER",
        marketplace_name="US",
        seller_id="IMPORT_SELLER"
    )
    db.add(store)
    db.commit()
    return store.id

@pytest.mark.asyncio
async def test_import_product_costs(db: Session, store_id):
    csv_content = "SKU,ASIN,COGS,FBA_Fee,Referral_Rate\nSKU1,ASIN1,10.5,3.2,0.15\nSKU2,ASIN2,20.0,5.0,0.15"
    file = UploadFile(filename="costs.csv", file=BytesIO(csv_content.encode('utf-8')))
    
    result = await AdsImportService.import_product_costs(db, store_id, file)
    
    assert result["success"] == 2
    assert result["errors"] == 0
    
    # Verify DB
    costs = db.query(ProductCost).filter(ProductCost.store_id == store_id).all()
    assert len(costs) == 2
    assert costs[0].sku == "SKU1"
    assert costs[0].cogs == 10.5

@pytest.mark.asyncio
async def test_import_ads_report(db: Session, store_id):
    csv_content = "Date,SKU,ASIN,Spend,Sales,Impressions,Clicks,Orders\n2025-12-30,SKU1,ASIN1,50.0,200.0,1000,100,10"
    file = UploadFile(filename="ads.csv", file=BytesIO(csv_content.encode('utf-8')))
    
    result = await AdsImportService.import_ads_report(db, store_id, file)
    
    assert result["success"] == 1
    
    # Verify DB
    snapshot = db.query(AdsMetricSnapshot).filter(
        AdsMetricSnapshot.store_id == store_id,
        AdsMetricSnapshot.sku == "SKU1"
    ).first()
    assert snapshot is not None
    assert snapshot.spend == 50.0
    assert snapshot.orders == 10
    assert snapshot.date == date(2025, 12, 30)
