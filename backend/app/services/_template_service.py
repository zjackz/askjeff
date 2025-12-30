"""
新服务模板

使用方法:
1. 复制此文件到 backend/app/services/
2. 重命名为 your_service.py
3. 替换 Template 为你的服务名
4. 实现具体业务逻辑
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TemplateService:
    """
    [服务名称] 服务类
    
    功能描述:
    - 功能 1
    - 功能 2
    - 功能 3
    """
    
    def __init__(self):
        """初始化服务"""
        logger.info("初始化 TemplateService")
    
    async def process(
        self,
        db: Session,
        *,
        param1: str,
        param2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理主要业务逻辑
        
        Args:
            db: 数据库会话
            param1: 参数1说明
            param2: 参数2说明 (可选)
        
        Returns:
            处理结果字典:
            {
                "status": "success" | "failed",
                "message": "处理消息",
                "data": {...}
            }
        
        Raises:
            ValueError: 参数错误
            Exception: 处理失败
        """
        logger.info(f"开始处理: param1={param1}, param2={param2}")
        
        try:
            # 1. 参数验证
            if not param1:
                raise ValueError("param1 不能为空")
            
            # 2. 业务逻辑处理
            result = self._do_process(param1, param2)
            
            # 3. 返回结果
            logger.info("处理完成")
            return {
                "status": "success",
                "message": "处理成功",
                "data": result
            }
            
        except ValueError as e:
            logger.warning(f"参数错误: {e}")
            raise
        except Exception as e:
            logger.error(f"处理失败: {e}", exc_info=True)
            raise
    
    def _do_process(self, param1: str, param2: Optional[str]) -> Dict[str, Any]:
        """
        内部处理逻辑
        
        Args:
            param1: 参数1
            param2: 参数2
        
        Returns:
            处理结果
        """
        # 实现具体业务逻辑
        return {
            "param1": param1,
            "param2": param2,
            "processed": True
        }


# 创建服务实例
template_service = TemplateService()
