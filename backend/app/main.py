"""李会计凭证识别系统 - 主应用"""
import os
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .api import router
from .config import get_settings
from .utils.logger import setup_logging, get_logger, get_request_logger

settings = get_settings()

# 初始化日志
setup_logging(log_dir=settings.log_dir, log_level=settings.log_level)
logger = get_logger(__name__)
request_logger = get_request_logger()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="李会计凭证OCR识别与Excel导出系统",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 请求日志中间件
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求信息
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        
        request_logger.info(
            f"[{method}] {path}?{query_params} - IP: {client_ip} - "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录响应信息
            status_code = response.status_code
            request_logger.info(
                f"[{method}] {path} - Status: {status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {method} {path} - Error: {str(e)} - "
                f"Time: {process_time:.3f}s",
                exc_info=True
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "内部服务器错误"}
            )

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 配置CORS（允许前端跨域访问）
# 从环境变量读取允许的源，支持多个域名
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")

if allowed_origins_env:
    # 生产环境：使用环境变量配置的域名
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    # 开发环境：允许所有来源
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(router, prefix="/api", tags=["李会计凭证识别"])

# 确保上传目录和日志目录存在
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.log_dir, exist_ok=True)

# 挂载静态文件服务（用于访问上传的图片）
# 注意：在生产环境中，建议使用Nginx等Web服务器来提供静态文件服务
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# 自动初始化OCR和LLM服务（使用默认配置）
@app.on_event("startup")
async def startup_event():
    """应用启动时自动初始化服务"""
    from app.services import OCRService, LLMService
    from app.api import routes
    
    # 初始化OCR服务（如果配置了默认值）
    if settings.ocr_api_key and settings.ocr_secret_key:
        try:
            routes.ocr_service = OCRService(
                provider=settings.ocr_provider,
                api_key=settings.ocr_api_key,
                secret_key=settings.ocr_secret_key,
                endpoint=settings.ocr_endpoint,
            )
            routes.current_config["ocr"] = {
                "provider": settings.ocr_provider,
                "api_key": settings.ocr_api_key,
                "secret_key": settings.ocr_secret_key,
                "endpoint": settings.ocr_endpoint,
            }
            logger.info(f"OCR服务已自动初始化 - Provider: {settings.ocr_provider}")
        except Exception as e:
            logger.warning(f"OCR服务自动初始化失败: {str(e)}")
    
    # 初始化LLM服务（如果配置了默认值）
    if settings.llm_api_key:
        try:
            routes.llm_service = LLMService(
                provider=settings.llm_provider,
                api_key=settings.llm_api_key,
                model=settings.llm_model,
                endpoint=settings.llm_endpoint,
            )
            routes.current_config["llm"] = {
                "provider": settings.llm_provider,
                "api_key": settings.llm_api_key,
                "model": settings.llm_model,
                "endpoint": settings.llm_endpoint,
            }
            logger.info(f"LLM服务已自动初始化 - Provider: {settings.llm_provider}, Model: {settings.llm_model}")
        except Exception as e:
            logger.warning(f"LLM服务自动初始化失败: {str(e)}")

# 启动日志
logger.info("=" * 50)
logger.info(f"启动 {settings.app_name}")
logger.info(f"日志级别: {settings.log_level}")
logger.info(f"日志目录: {settings.log_dir}")
logger.info(f"上传目录: {settings.upload_dir}")
logger.info("=" * 50)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "李会计凭证识别系统",
        "docs": "/api/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

