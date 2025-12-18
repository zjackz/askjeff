"""
缓存服务

提供 Redis 缓存功能，用于减少 API 调用次数和成本。
"""

import redis.asyncio as redis
import json
import hashlib
from typing import Optional, Any, Dict
import logging
import os

logger = logging.getLogger(__name__)


class CacheService:
    """
    多级缓存服务
    
    提供 Redis 缓存功能，支持：
    - 异步操作
    - 自动序列化/反序列化
    - TTL 管理
    - 缓存键生成
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        初始化缓存服务
        
        Args:
            redis_url: Redis 连接 URL，默认从环境变量读取
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = 86400  # 24 小时
        
        # 不同类型数据的 TTL 配置
        self.ttl_config = {
            "product_selection": 86400,      # 24 小时
            "keyword_optimization": 43200,   # 12 小时
            "product_detail": 21600,         # 6 小时
            "category_data": 172800,         # 48 小时
        }
        
        logger.info(f"CacheService initialized with URL: {self.redis_url}")
    
    async def connect(self):
        """连接到 Redis"""
        if not self.redis_client:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                # 测试连接
                await self.redis_client.ping()
                logger.info("Successfully connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self.redis_client = None
    
    async def disconnect(self):
        """断开 Redis 连接"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存的数据，如果不存在返回 None
        """
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            logger.warning("Redis not available, cache disabled")
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data:
                logger.info(f"Cache HIT: {key}")
                return json.loads(data)
            else:
                logger.info(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 要缓存的数据（必须可 JSON 序列化）
            ttl: 过期时间（秒），默认使用 default_ttl
        
        Returns:
            是否设置成功
        """
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            logger.warning("Redis not available, cache disabled")
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, ensure_ascii=False)
            
            await self.redis_client.setex(
                key,
                ttl,
                serialized
            )
            
            logger.info(f"Cache SET: {key}, TTL: {ttl}s")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            logger.info(f"Cache DELETE: {key}, result: {result}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            是否存在
        """
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    def generate_key(self, prefix: str, **params) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 键前缀（如 "product_selection", "keyword_optimization"）
            **params: 参数字典
        
        Returns:
            生成的缓存键
        """
        # 排序参数确保一致性
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        
        # 生成哈希
        hash_str = hashlib.md5(param_str.encode()).hexdigest()
        
        # 组合键
        key = f"askjeff:{prefix}:{hash_str}"
        
        return key
    
    def get_ttl_for_type(self, cache_type: str) -> int:
        """
        获取指定类型的 TTL
        
        Args:
            cache_type: 缓存类型
        
        Returns:
            TTL（秒）
        """
        return self.ttl_config.get(cache_type, self.default_ttl)
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            return {"status": "unavailable"}
        
        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": await self.redis_client.dbsize(),
                "hit_rate": "N/A"  # 需要额外跟踪
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {"status": "error", "error": str(e)}


# 全局缓存服务实例
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    获取全局缓存服务实例
    
    Returns:
        CacheService 实例
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
