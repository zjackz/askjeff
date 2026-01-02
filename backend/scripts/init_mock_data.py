import sys
import os
from datetime import datetime, timedelta
import random

# 添加 backend 目录到路径
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db import SessionLocal
from app.models.amazon_ads import AmazonStore, SyncTask
from app.services.mock_data_generator import MockDataGenerator

from app.models.user import User

def init_mock_data():
    db = SessionLocal()
    try:
        print("开始生成初始 Mock 数据...")
        
        # 0. 获取有效用户
        user = db.query(User).first()
        if not user:
            print("未找到用户，正在创建测试用户...")
            # 这里简化处理，假设 User 模型有 email/password 等字段
            # 实际情况可能需要更多字段，或者直接报错提示先注册
            # 为了脚本健壮性，我们尝试获取 ID=1 的用户，如果不存在则报错
            print("❌ 数据库中没有用户，请先注册一个用户。")
            return

        print(f"使用用户: {user.username} (ID: {user.id})")
        
        # 1. 获取或创建一个测试店铺
        store = db.query(AmazonStore).first()
        if not store:
            print("未找到店铺，正在创建测试店铺...")
            store = AmazonStore(
                user_id=user.id,
                store_name="Official Store (US)",
                seller_id="SELLER_TEST_001",
                marketplace_id="ATVPDKIKX0DER", # US
                marketplace_name="United States",
                sp_api_refresh_token="mock_refresh_token",
                advertising_api_refresh_token="mock_ads_token",
                is_active=True
            )
            db.add(store)
            db.commit()
            db.refresh(store)
            print(f"创建了测试店铺: {store.store_name} (ID: {store.id})")
        else:
            print(f"使用现有店铺: {store.store_name} (ID: {store.id})")

        # 2. 生成过去 5 天的同步记录
        sync_types = ['inventory', 'business', 'advertising']
        generator = MockDataGenerator()
        
        for i in range(5):
            date_offset = 4 - i # 4天前, 3天前... 今天
            sync_date = datetime.utcnow() - timedelta(days=date_offset)
            
            print(f"生成 {sync_date.date()} 的同步记录...")
            
            for sync_type in sync_types:
                # 模拟不同的同步结果
                status = 'success'
                records = random.randint(50, 200)
                error_msg = None
                
                # 偶尔模拟一个失败
                if random.random() < 0.1: 
                    status = 'failed'
                    records = 0
                    error_msg = "Network timeout connection to SP-API"
                
                # 创建任务记录
                task = SyncTask(
                    store_id=store.id,
                    sync_type=sync_type,
                    status=status,
                    start_time=sync_date.replace(hour=2, minute=random.randint(0, 59)),
                    end_time=sync_date.replace(hour=2, minute=random.randint(0, 59)) + timedelta(seconds=random.randint(10, 120)),
                    records_synced=records,
                    records_failed=0,
                    error_message=error_msg,
                    created_at=sync_date
                )
                db.add(task)
        
        db.commit()
        print("✅ 初始 Mock 数据生成完成！")
        print(f"店铺 ID: {store.id}")
        print("请在前端刷新页面查看。")
        
    except Exception as e:
        print(f"❌ 生成数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_mock_data()
