"""日志配置模块"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os


def setup_logging(log_dir: str = "./logs", log_level: str = "INFO"):
    """
    配置日志系统
    
    Args:
        log_dir: 日志文件目录
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除已有的处理器
    root_logger.handlers.clear()
    
    # 控制台处理器（输出到终端）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt=date_format
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器 - 所有日志
    all_log_file = log_path / "app.log"
    all_file_handler = RotatingFileHandler(
        all_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    all_file_handler.setLevel(logging.DEBUG)
    all_file_formatter = logging.Formatter(log_format, datefmt=date_format)
    all_file_handler.setFormatter(all_file_formatter)
    root_logger.addHandler(all_file_handler)
    
    # 文件处理器 - 错误日志
    error_log_file = log_path / "error.log"
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(all_file_formatter)
    root_logger.addHandler(error_file_handler)
    
    # 文件处理器 - 请求日志
    request_log_file = log_path / "request.log"
    request_file_handler = RotatingFileHandler(
        request_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    request_file_handler.setLevel(logging.INFO)
    request_formatter = logging.Formatter(
        "%(asctime)s - %(message)s",
        datefmt=date_format
    )
    request_file_handler.setFormatter(request_formatter)
    
    # 创建请求日志记录器
    request_logger = logging.getLogger("request")
    request_logger.setLevel(logging.INFO)
    request_logger.addHandler(request_file_handler)
    request_logger.propagate = False
    
    # 文件处理器 - OCR日志
    ocr_log_file = log_path / "ocr.log"
    ocr_file_handler = RotatingFileHandler(
        ocr_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    ocr_file_handler.setLevel(logging.INFO)
    ocr_file_handler.setFormatter(all_file_formatter)
    
    ocr_logger = logging.getLogger("ocr")
    ocr_logger.setLevel(logging.INFO)
    ocr_logger.addHandler(ocr_file_handler)
    ocr_logger.propagate = False
    
    # 文件处理器 - LLM日志
    llm_log_file = log_path / "llm.log"
    llm_file_handler = RotatingFileHandler(
        llm_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    llm_file_handler.setLevel(logging.INFO)
    llm_file_handler.setFormatter(all_file_formatter)
    
    llm_logger = logging.getLogger("llm")
    llm_logger.setLevel(logging.INFO)
    llm_logger.addHandler(llm_file_handler)
    llm_logger.propagate = False


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，默认为调用模块名
    
    Returns:
        日志记录器实例
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__", "app")
    
    return logging.getLogger(name)


def get_request_logger() -> logging.Logger:
    """获取请求日志记录器"""
    return logging.getLogger("request")


def get_ocr_logger() -> logging.Logger:
    """获取OCR日志记录器"""
    return logging.getLogger("ocr")


def get_llm_logger() -> logging.Logger:
    """获取LLM日志记录器"""
    return logging.getLogger("llm")

