"""大模型服务 - 支持豆包、DeepSeek、Kimi、OpenRouter等"""
import httpx
import json
from typing import Optional
from ..data import ACCOUNTING_SUBJECTS, match_subject


# 凭证识别提示词模板
VOUCHER_RECOGNITION_PROMPT = """你是一个专业的财务凭证识别助手。请根据OCR识别的凭证文本内容，提取并整理成结构化的财务凭证数据。

## 会计科目表（请严格按照此表匹配科目编码和名称）：
{subjects_table}

## OCR识别的凭证内容：
{ocr_text}

## 请按照以下JSON格式输出识别结果（可能有多条分录，请全部提取）：
```json
{{
    "voucher_date": "编制日期，格式YYYY-MM-DD",
    "voucher_type": "凭证类型，如：记账凭证、收款凭证、付款凭证、转账凭证",
    "voucher_no": "凭证号",
    "preparer": "制单人",
    "attachment_count": "附件张数，数字",
    "fiscal_year": "会计年度，如202511",
    "entries": [
        {{
            "subject_code": "科目编码，必须从会计科目表中匹配",
            "subject_name": "科目名称，必须从会计科目表中匹配",
            "summary": "凭证摘要",
            "direction": "借贷方向，借或贷",
            "amount": "金额，数字",
            "currency": "币种，默认人民币",
            "exchange_rate": "汇率，默认1",
            "original_amount": "原币金额，数字",
            "quantity": "数量，数字或空",
            "unit_price": "单价，数字或空",
            "settlement_method": "结算方式名称",
            "settlement_date": "结算日期",
            "settlement_no": "结算票号",
            "business_date": "业务日期",
            "employee_no": "员工编号",
            "employee_name": "员工姓名",
            "partner_no": "往来单位编号",
            "partner_name": "往来单位名称",
            "product_no": "货品编号",
            "product_name": "货品名称",
            "department": "部门名称",
            "project": "项目名称"
        }}
    ]
}}
```

## 注意事项：
1. 科目编码和科目名称必须严格匹配上面提供的会计科目表
2. 如果凭证中的科目名称与科目表不完全匹配，请选择最接近的科目
3. 金额必须是数字，不要包含货币符号
4. 如果某个字段无法识别，请填写空字符串
5. 借贷方向只能是"借"或"贷"
6. 请确保借贷金额平衡

只输出JSON，不要输出其他内容。"""


def build_subjects_table() -> str:
    """构建会计科目表字符串"""
    lines = []
    for code, name in sorted(ACCOUNTING_SUBJECTS.items()):
        lines.append(f"{code}: {name}")
    return "\n".join(lines)


class LLMService:
    """大模型服务"""
    
    # 默认端点配置
    DEFAULT_ENDPOINTS = {
        "doubao": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "deepseek": "https://api.deepseek.com/chat/completions",
        "kimi": "https://api.moonshot.cn/v1/chat/completions",
        "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    }
    
    # 默认模型配置
    DEFAULT_MODELS = {
        "doubao": "ep-20241210123456-abcde",  # 需要替换为实际的endpoint_id
        "deepseek": "deepseek-chat",
        "kimi": "moonshot-v1-8k",
        "openrouter": "deepseek/deepseek-chat",
    }
    
    def __init__(
        self,
        provider: str = "deepseek",
        api_key: str = None,
        model: str = None,
        endpoint: str = None,
    ):
        self.provider = provider
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODELS.get(provider, "deepseek-chat")
        self.endpoint = endpoint or self.DEFAULT_ENDPOINTS.get(provider)
    
    async def _call_api(self, messages: list[dict]) -> str:
        """调用大模型API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        # OpenRouter需要额外的headers
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://voucher-recognition.app"
            headers["X-Title"] = "李会计凭证识别"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,  # 低温度以获得更稳定的输出
            "max_tokens": 4096,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
        
        # 提取回复内容
        return result["choices"][0]["message"]["content"]
    
    async def recognize_voucher(self, ocr_text: str) -> dict:
        """识别凭证内容并返回结构化数据"""
        subjects_table = build_subjects_table()
        
        prompt = VOUCHER_RECOGNITION_PROMPT.format(
            subjects_table=subjects_table,
            ocr_text=ocr_text,
        )
        
        messages = [
            {"role": "system", "content": "你是一个专业的财务凭证识别助手，擅长从OCR文本中提取结构化的财务数据。"},
            {"role": "user", "content": prompt},
        ]
        
        response_text = await self._call_api(messages)
        
        # 解析JSON响应
        try:
            # 尝试提取JSON块
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            voucher_data = json.loads(json_str)
            
            # 验证并修正科目编码
            voucher_data = self._validate_and_fix_subjects(voucher_data)
            
            return voucher_data
            
        except json.JSONDecodeError as e:
            return {
                "error": f"解析LLM响应失败: {str(e)}",
                "raw_response": response_text,
            }
    
    def _validate_and_fix_subjects(self, voucher_data: dict) -> dict:
        """验证并修正科目编码和名称"""
        entries = voucher_data.get("entries", [])
        
        for entry in entries:
            subject_code = entry.get("subject_code", "")
            subject_name = entry.get("subject_name", "")
            
            # 尝试匹配科目
            if subject_code and subject_code in ACCOUNTING_SUBJECTS:
                # 科目编码正确，确保名称也正确
                entry["subject_name"] = ACCOUNTING_SUBJECTS[subject_code]
            elif subject_name:
                # 尝试通过名称匹配
                matched_code, matched_name = match_subject(subject_name)
                if matched_code:
                    entry["subject_code"] = matched_code
                    entry["subject_name"] = matched_name
        
        return voucher_data
    
    def update_config(
        self,
        provider: str = None,
        api_key: str = None,
        model: str = None,
        endpoint: str = None,
    ):
        """更新配置"""
        if provider:
            self.provider = provider
            # 如果更换了provider但没有指定endpoint，使用默认值
            if not endpoint:
                self.endpoint = self.DEFAULT_ENDPOINTS.get(provider)
            if not model:
                self.model = self.DEFAULT_MODELS.get(provider)
        if api_key:
            self.api_key = api_key
        if model:
            self.model = model
        if endpoint:
            self.endpoint = endpoint

