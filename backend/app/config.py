"""应用配置"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 服务配置
    app_name: str = "李会计凭证识别系统"
    debug: bool = True
    
    # OCR配置
    ocr_provider: str = Field(default="baidu", description="OCR提供商: baidu, aliyun, tencent")
    ocr_api_key: Optional[str] = Field(
        default=None,
        description="OCR API Key"
    )
    ocr_secret_key: Optional[str] = Field(
        default=None,
        description="OCR Secret Key"
    )
    ocr_endpoint: Optional[str] = Field(
        default="https://aip.baidubce.com/rest/2.0/ocr/v1/multiple_invoice",
        description="OCR API端点"
    )
    
    # 大模型配置
    llm_provider: str = Field(default="deepseek", description="LLM提供商: doubao, deepseek, kimi, openrouter")
    llm_api_key: Optional[str] = Field(
        default=None,
        description="LLM API Key"
    )
    llm_model: str = Field(default="deepseek-chat", description="模型名称")
    llm_endpoint: Optional[str] = Field(
        default="https://api.deepseek.com/chat/completions",
        description="LLM API端点"
    )
    
    # 文件上传配置
    max_file_size: int = Field(default=10 * 1024 * 1024, description="最大文件大小(10MB)")
    upload_dir: str = Field(default="./uploads", description="上传目录")
    
    # 日志配置
    log_dir: str = Field(default="./logs", description="日志目录")
    log_level: str = Field(default="DEBUG", description="日志级别: DEBUG, INFO, WARNING, ERROR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 默认LLM端点配置
LLM_ENDPOINTS = {
    "doubao": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "kimi": "https://api.moonshot.cn/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
}

# 默认模型配置
DEFAULT_MODELS = {
    "doubao": "doubao-pro-32k",
    "deepseek": "deepseek-chat",
    "kimi": "moonshot-v1-8k",
    "openrouter": "deepseek/deepseek-chat",
}


def get_settings() -> Settings:
    """获取设置实例"""
    return Settings()

