"""数据模型定义"""
from pydantic import BaseModel, Field
from typing import Optional, List


class OCRConfig(BaseModel):
    """OCR配置"""
    provider: str = Field(default="baidu", description="OCR提供商: baidu, aliyun, tencent, generic")
    api_key: str = Field(description="API Key")
    secret_key: Optional[str] = Field(default=None, description="Secret Key (部分提供商需要)")
    endpoint: Optional[str] = Field(default=None, description="API端点 (可选)")


class LLMConfig(BaseModel):
    """大模型配置"""
    provider: str = Field(default="deepseek", description="LLM提供商: doubao, deepseek, kimi, openrouter")
    api_key: str = Field(description="API Key")
    model: Optional[str] = Field(default=None, description="模型名称")
    endpoint: Optional[str] = Field(default=None, description="API端点 (可选)")


class AppConfig(BaseModel):
    """应用配置"""
    ocr: Optional[OCRConfig] = None
    llm: Optional[LLMConfig] = None


class VoucherEntry(BaseModel):
    """凭证分录"""
    subject_code: str = Field(default="", description="科目编码")
    subject_name: str = Field(default="", description="科目名称")
    summary: str = Field(default="", description="凭证摘要")
    direction: str = Field(default="", description="借贷方向")
    amount: float = Field(default=0, description="金额")
    currency: str = Field(default="人民币", description="币种")
    exchange_rate: float = Field(default=1, description="汇率")
    original_amount: float = Field(default=0, description="原币金额")
    quantity: Optional[float] = Field(default=None, description="数量")
    unit_price: Optional[float] = Field(default=None, description="单价")
    settlement_method: str = Field(default="", description="结算方式名称")
    settlement_date: str = Field(default="", description="结算日期")
    settlement_no: str = Field(default="", description="结算票号")
    business_date: str = Field(default="", description="业务日期")
    employee_no: str = Field(default="", description="员工编号")
    employee_name: str = Field(default="", description="员工姓名")
    partner_no: str = Field(default="", description="往来单位编号")
    partner_name: str = Field(default="", description="往来单位名称")
    product_no: str = Field(default="", description="货品编号")
    product_name: str = Field(default="", description="货品名称")
    department: str = Field(default="", description="部门名称")
    project: str = Field(default="", description="项目名称")


class VoucherData(BaseModel):
    """凭证数据"""
    voucher_date: str = Field(default="", description="编制日期")
    voucher_type: str = Field(default="记", description="凭证类型")
    voucher_no: str = Field(default="", description="凭证号")
    preparer: str = Field(default="", description="制单人")
    attachment_count: int = Field(default=0, description="附件张数")
    fiscal_year: str = Field(default="", description="会计年度")
    entries: List[VoucherEntry] = Field(default_factory=list, description="分录列表")


class RecognitionResult(BaseModel):
    """识别结果"""
    success: bool = Field(description="是否成功")
    filename: str = Field(description="文件名")
    image_url: Optional[str] = Field(default=None, description="图片URL，用于显示缩略图")
    ocr_text: Optional[str] = Field(default=None, description="OCR识别的文本")
    voucher_data: Optional[dict] = Field(default=None, description="结构化凭证数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class BatchRecognitionResult(BaseModel):
    """批量识别结果"""
    total: int = Field(description="总数")
    success_count: int = Field(description="成功数")
    failed_count: int = Field(description="失败数")
    results: List[RecognitionResult] = Field(description="识别结果列表")


class SubjectInfo(BaseModel):
    """会计科目信息"""
    code: str = Field(description="科目编码")
    name: str = Field(description="科目名称")
    category: str = Field(description="科目类别")

