"""API路由"""
import os
import json
import time
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
import io

from ..models import (
    OCRConfig,
    LLMConfig,
    AppConfig,
    RecognitionResult,
    BatchRecognitionResult,
    SubjectInfo,
)
from ..services import OCRService, LLMService, ExcelService
from ..data import get_subjects_list, ACCOUNTING_SUBJECTS
from ..utils.logger import get_logger, get_ocr_logger, get_llm_logger

logger = get_logger(__name__)
ocr_logger = get_ocr_logger()
llm_logger = get_llm_logger()

router = APIRouter()

# 全局服务实例（使用global关键字以便在main.py中修改）
ocr_service: Optional[OCRService] = None
llm_service: Optional[LLMService] = None
excel_service = ExcelService()

# 当前配置存储
current_config: dict = {
    "ocr": None,
    "llm": None,
}


def get_ocr_service() -> OCRService:
    """获取OCR服务实例"""
    global ocr_service
    if ocr_service is None:
        raise HTTPException(status_code=400, detail="请先配置OCR服务")
    return ocr_service


def get_llm_service() -> LLMService:
    """获取LLM服务实例"""
    global llm_service
    if llm_service is None:
        raise HTTPException(status_code=400, detail="请先配置大模型服务")
    return llm_service


# ============ 配置相关API ============

@router.post("/config/ocr", summary="配置OCR服务")
async def configure_ocr(config: OCRConfig):
    """配置OCR服务（只接收key，其他使用默认值）"""
    global ocr_service, current_config
    from ..config import get_settings
    
    settings = get_settings()
    
    try:
        # 使用默认值或配置值（如果前端传了None或空字符串，使用默认值）
        provider = config.provider if (config.provider and config.provider.strip()) else settings.ocr_provider
        endpoint = config.endpoint if (config.endpoint and config.endpoint.strip()) else settings.ocr_endpoint
        
        ocr_service = OCRService(
            provider=provider,
            api_key=config.api_key,
            secret_key=config.secret_key,
            endpoint=endpoint,
        )
        
        current_config["ocr"] = {
            "provider": provider,
            "api_key": config.api_key,
            "secret_key": config.secret_key,
            "endpoint": endpoint,
        }
        
        logger.info(f"OCR服务配置成功 - Provider: {provider}")
        ocr_logger.info(f"OCR配置更新 - Provider: {provider}, Endpoint: {endpoint or 'default'}")
        
        return {"message": "OCR配置成功", "provider": provider}
    except Exception as e:
        logger.error(f"OCR配置失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR配置失败: {str(e)}")


@router.post("/config/llm", summary="配置大模型服务")
async def configure_llm(config: LLMConfig):
    """配置大模型服务（只接收key，其他使用默认值）"""
    global llm_service, current_config
    from ..config import get_settings, LLM_ENDPOINTS, DEFAULT_MODELS
    
    settings = get_settings()
    
    try:
        # 使用默认值或配置值（如果前端传了None或空字符串，使用默认值）
        provider = config.provider if (config.provider and config.provider.strip()) else settings.llm_provider
        model = config.model if (config.model and config.model.strip()) else (DEFAULT_MODELS.get(provider) or settings.llm_model)
        endpoint = config.endpoint if (config.endpoint and config.endpoint.strip()) else (LLM_ENDPOINTS.get(provider) or settings.llm_endpoint)
        
        llm_service = LLMService(
            provider=provider,
            api_key=config.api_key,
            model=model,
            endpoint=endpoint,
        )
        
        current_config["llm"] = {
            "provider": provider,
            "api_key": config.api_key,
            "model": model,
            "endpoint": endpoint,
        }
        
        logger.info(f"大模型服务配置成功 - Provider: {provider}, Model: {llm_service.model}")
        llm_logger.info(
            f"LLM配置更新 - Provider: {provider}, Model: {llm_service.model}, "
            f"Endpoint: {llm_service.endpoint or 'default'}"
        )
        
        return {
            "message": "大模型配置成功",
            "provider": provider,
            "model": llm_service.model,
            "endpoint": llm_service.endpoint,
        }
    except Exception as e:
        logger.error(f"大模型配置失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"大模型配置失败: {str(e)}")


@router.get("/config", summary="获取当前配置")
async def get_config():
    """获取当前配置（隐藏敏感信息）"""
    result = {}
    
    if current_config["ocr"]:
        ocr_conf = current_config["ocr"].copy()
        if ocr_conf.get("api_key"):
            ocr_conf["api_key"] = ocr_conf["api_key"][:8] + "****"
        if ocr_conf.get("secret_key"):
            ocr_conf["secret_key"] = ocr_conf["secret_key"][:8] + "****"
        result["ocr"] = ocr_conf
    
    if current_config["llm"]:
        llm_conf = current_config["llm"].copy()
        if llm_conf.get("api_key"):
            llm_conf["api_key"] = llm_conf["api_key"][:8] + "****"
        result["llm"] = llm_conf
    
    return result


# ============ 识别相关API ============

@router.post("/recognize/single", response_model=RecognitionResult, summary="识别单张凭证")
async def recognize_single(file: UploadFile = File(...)):
    """
    识别单张凭证图片
    
    1. 调用OCR识别图片文字
    2. 调用大模型提取结构化数据
    """
    start_time = time.time()
    ocr = get_ocr_service()
    llm = get_llm_service()
    
    logger.info(f"开始识别单张凭证 - 文件名: {file.filename}, 大小: {file.size} bytes")
    
    try:
        # 读取文件
        image_data = await file.read()
        
        # 保存文件到uploads目录（用于后续显示缩略图）
        from ..config import get_settings
        settings = get_settings()
        import uuid
        # 生成唯一文件名，避免重名
        file_ext = os.path.splitext(file.filename or '')[-1] or '.jpg'
        saved_filename = f"{uuid.uuid4().hex}{file_ext}"
        saved_path = os.path.join(settings.upload_dir, saved_filename)
        with open(saved_path, 'wb') as f:
            f.write(image_data)
        logger.debug(f"文件已保存: {saved_filename}")
        
        # OCR识别
        ocr_start = time.time()
        ocr_logger.info(f"开始OCR识别 - 文件: {file.filename}, 大小: {len(image_data)} bytes")
        ocr_text = await ocr.recognize(image_data)
        ocr_time = time.time() - ocr_start
        ocr_logger.info(f"OCR识别完成 - 文件: {file.filename}, 耗时: {ocr_time:.2f}s, 识别文字长度: {len(ocr_text)}")
        
        if not ocr_text.strip():
            logger.warning(f"OCR未识别到文字 - 文件: {file.filename}")
            return RecognitionResult(
                success=False,
                filename=file.filename,
                image_url=f"/uploads/{saved_filename}",
                error="OCR未识别到任何文字",
            )
        
        # 大模型提取结构化数据
        llm_start = time.time()
        llm_logger.info(f"开始LLM识别 - 文件: {file.filename}, OCR文本长度: {len(ocr_text)}")
        voucher_data = await llm.recognize_voucher(ocr_text)
        llm_time = time.time() - llm_start
        llm_logger.info(f"LLM识别完成 - 文件: {file.filename}, 耗时: {llm_time:.2f}s")
        
        if "error" in voucher_data:
            logger.error(f"LLM识别失败 - 文件: {file.filename}, 错误: {voucher_data['error']}")
            return RecognitionResult(
                success=False,
                filename=file.filename,
                image_url=f"/uploads/{saved_filename}",
                ocr_text=ocr_text,
                error=voucher_data["error"],
            )
        
        total_time = time.time() - start_time
        entries_count = len(voucher_data.get("entries", []))
        logger.info(
            f"凭证识别成功 - 文件: {file.filename}, 分录数: {entries_count}, "
            f"总耗时: {total_time:.2f}s (OCR: {ocr_time:.2f}s, LLM: {llm_time:.2f}s)"
        )
        
        return RecognitionResult(
            success=True,
            filename=file.filename,
            image_url=f"/uploads/{saved_filename}",
            ocr_text=ocr_text,
            voucher_data=voucher_data,
        )
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(
            f"凭证识别失败 - 文件: {file.filename}, 错误: {str(e)}, 耗时: {total_time:.2f}s",
            exc_info=True
        )
        # 尝试保存文件（如果还没有保存）
        saved_filename = None
        try:
            from ..config import get_settings
            settings = get_settings()
            import uuid
            file_ext = os.path.splitext(file.filename or '')[-1] or '.jpg'
            saved_filename = f"{uuid.uuid4().hex}{file_ext}"
            saved_path = os.path.join(settings.upload_dir, saved_filename)
            # 重新读取文件（因为之前已经read过了）
            await file.seek(0)
            image_data = await file.read()
            with open(saved_path, 'wb') as f:
                f.write(image_data)
        except Exception:
            pass
        
        return RecognitionResult(
            success=False,
            filename=file.filename,
            image_url=f"/uploads/{saved_filename}" if saved_filename else None,
            error=str(e),
        )


@router.post("/recognize/batch", response_model=BatchRecognitionResult, summary="批量识别凭证")
async def recognize_batch(files: List[UploadFile] = File(...)):
    """
    批量识别凭证图片
    """
    start_time = time.time()
    ocr = get_ocr_service()
    llm = get_llm_service()
    
    logger.info(f"开始批量识别 - 文件数量: {len(files)}")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for idx, file in enumerate(files, 1):
            file_start = time.time()
            logger.info(f"处理文件 [{idx}/{len(files)}] - {file.filename}")
            
            try:
                # 读取文件
                image_data = await file.read()
                
                # 保存文件到uploads目录（用于后续显示缩略图）
                from ..config import get_settings
                settings = get_settings()
                import uuid
                # 生成唯一文件名，避免重名
                file_ext = os.path.splitext(file.filename or '')[-1] or '.jpg'
                saved_filename = f"{uuid.uuid4().hex}{file_ext}"
                saved_path = os.path.join(settings.upload_dir, saved_filename)
                with open(saved_path, 'wb') as f:
                    f.write(image_data)
                logger.debug(f"文件已保存: {saved_filename}")
                
                # OCR识别
                ocr_start = time.time()
                ocr_logger.info(f"[批量 {idx}/{len(files)}] OCR识别 - 文件: {file.filename}")
                try:
                    ocr_text = await ocr.recognize(image_data)
                except Exception as ocr_error:
                    # OCR识别失败，记录详细错误信息
                    error_msg = str(ocr_error)
                    logger.error(f"[批量 {idx}/{len(files)}] OCR识别异常 - {file.filename}, 错误: {error_msg}", exc_info=True)
                    # 即使失败也保存文件，方便查看
                    saved_filename = None
                    try:
                        from ..config import get_settings
                        settings = get_settings()
                        import uuid
                        file_ext = os.path.splitext(file.filename or '')[-1] or '.jpg'
                        saved_filename = f"{uuid.uuid4().hex}{file_ext}"
                        saved_path = os.path.join(settings.upload_dir, saved_filename)
                        with open(saved_path, 'wb') as f:
                            f.write(image_data)
                    except Exception as save_error:
                        logger.warning(f"保存文件失败: {save_error}")
                    
                    results.append(RecognitionResult(
                        success=False,
                        filename=file.filename,
                        image_url=f"/uploads/{saved_filename}" if saved_filename else None,
                        error=f"OCR识别失败: {error_msg}",
                    ))
                    failed_count += 1
                    continue
                
                ocr_time = time.time() - ocr_start
                ocr_logger.info(f"[批量 {idx}/{len(files)}] OCR完成 - 文件: {file.filename}, 耗时: {ocr_time:.2f}s, 文字长度: {len(ocr_text)}")
                
                if not ocr_text.strip():
                    logger.warning(f"[批量 {idx}/{len(files)}] OCR未识别到文字 - {file.filename}")
                    results.append(RecognitionResult(
                        success=False,
                        filename=file.filename,
                        image_url=f"/uploads/{saved_filename}",
                        error="OCR未识别到任何文字",
                    ))
                    failed_count += 1
                    continue
                
                # 大模型提取结构化数据
                llm_start = time.time()
                llm_logger.info(f"[批量 {idx}/{len(files)}] LLM识别 - 文件: {file.filename}")
                voucher_data = await llm.recognize_voucher(ocr_text)
                llm_time = time.time() - llm_start
                llm_logger.info(f"[批量 {idx}/{len(files)}] LLM完成 - 文件: {file.filename}, 耗时: {llm_time:.2f}s")
                
                if "error" in voucher_data:
                    logger.error(f"[批量 {idx}/{len(files)}] LLM识别失败 - {file.filename}, 错误: {voucher_data['error']}")
                    results.append(RecognitionResult(
                        success=False,
                        filename=file.filename,
                        image_url=f"/uploads/{saved_filename}",
                        ocr_text=ocr_text,
                        error=voucher_data["error"],
                    ))
                    failed_count += 1
                else:
                    entries_count = len(voucher_data.get("entries", []))
                    file_time = time.time() - file_start
                    logger.info(
                        f"[批量 {idx}/{len(files)}] 识别成功 - {file.filename}, "
                        f"分录数: {entries_count}, 耗时: {file_time:.2f}s"
                    )
                    results.append(RecognitionResult(
                        success=True,
                        filename=file.filename,
                        image_url=f"/uploads/{saved_filename}",
                        ocr_text=ocr_text,
                        voucher_data=voucher_data,
                    ))
                    success_count += 1
                    
            except Exception as e:
                file_time = time.time() - file_start
                logger.error(
                    f"[批量 {idx}/{len(files)}] 识别失败 - {file.filename}, 错误: {str(e)}, 耗时: {file_time:.2f}s",
                    exc_info=True
                )
                results.append(RecognitionResult(
                    success=False,
                    filename=file.filename,
                    error=str(e),
                ))
                failed_count += 1
    
    total_time = time.time() - start_time
    logger.info(
        f"批量识别完成 - 总数: {len(files)}, 成功: {success_count}, 失败: {failed_count}, "
        f"总耗时: {total_time:.2f}s, 平均: {total_time/len(files):.2f}s/文件"
    )
    
    return BatchRecognitionResult(
        total=len(files),
        success_count=success_count,
        failed_count=failed_count,
        results=results,
    )


# ============ Excel导出API ============

@router.post("/export/excel", summary="导出Excel")
async def export_excel(vouchers: List[dict]):
    """
    将识别结果导出为Excel
    
    Args:
        vouchers: 凭证数据列表
    """
    excel_data = excel_service.generate_excel(vouchers)
    
    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=vouchers.xlsx"
        }
    )


@router.get("/export/template", summary="下载Excel模板")
async def download_template():
    """下载空白Excel模板"""
    excel_data = excel_service.generate_template()
    
    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=template.xlsx"
        }
    )


# ============ 会计科目API ============

@router.get("/subjects", response_model=List[SubjectInfo], summary="获取会计科目列表")
async def get_subjects():
    """获取所有会计科目"""
    return get_subjects_list()


@router.get("/subjects/{code}", summary="根据编码获取科目")
async def get_subject_by_code(code: str):
    """根据科目编码获取科目信息"""
    if code in ACCOUNTING_SUBJECTS:
        return {
            "code": code,
            "name": ACCOUNTING_SUBJECTS[code],
        }
    raise HTTPException(status_code=404, detail="科目不存在")


# ============ 健康检查 ============

@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查"""
    return {
        "status": "healthy",
        "ocr_configured": ocr_service is not None,
        "llm_configured": llm_service is not None,
    }

