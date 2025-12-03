"""错误码定义

定义所有业务和系统错误码
"""
from __future__ import annotations


class ErrorCode:
    """错误码常量"""
    
    # ========== 验证错误 (400) ==========
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    MISSING_REQUIRED_COLUMNS = "MISSING_REQUIRED_COLUMNS"
    INVALID_DATA_TYPE = "INVALID_DATA_TYPE"
    
    # ========== 业务错误 (422) ==========
    DUPLICATE_DATA = "DUPLICATE_DATA"
    BATCH_NOT_FOUND = "BATCH_NOT_FOUND"
    RUN_NOT_FOUND = "RUN_NOT_FOUND"
    EXPORT_JOB_NOT_FOUND = "EXPORT_JOB_NOT_FOUND"
    INVALID_IMPORT_STRATEGY = "INVALID_IMPORT_STRATEGY"
    
    # ========== 系统错误 (500) ==========
    DATABASE_ERROR = "DATABASE_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


# 错误码到用户友好消息的映射
ERROR_MESSAGES = {
    # 验证错误
    ErrorCode.VALIDATION_ERROR: "输入数据验证失败",
    ErrorCode.INVALID_FILE_FORMAT: "文件格式不正确,仅支持 CSV 和 XLSX 格式",
    ErrorCode.FILE_TOO_LARGE: "文件大小超过限制",
    ErrorCode.MISSING_REQUIRED_COLUMNS: "文件缺少必需的列",
    ErrorCode.INVALID_DATA_TYPE: "数据类型不正确",
    
    # 业务错误
    ErrorCode.DUPLICATE_DATA: "数据已存在",
    ErrorCode.BATCH_NOT_FOUND: "批次不存在",
    ErrorCode.RUN_NOT_FOUND: "提取记录不存在",
    ErrorCode.EXPORT_JOB_NOT_FOUND: "导出任务不存在",
    ErrorCode.INVALID_IMPORT_STRATEGY: "导入策略不正确",
    
    # 系统错误
    ErrorCode.DATABASE_ERROR: "数据库操作失败,请稍后重试",
    ErrorCode.STORAGE_ERROR: "文件存储失败,请稍后重试",
    ErrorCode.EXTERNAL_API_ERROR: "外部服务暂时不可用,请稍后重试",
    ErrorCode.INTERNAL_SERVER_ERROR: "系统繁忙,请稍后重试",
}


class AppException(Exception):
    """应用异常基类"""
    
    def __init__(
        self,
        code: str,
        message: str | None = None,
        details: dict | None = None,
        status_code: int = 400
    ):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, "未知错误")
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(AppException):
    """验证异常"""
    def __init__(self, code: str = ErrorCode.VALIDATION_ERROR, message: str | None = None, details: dict | None = None):
        super().__init__(code, message, details, status_code=400)


class BusinessException(AppException):
    """业务异常"""
    def __init__(self, code: str, message: str | None = None, details: dict | None = None):
        super().__init__(code, message, details, status_code=422)


class SystemException(AppException):
    """系统异常"""
    def __init__(self, code: str = ErrorCode.INTERNAL_SERVER_ERROR, message: str | None = None, details: dict | None = None):
        super().__init__(code, message, details, status_code=500)
