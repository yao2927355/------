"""会计科目表数据"""

# 常用会计科目表
ACCOUNTING_SUBJECTS = {
    # 一、资产类
    "1001": "库存现金",
    "1002": "银行存款",
    "1101": "交易性金融资产",
    "1121": "应收票据",
    "1122": "应收账款",
    "1123": "预付账款",
    "1131": "应收股利",
    "1221": "其他应收款",
    "1231": "坏账准备",
    "1401": "材料采购",
    "1402": "在途物资",
    "1403": "原材料",
    "1404": "材料成本差异",
    "1405": "库存商品",
    "1411": "周转材料",
    "1471": "存货跌价准备",
    "1511": "长期股权投资",
    "1512": "长期股权投资减值准备",
    "1601": "固定资产",
    "1602": "累计折旧",
    "1603": "固定资产减值准备",
    "1604": "在建工程",
    "1606": "固定资产清理",
    "1701": "无形资产",
    "1702": "累计摊销",
    "1703": "无形资产减值准备",
    "1801": "长期待摊费用",
    "1901": "待处理财产损溢",
    
    # 二、负债类
    "2001": "短期借款",
    "2201": "应付票据",
    "2202": "应付账款",
    "2203": "预收账款",
    "2211": "应付职工薪酬",
    "2221": "应交税费",
    "2231": "应付利息",
    "2232": "应付股利",
    "2241": "其他应付款",
    "2501": "长期借款",
    "2502": "应付债券",
    "2701": "长期应付款",
    "2801": "预计负债",
    "2901": "递延收益",
    
    # 三、所有者权益类
    "4001": "实收资本",
    "4002": "资本公积",
    "4101": "盈余公积",
    "4103": "本年利润",
    "4104": "利润分配",
    "4201": "其他综合收益",
    
    # 四、成本类
    "5001": "生产成本",
    "5101": "制造费用",
    
    # 五、损益类
    "6001": "主营业务收入",
    "6051": "其他业务收入",
    "6101": "公允价值变动损益",
    "6111": "投资收益",
    "6301": "营业外收入",
    "6401": "主营业务成本",
    "6402": "其他业务成本",
    "6403": "营业税金及附加",
    "6601": "销售费用",
    "6602": "管理费用",
    "6603": "财务费用",
    "6701": "资产减值损失",
    "6711": "营业外支出",
    "6801": "所得税费用",
}

# 按名称查找的反向映射
SUBJECTS_BY_NAME = {v: k for k, v in ACCOUNTING_SUBJECTS.items()}

# 科目类别
SUBJECT_CATEGORIES = {
    "1": "资产类",
    "2": "负债类",
    "4": "所有者权益类",
    "5": "成本类",
    "6": "损益类",
}


def get_subject_code(name: str) -> str | None:
    """根据科目名称获取科目编码"""
    # 精确匹配
    if name in SUBJECTS_BY_NAME:
        return SUBJECTS_BY_NAME[name]
    
    # 模糊匹配
    for subject_name, code in SUBJECTS_BY_NAME.items():
        if name in subject_name or subject_name in name:
            return code
    
    return None


def get_subject_name(code: str) -> str | None:
    """根据科目编码获取科目名称"""
    return ACCOUNTING_SUBJECTS.get(code)


def match_subject(text: str) -> tuple[str | None, str | None]:
    """
    根据文本匹配会计科目
    返回 (科目编码, 科目名称)
    """
    # 先尝试作为编码匹配
    if text in ACCOUNTING_SUBJECTS:
        return text, ACCOUNTING_SUBJECTS[text]
    
    # 再尝试作为名称匹配
    code = get_subject_code(text)
    if code:
        return code, ACCOUNTING_SUBJECTS[code]
    
    return None, None


def get_all_subjects() -> dict:
    """获取所有会计科目"""
    return ACCOUNTING_SUBJECTS.copy()


def get_subjects_list() -> list[dict]:
    """获取会计科目列表（用于前端展示）"""
    return [
        {"code": code, "name": name, "category": SUBJECT_CATEGORIES.get(code[0], "未知")}
        for code, name in ACCOUNTING_SUBJECTS.items()
    ]

