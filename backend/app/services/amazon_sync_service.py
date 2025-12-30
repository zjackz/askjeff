import json
import time
import logging
from datetime import date, timedelta
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.amazon_ads import (
    AmazonStore,
    InventorySnapshot,
    BusinessMetricSnapshot,
    AdsMetricSnapshot
)
from app.clients.amazon.sp_api_client import SpApiClient
from app.clients.amazon.ads_api_client import AdsApiClient

logger = logging.getLogger(__name__)

class AmazonSyncService:
    def __init__(self, db: Session):
        self.db = db
        # 注意: 实际使用时需动态获取每个店铺的 refresh_token
        # 这里为简化 MVP，假设 Client 内部能处理或已被初始化
        self.sp_client = SpApiClient()
        self.ads_client = AdsApiClient()

    def _get_store_creds(self, store_id: UUID) -> AmazonStore:
        store = self.db.query(AmazonStore).get(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        if not store.sp_api_refresh_token:
            raise HTTPException(status_code=400, detail="Store missing SP-API credentials")
        return store

    def sync_all(self, store_id: UUID):
        """
        触发全量同步 (Inventory + Business + Ads)
        """
        logger.info(f"Starting full sync for store {store_id}")
        store = self._get_store_creds(store_id)
        
        # 1. 刷新 Token (如果 Client 支持动态设置)
        self.sp_client.refresh_token = store.sp_api_refresh_token
        self.ads_client.refresh_token = store.advertising_api_refresh_token
        if store.advertising_api_refresh_token:
             # ProfilID 很多时候需要额外存储和获取，这里简化
             pass
        
        # 2. 同步库存 (实时)
        self.sync_inventory(store, store.marketplace_id)
        
        # 3. 同步业务报告 (过去 30 天)
        self.sync_business_report(store, days=30)
        
        # 4. 同步广告报告 (过去 30 天)
        if store.advertising_api_refresh_token:
            self.sync_ads_report(store, days=30)
            
        logger.info(f"Full sync completed for store {store_id}")
        return {"status": "completed"}

    def sync_inventory(self, store: AmazonStore, marketplace_id: str):
        """同步 FBA 库存"""
        logger.info(f"Syncing inventory for store {store.id}")
        try:
            # 调用 SP-API
            data = self.sp_client.get_inventory_summary(marketplace_id)
            items = data.get("payload", {}).get("inventorySummaries", [])
            
            today = date.today()
            count = 0
            
            for item in items:
                sku = item.get("sellerSku")
                if not sku: continue
                
                # Update InventorySnapshot
                details = item.get("inventoryDetails", {})
                fba_qty = details.get("fulfillableQuantity", 0)
                inbound = details.get("inboundQuantity", {}).get("totalQuantity", 0)
                reserved = details.get("reservedQuantity", {}).get("totalQuantity", 0)
                unfulfillable = details.get("unfulfillableQuantity", {}).get("totalQuantity", 0)
                
                snapshot = self.db.query(InventorySnapshot).filter(
                    InventorySnapshot.store_id == store.id,
                    InventorySnapshot.date == today,
                    InventorySnapshot.sku == sku
                ).first()
                
                if not snapshot:
                    snapshot = InventorySnapshot(
                        store_id=store.id,
                        date=today,
                        sku=sku,
                        asin=item.get("asin")
                    )
                    self.db.add(snapshot)
                
                snapshot.fba_inventory = fba_qty
                snapshot.inbound_inventory = inbound
                snapshot.reserved_inventory = reserved
                snapshot.unfulfillable_inventory = unfulfillable
                count += 1
            
            self.db.commit()
            logger.info(f"Synced {count} inventory items")
            
        except Exception as e:
            logger.error(f"Inventory sync failed: {e}")
            self.db.rollback()
            raise

    def sync_business_report(self, store: AmazonStore, days: int = 30):
        """
        同步业务报告 (GET_SALES_AND_TRAFFIC_REPORT)
        MVP: 简化为模拟数据或伪代码，因为报告下载流程较长
        """
        logger.info("Syncing business report (Mock implementation for MVP)")
        # 真实流程:
        # 1. create_report
        # 2. loop get_report check status until DONE
        # 3. get_report_document -> download -> parse
        pass

    def sync_ads_report(self, store: AmazonStore, days: int = 30):
        """
        同步广告报告
        MVP: 简化为模拟数据
        """
        logger.info("Syncing ads report (Mock implementation for MVP)")
        pass
