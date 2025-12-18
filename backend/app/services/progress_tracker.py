"""
API 导入进度跟踪器

简单可靠的进度管理方案,使用 import_metadata JSON 字段存储实时进度
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.import_batch import ImportBatch
import logging

logger = logging.getLogger(__name__)


class ProgressTracker:
    """API 导入进度跟踪器"""
    
    # 阶段定义: (起始百分比, 结束百分比)
    PHASES = {
        "preparing": (0, 10),           # 准备阶段
        "fetching_list": (10, 20),      # 获取产品列表
        "fetching_details": (20, 90),   # 获取产品详情 (主要阶段)
        "saving": (90, 95),             # 保存到数据库
        "generating_excel": (95, 100),  # 生成 Excel
        "completed": (100, 100),        # 完成
    }
    
    @staticmethod
    def update_progress(
        db: Session,
        batch_id: int,
        phase: str,
        current: int = 0,
        total: int = 0,
        message: Optional[str] = None
    ):
        """
        更新进度 (简化版)
        
        直接更新 total_rows, success_rows 和状态,不依赖复杂的 JSON 更新
        """
        try:
            batch = db.get(ImportBatch, batch_id)
            if not batch:
                logger.warning(f"批次 {batch_id} 不存在,无法更新进度")
                return
            
            # 生成默认消息
            if not message:
                phase_names = {
                    "preparing": "准备中",
                    "fetching_list": "获取产品列表",
                    "fetching_details": "获取产品详情",
                    "saving": "保存数据",
                    "generating_excel": "生成文件",
                    "completed": "完成",
                }
                phase_name = phase_names.get(phase, phase)
                if total > 0:
                    message = f"{phase_name} ({current}/{total})"
                else:
                    message = phase_name
            
            # 更新简单字段 (更可靠)
            if total > 0:
                batch.total_rows = total
            if current > 0:
                batch.success_rows = current
            
            # 更新状态
            if phase == "completed":
                batch.status = "succeeded"
            elif phase != "preparing":
                batch.status = "running"
            
            # 在 metadata 中只存储阶段和消息 (简单字符串,不是嵌套 JSON)
            if not batch.import_metadata:
                batch.import_metadata = {}
            batch.import_metadata["current_phase"] = phase
            batch.import_metadata["current_message"] = message
            
            # 提交更改
            db.commit()
            
            logger.debug(f"[{batch_id}] 进度更新: {phase} - {message}")
            
        except Exception as e:
            logger.error(f"更新进度失败 (batch_id={batch_id}): {e}", exc_info=True)
            # 不抛出异常,避免影响主流程
            try:
                db.rollback()
            except:
                pass
    
    @staticmethod
    def mark_failed(db: Session, batch_id: int, error_message: str):
        """标记为失败"""
        try:
            batch = db.get(ImportBatch, batch_id)
            if not batch:
                return
            
            if not batch.import_metadata:
                batch.import_metadata = {}
            
            batch.import_metadata["progress"] = {
                "phase": "failed",
                "percentage": 0,
                "message": f"失败: {error_message}",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            batch.status = "failed"
            db.commit()
            
        except Exception as e:
            logger.error(f"标记失败状态出错: {e}", exc_info=True)
    
    @staticmethod
    def get_progress(batch: ImportBatch) -> dict:
        """
        获取进度信息 (简化版)
        
        根据 total_rows 和 success_rows 计算进度
        """
        if not batch.import_metadata:
            return {"percentage": 0, "message": "准备中...", "phase": "preparing"}
        
        # 获取当前阶段和消息
        phase = batch.import_metadata.get("current_phase", "preparing")
        message = batch.import_metadata.get("current_message", "处理中...")
        
        # 根据阶段和数据计算百分比
        if batch.status == "succeeded":
            return {
                "percentage": 100,
                "message": f"完成! 共 {batch.total_rows} 条数据",
                "phase": "completed"
            }
        
        if batch.status == "failed":
            return {
                "percentage": 0,
                "message": "导入失败",
                "phase": "failed"
            }
        
        # 根据阶段和实际数据计算进度
        if phase in ProgressTracker.PHASES:
            phase_start, phase_end = ProgressTracker.PHASES[phase]
            
            # 如果有总数和当前数,计算实际进度
            if batch.total_rows > 0 and batch.success_rows > 0:
                real_progress = (batch.success_rows / batch.total_rows) * 100
                # 映射到阶段范围
                if phase == "fetching_details":
                    # 主要阶段 (20-90%)
                    percentage = int(20 + (real_progress * 0.7))
                else:
                    # 其他阶段使用阶段起始值
                    percentage = phase_start
            else:
                percentage = phase_start
        else:
            percentage = 0
        
        return {
            "percentage": max(0, min(100, percentage)),
            "message": message,
            "phase": phase
        }
