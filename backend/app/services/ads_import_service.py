import csv
import logging
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.amazon_ads import ProductCost, AdsMetricSnapshot, BusinessMetricSnapshot

logger = logging.getLogger(__name__)

class AdsImportService:
    @staticmethod
    async def import_product_costs(db: Session, store_id: UUID, file: UploadFile) -> Dict:
        """
        导入产品成本 CSV
        格式要求: SKU, ASIN, COGS, FBA_Fee, Referral_Rate
        """
        content = await file.read()
        decoded = content.decode('utf-8-sig').splitlines()
        reader = csv.DictReader(decoded)
        
        success_count = 0
        error_count = 0
        
        for row in reader:
            try:
                sku = row.get('SKU')
                if not sku: continue
                
                # 更新或创建
                cost = db.query(ProductCost).filter(
                    ProductCost.store_id == store_id,
                    ProductCost.sku == sku
                ).first()
                
                if not cost:
                    cost = ProductCost(store_id=store_id, sku=sku)
                    db.add(cost)
                
                cost.asin = row.get('ASIN', cost.asin)
                cost.cogs = float(row.get('COGS', 0))
                cost.fba_fee = float(row.get('FBA_Fee', 0))
                cost.referral_fee_rate = float(row.get('Referral_Rate', 0.15))
                cost.updated_at = datetime.utcnow()
                
                success_count += 1
            except Exception as e:
                logger.error(f"Import cost row failed: {row}, error: {e}")
                error_count += 1
        
        db.commit()
        return {"success": success_count, "errors": error_count}

    @staticmethod
    async def import_ads_report(db: Session, store_id: UUID, file: UploadFile) -> Dict:
        """
        导入广告报表 CSV (SKU 粒度)
        格式要求: Date, SKU, ASIN, Spend, Sales, Impressions, Clicks, Orders
        """
        content = await file.read()
        decoded = content.decode('utf-8-sig').splitlines()
        reader = csv.DictReader(decoded)
        
        success_count = 0
        for row in reader:
            try:
                date_str = row.get('Date')
                sku = row.get('SKU')
                if not date_str or not sku: continue
                
                report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # 更新或创建快照
                snapshot = db.query(AdsMetricSnapshot).filter(
                    AdsMetricSnapshot.store_id == store_id,
                    AdsMetricSnapshot.date == report_date,
                    AdsMetricSnapshot.sku == sku
                ).first()
                
                if not snapshot:
                    snapshot = AdsMetricSnapshot(
                        store_id=store_id,
                        date=report_date,
                        sku=sku,
                        asin=row.get('ASIN')
                    )
                    db.add(snapshot)
                
                snapshot.spend = float(row.get('Spend', 0))
                snapshot.sales = float(row.get('Sales', 0))
                snapshot.impressions = int(row.get('Impressions', 0))
                snapshot.clicks = int(row.get('Clicks', 0))
                snapshot.orders = int(row.get('Orders', 0))
                snapshot.units = int(row.get('Units', snapshot.orders))
                
                success_count += 1
            except Exception as e:
                logger.error(f"Import ads row failed: {e}")
        
        db.commit()
        return {"success": success_count}

ads_import_service = AdsImportService()
