"""OCR服务 - 支持多种OCR提供商"""
import base64
import httpx
from typing import Optional
from abc import ABC, abstractmethod


class BaseOCRProvider(ABC):
    """OCR提供商基类"""
    
    @abstractmethod
    async def recognize(self, image_data: bytes) -> str:
        """识别图片中的文字"""
        pass


class BaiduOCRProvider(BaseOCRProvider):
    """百度OCR"""
    
    def __init__(self, api_key: str, secret_key: str, endpoint: Optional[str] = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.token_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.ocr_url = endpoint or "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        self.bank_receipt_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/bank_receipt_new"  # 银行回单专用接口
        self._access_token: Optional[str] = None
    
    async def _get_access_token(self) -> str:
        """获取百度API访问令牌"""
        if self._access_token:
            return self._access_token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.secret_key,
                }
            )
            result = response.json()
            self._access_token = result.get("access_token")
            return self._access_token
    
    async def recognize(self, image_data: bytes) -> str:
        """识别图片"""
        import logging
        import sys
        ocr_logger = logging.getLogger("ocr")
        
        # 记录调用的接口类型
        ocr_logger.info(f"调用百度OCR接口: {self.ocr_url}")
        # 同时打印到控制台，确保能看到
        print(f"[OCR] 调用百度OCR接口: {self.ocr_url}", file=sys.stderr)
        
        access_token = await self._get_access_token()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 百度OCR接口要求使用application/x-www-form-urlencoded格式
        # 根据文档，image参数需要：base64编码后进行urlencode
        # httpx 的 data 参数会自动进行 URL 编码，所以直接传入 dict 即可
        form_data = {
            "image": image_base64,
            "verify_parameter": "false",  # 是否返回校验参数
            "probability": "false",       # 是否返回识别结果中每一行的置信度
            "location": "false",          # 是否返回位置信息
        }
        
        # multiple_invoice 为主接口；当只返回分类结果（type=others 等）时，不在这里降级
        # 降级逻辑在后面的解析部分处理，根据type调用对应的专用接口（如bank_receipt_new）
        async with httpx.AsyncClient() as client:
            # 第一次调用：智能财务票据识别 multiple_invoice
            response = await client.post(
                self.ocr_url,
                params={"access_token": access_token},
                data=form_data,  # httpx 会自动进行 URL 编码
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            result = response.json()
            
        # 记录返回数据（用于调试）- 使用INFO级别确保能看到
        ocr_logger.info(f"百度OCR返回数据键: {list(result.keys()) if isinstance(result, dict) else '非字典'}")
        ocr_logger.info(f"百度OCR返回数据: {result}")
        # 同时打印到控制台，确保能看到
        print(f"[OCR] 返回数据键: {list(result.keys()) if isinstance(result, dict) else '非字典'}", file=sys.stderr)
        print(f"[OCR] 完整返回数据: {result}", file=sys.stderr)
        
        # 处理错误 - 百度OCR返回错误时通常包含error_code
        if "error_code" in result:
            error_msg = result.get("error_msg", "未知错误")
            error_code = result.get("error_code", "未知")
            ocr_logger.error(f"百度OCR API错误 - Code: {error_code}, Message: {error_msg}")
            ocr_logger.error(f"完整返回数据: {result}")
            raise Exception(f"百度OCR API错误: {error_msg} (错误码: {error_code})")
        
        # 如果返回数据为空或格式异常，也记录
        if not result:
            ocr_logger.error(f"百度OCR返回空数据")
            raise Exception("百度OCR返回空数据")
        
        # 提取文字 - 支持多种返回格式
        text_lines = []
        
        # 格式1: multiple_invoice格式 (words_result在顶层，包含result字段)
        if "words_result" in result:
            words_result = result.get("words_result", [])
            
            if not words_result:
                ocr_logger.warning("words_result为空")
            else:
                # 检查是否是multiple_invoice格式（包含result字段）
                # 根据文档，multiple_invoice接口返回的格式是：words_result数组中每个元素包含result字段
                first_item = words_result[0]
                if isinstance(first_item, dict) and "result" in first_item:
                    # multiple_invoice格式：从result字段中提取所有word
                    ocr_logger.info(f"检测到multiple_invoice格式，票据数量: {len(words_result)}")
                    for idx, invoice in enumerate(words_result):
                        invoice_type = invoice.get("type", "未知")
                        invoice_result = invoice.get("result", {})
                        ocr_logger.debug(f"处理票据 {idx+1}/{len(words_result)} - 类型: {invoice_type}")
                        
                        # 遍历result中的所有字段
                        for field_name, field_value in invoice_result.items():
                            if isinstance(field_value, list):
                                for item in field_value:
                                    if isinstance(item, dict) and "word" in item:
                                        word = item.get("word", "").strip()
                                        if word:  # 只添加非空文字
                                            text_lines.append(word)
                    ocr_logger.info(f"使用格式1 (multiple_invoice) - 从 {len(words_result)} 个票据中提取到 {len(text_lines)} 行文字")
                elif isinstance(first_item, dict) and "type" in first_item and "result" not in first_item:
                    # 如果只有type字段（如type="others"），说明是仅分类结果，没有具体内容
                    # 对于银行回单等类型，需要调用专门的接口
                    invoice_type = first_item.get("type", "未知")
                    ocr_logger.info(f"multiple_invoice返回仅分类结果(type={invoice_type})，尝试调用银行回单专用接口")
                    
                    # 调用银行回单专用接口
                    try:
                        bank_receipt_text = await self._recognize_bank_receipt(image_data)
                        if bank_receipt_text:
                            text_lines = bank_receipt_text.split("\n")
                            ocr_logger.info(f"银行回单接口识别成功，提取到 {len(text_lines)} 行文字")
                        else:
                            ocr_logger.warning("银行回单接口未识别到文字")
                    except Exception as e:
                        ocr_logger.error(f"银行回单接口调用失败: {str(e)}")
                        raise
                else:
                    # 标准accurate_basic格式：直接提取words字段
                    text_lines = [item.get("words", "") for item in words_result if item.get("words")]
                    ocr_logger.info(f"使用格式1 (accurate_basic) - 提取到 {len(text_lines)} 行文字")
        
        # 格式2: multiple_invoice格式 (可能有多个票据)
        elif "data" in result:
            data = result.get("data", {})
            ocr_logger.info(f"使用格式2 (multiple_invoice) - data类型: {type(data)}, data内容: {data}")
            
            # 如果是列表，遍历每个票据
            if isinstance(data, list):
                for idx, invoice in enumerate(data):
                    ocr_logger.info(f"处理票据 {idx+1}/{len(data)}: {invoice}")
                    # 提取每个票据的文字
                    if "words_result" in invoice:
                        words_result = invoice.get("words_result", [])
                        text_lines.extend([item.get("words", "") for item in words_result])
                    # 也可能在invoice的其他字段中
                    elif "words" in invoice:
                        text_lines.append(str(invoice.get("words", "")))
                ocr_logger.info(f"从 {len(data)} 个票据中提取到 {len(text_lines)} 行文字")
            # 如果是字典，直接提取
            elif isinstance(data, dict):
                ocr_logger.info(f"data是字典，键: {list(data.keys())}")
                if "words_result" in data:
                    words_result = data.get("words_result", [])
                    text_lines = [item.get("words", "") for item in words_result]
                    ocr_logger.info(f"从字典中提取到 {len(text_lines)} 行文字")
                # 尝试其他可能的字段
                elif "words" in data:
                    text_lines.append(str(data.get("words", "")))
        
        # 格式3: 通用格式，尝试提取所有文本字段
        if not text_lines:
            ocr_logger.info("尝试格式3 (通用格式) - 递归提取文本，返回数据完整结构: " + str(result)[:1000])
            # 递归提取所有可能的文本字段
            def extract_text(obj, texts, depth=0):
                if depth > 10:  # 防止无限递归
                    return
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        # 常见文本字段
                        if key in ["words", "word", "text", "content", "value", "name"] and isinstance(value, str) and value.strip():
                            texts.append(value)
                        elif isinstance(value, (dict, list)):
                            extract_text(value, texts, depth + 1)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_text(item, texts, depth + 1)
            
            extract_text(result, text_lines)
            ocr_logger.debug(f"通用格式提取到 {len(text_lines)} 行文字")
        
        # 如果还是没提取到，记录完整返回数据并抛出异常（方便调试）
        if not text_lines:
            error_info = {
                "message": "OCR未能提取到文字",
                "返回数据键": list(result.keys()) if isinstance(result, dict) else "非字典类型",
                "完整返回数据": result
            }
            ocr_logger.error(f"OCR提取失败: {error_info}")
            # 打印到控制台
            print(f"[OCR错误] 未能提取到文字", file=sys.stderr)
            print(f"[OCR错误] 返回数据: {result}", file=sys.stderr)
            # 抛出异常，包含完整返回数据，这样前端能看到实际返回内容
            raise Exception(f"OCR未能提取到文字。返回数据: {result}")
        
        result_text = "\n".join(text_lines) if text_lines else ""
        ocr_logger.info(f"OCR识别完成 - 提取文字长度: {len(result_text)}, 行数: {len(text_lines)}")
        
        return result_text
    
    async def _recognize_bank_receipt(self, image_data: bytes) -> str:
        """调用银行回单专用OCR接口"""
        import logging
        import sys
        from urllib.parse import urlencode
        ocr_logger = logging.getLogger("ocr")
        
        ocr_logger.info("调用银行回单专用OCR接口")
        print(f"[OCR] 调用银行回单专用接口: {self.bank_receipt_url}", file=sys.stderr)
        
        access_token = await self._get_access_token()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 银行回单接口参数（按照文档示例）
        form_data = {
            "image": image_base64,
            "probability": "false",
            "location": "false"
        }
        
        # 手动构建form data字符串（按照文档示例，使用urlencode）
        payload = urlencode(form_data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.bank_receipt_url,
                params={"access_token": access_token},
                content=payload.encode("utf-8"),  # 手动编码为bytes
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
            )
            result = response.json()
        
        ocr_logger.info(f"银行回单OCR返回数据: {result}")
        print(f"[OCR] 银行回单返回数据: {result}", file=sys.stderr)
        
        # 处理错误
        if "error_code" in result:
            error_msg = result.get("error_msg", "未知错误")
            error_code = result.get("error_code", "未知")
            ocr_logger.error(f"银行回单OCR API错误 - Code: {error_code}, Message: {error_msg}")
            raise Exception(f"银行回单OCR API错误: {error_msg} (错误码: {error_code})")
        
        # 提取文字 - 银行回单接口返回格式：words_result是字典，键是字段名，值是数组
        # 格式：{"words_result": {"标题": [{"word": "..."}], "付款人户名": [{"word": "..."}], ...}}
        text_lines = []
        if "words_result" in result:
            words_result = result.get("words_result", {})
            ocr_logger.info(f"银行回单OCR words_result类型: {type(words_result)}, 键: {list(words_result.keys())[:5] if isinstance(words_result, dict) else '非字典'}")
            
            # 根据文档，words_result是字典，键是字段名（如"标题"、"付款人户名"等），值是数组
            if isinstance(words_result, dict):
                for field_name, field_value in words_result.items():
                    if isinstance(field_value, list):
                        # 遍历数组中的每个元素
                        for item in field_value:
                            if isinstance(item, dict) and "word" in item:
                                word = item.get("word", "").strip()
                                if word:  # 只添加非空文字
                                    text_lines.append(word)
                            elif isinstance(item, str) and item.strip():
                                # 如果直接是字符串
                                text_lines.append(item.strip())
                    elif isinstance(field_value, str) and field_value.strip():
                        # 如果值直接是字符串
                        text_lines.append(field_value.strip())
            elif isinstance(words_result, list):
                # 兼容处理：如果是列表格式
                for item in words_result:
                    if isinstance(item, dict) and "word" in item:
                        word = item.get("word", "").strip()
                        if word:
                            text_lines.append(word)
                    elif isinstance(item, str) and item.strip():
                        text_lines.append(item.strip())
            
            ocr_logger.info(f"银行回单OCR提取到 {len(text_lines)} 行文字")
        
        return "\n".join(text_lines) if text_lines else ""


class AliyunOCRProvider(BaseOCRProvider):
    """阿里云OCR"""
    
    def __init__(self, api_key: str, secret_key: str = None, endpoint: Optional[str] = None):
        self.api_key = api_key
        self.ocr_url = endpoint or "https://ocrapi-advanced.taobao.com/ocrservice/advanced"
    
    async def recognize(self, image_data: bytes) -> str:
        """识别图片"""
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ocr_url,
                json={"img": image_base64},
                headers={
                    "Authorization": f"APPCODE {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            result = response.json()
        
        # 提取文字
        if "prism_wordsInfo" in result:
            text_lines = [item.get("word", "") for item in result["prism_wordsInfo"]]
            return "\n".join(text_lines)
        return result.get("content", "")


class TencentOCRProvider(BaseOCRProvider):
    """腾讯云OCR"""
    
    def __init__(self, api_key: str, secret_key: str, endpoint: Optional[str] = None):
        self.secret_id = api_key
        self.secret_key = secret_key
        self.endpoint = endpoint or "ocr.tencentcloudapi.com"
    
    async def recognize(self, image_data: bytes) -> str:
        """识别图片"""
        import hashlib
        import hmac
        import json
        import time
        from datetime import datetime
        
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 腾讯云签名较复杂，这里简化处理
        timestamp = int(time.time())
        date = datetime.utcnow().strftime("%Y-%m-%d")
        
        payload = json.dumps({"ImageBase64": image_base64})
        
        # 构建规范请求
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json\nhost:{self.endpoint}\nx-tc-action:generalbasicOCR\n"
        signed_headers = "content-type;host;x-tc-action"
        hashed_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
        
        # 构建签名字符串
        algorithm = "TC3-HMAC-SHA256"
        credential_scope = f"{date}/ocr/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
        
        # 计算签名
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
        
        secret_date = sign(("TC3" + self.secret_key).encode("utf-8"), date)
        secret_service = sign(secret_date, "ocr")
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        
        # 构建授权头
        authorization = f"{algorithm} Credential={self.secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self.endpoint}",
                content=payload,
                headers={
                    "Authorization": authorization,
                    "Content-Type": "application/json",
                    "Host": self.endpoint,
                    "X-TC-Action": "GeneralBasicOCR",
                    "X-TC-Version": "2018-11-19",
                    "X-TC-Timestamp": str(timestamp),
                }
            )
            result = response.json()
        
        # 提取文字
        response_data = result.get("Response", {})
        text_detections = response_data.get("TextDetections", [])
        text_lines = [item.get("DetectedText", "") for item in text_detections]
        return "\n".join(text_lines)


class GenericOCRProvider(BaseOCRProvider):
    """通用OCR提供商 - 支持任意兼容的OCR API"""
    
    def __init__(self, api_key: str, secret_key: str = None, endpoint: str = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.endpoint = endpoint
    
    async def recognize(self, image_data: bytes) -> str:
        """识别图片 - 通用实现"""
        if not self.endpoint:
            raise ValueError("通用OCR需要配置endpoint")
        
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint,
                json={"image": image_base64},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            result = response.json()
        
        # 尝试从常见字段提取文字
        if "text" in result:
            return result["text"]
        if "result" in result:
            if isinstance(result["result"], str):
                return result["result"]
            if isinstance(result["result"], list):
                return "\n".join(str(item) for item in result["result"])
        
        return str(result)


class OCRService:
    """OCR服务管理器"""
    
    PROVIDERS = {
        "baidu": BaiduOCRProvider,
        "aliyun": AliyunOCRProvider,
        "tencent": TencentOCRProvider,
        "generic": GenericOCRProvider,
    }
    
    def __init__(
        self,
        provider: str = "baidu",
        api_key: str = None,
        secret_key: str = None,
        endpoint: str = None,
    ):
        self.provider_name = provider
        self.api_key = api_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self._provider: Optional[BaseOCRProvider] = None
    
    def _get_provider(self) -> BaseOCRProvider:
        """获取OCR提供商实例"""
        if self._provider is None:
            provider_class = self.PROVIDERS.get(self.provider_name, GenericOCRProvider)
            self._provider = provider_class(
                api_key=self.api_key,
                secret_key=self.secret_key,
                endpoint=self.endpoint,
            )
        return self._provider
    
    async def recognize(self, image_data: bytes) -> str:
        """识别图片中的文字"""
        provider = self._get_provider()
        return await provider.recognize(image_data)
    
    def update_config(
        self,
        provider: str = None,
        api_key: str = None,
        secret_key: str = None,
        endpoint: str = None,
    ):
        """更新配置"""
        if provider:
            self.provider_name = provider
        if api_key:
            self.api_key = api_key
        if secret_key:
            self.secret_key = secret_key
        if endpoint:
            self.endpoint = endpoint
        # 重置provider实例以应用新配置
        self._provider = None

