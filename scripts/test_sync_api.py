import requests
import time

# API 基础 URL
BASE_URL = "http://localhost:8001/api/v1"

# 1. 获取店铺列表 (需要先登录获取 token,这里简化假设已认证或使用 Mock)
# 注意: 实际测试需要处理认证

def test_sync_api():
    print("开始测试同步 API...")
    
    # 模拟触发同步
    # POST /api/v1/amazon/sync/all
    # 由于需要认证,这里仅打印 curl 命令供手动测试
    
    print("\n请使用以下命令手动测试:")
    print(f"curl -X POST '{BASE_URL}/amazon/sync/all?use_mock=true' -H 'Authorization: Bearer YOUR_TOKEN'")
    
    # 查询任务状态
    print(f"curl -X GET '{BASE_URL}/amazon/sync-tasks' -H 'Authorization: Bearer YOUR_TOKEN'")

if __name__ == "__main__":
    test_sync_api()
