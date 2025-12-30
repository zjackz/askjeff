import logging
import time
import requests
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AmazonBaseClient:
    """
    Amazon API 基础客户端，处理 LWA 鉴权和 Token 刷新
    """
    def __init__(self, refresh_token: str = None):
        self.client_id = settings.amazon_client_id
        self.client_secret = settings.amazon_client_secret
        self.refresh_token = refresh_token or settings.amazon_refresh_token
        self.access_token = None
        self.token_expiry = 0
        
        # 如果是测试环境且没有配置，允许跳过
        if settings.is_testing and not self.client_id:
            logger.warning("Amazon Client ID mapping missing in testing mode.")

    def _get_access_token(self) -> str:
        """获取有效的 Access Token"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
            
        return self._refresh_access_token()

    def _refresh_access_token(self) -> str:
        """通过 LWA 刷新 Access Token"""
        url = "https://api.amazon.com/auth/o2/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            # 提前 60 秒过期，留出缓冲
            self.token_expiry = time.time() + token_data["expires_in"] - 60
            logger.info("Amazon Access Token refreshed successfully.")
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to refresh Amazon Access Token: {str(e)}")
            raise

    def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """发送请求，包含自动重试逻辑 (429/Token过期)"""
        headers = kwargs.get("headers", {})
        
        # 自动注入 Token
        if "x-amz-access-token" not in headers:
            token = self._get_access_token()
            headers["x-amz-access-token"] = token
            
        kwargs["headers"] = headers
        
        # 简单的重试逻辑
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, **kwargs)
                
                # 处理 429 Too Many Requests
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"Rate limited (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # 如果是 401，可能是 Token 过期，尝试强制刷新一次
                if e.response.status_code == 401 and attempt == 0:
                    logger.warning("401 Unauthorized. Retrying with fresh token...")
                    self.access_token = None # 清除缓存
                    # 更新 headers 中的 token
                    headers["x-amz-access-token"] = self._get_access_token()
                    kwargs["headers"] = headers
                    continue
                raise
                
        raise Exception(f"Max retries exceeded for {url}")
