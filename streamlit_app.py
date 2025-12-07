"""李会计凭证识别系统 - Streamlit应用"""
import streamlit as st
import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import List, Optional
import pandas as pd
from io import BytesIO

# 添加backend目录到路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# 导入后端模块
from app.config import get_settings
from app.services import OCRService, LLMService, ExcelService
from app.data import get_subjects_list

# 页面配置
st.set_page_config(
    page_title="李会计凭证识别系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 密码常量
APP_PASSWORD = "li123456"

# 初始化session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "ocr_service" not in st.session_state:
    st.session_state.ocr_service = None
if "llm_service" not in st.session_state:
    st.session_state.llm_service = None
if "recognition_results" not in st.session_state:
    st.session_state.recognition_results = []
if "ocr_config" not in st.session_state:
    # 从localStorage加载（通过session state模拟）
    try:
        # 尝试从环境变量或默认位置读取
        pass
    except:
        st.session_state.ocr_config = {}
if "llm_config" not in st.session_state:
    st.session_state.llm_config = {}

# 密码验证
def check_password():
    """检查密码"""
    if st.session_state.authenticated:
        return True
    
    with st.container():
        st.title("🔒 李会计凭证识别系统")
        st.markdown("---")
        
        password = st.text_input("请输入密码", type="password", key="password_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("验证", type="primary", use_container_width=True):
                if password == APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("密码错误，请重新输入")
        
        return False

# 主应用
def main():
    """主应用"""
    # 检查密码
    if not check_password():
        return
    
    # 侧边栏导航
    with st.sidebar:
        st.title("📄 李会计凭证识别")
        st.markdown("---")
        
        page = st.radio(
            "选择功能",
            ["上传凭证", "识别结果", "API配置"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 服务状态
        st.subheader("服务状态")
        ocr_status = "✅ 已配置" if st.session_state.ocr_service else "❌ 未配置"
        llm_status = "✅ 已配置" if st.session_state.llm_service else "❌ 未配置"
        st.write(f"OCR服务: {ocr_status}")
        st.write(f"大模型服务: {llm_status}")
    
    # 根据选择显示不同页面
    if page == "上传凭证":
        upload_page()
    elif page == "识别结果":
        result_page()
    elif page == "API配置":
        config_page()

def upload_page():
    """上传凭证页面"""
    st.title("📤 上传凭证")
    
    # 检查配置
    if not st.session_state.ocr_service or not st.session_state.llm_service:
        st.warning("⚠️ 请先在「API配置」页面配置OCR服务和大模型服务")
        return
    
    st.markdown("---")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "选择凭证图片",
        type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
        accept_multiple_files=True,
        help="支持批量上传，每批最多10张图片"
    )
    
    if uploaded_files:
        st.info(f"已选择 {len(uploaded_files)} 个文件")
        
        # 显示文件列表（缩略图）
        cols = st.columns(min(5, len(uploaded_files)))
        for idx, file in enumerate(uploaded_files[:5]):
            with cols[idx % 5]:
                st.image(file, use_container_width=True)
                st.caption(file.name)
        
        if len(uploaded_files) > 5:
            st.caption(f"... 还有 {len(uploaded_files) - 5} 个文件")
    
    # 开始识别按钮
    if st.button("🚀 开始识别", type="primary", disabled=not uploaded_files):
        if uploaded_files:
            recognize_files(uploaded_files)

def recognize_files(files: List):
    """识别文件"""
    BATCH_SIZE = 10
    batches = [files[i:i+BATCH_SIZE] for i in range(0, len(files), BATCH_SIZE)]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_results = []
    
    for batch_idx, batch in enumerate(batches):
        status_text.text(f"正在处理第 {batch_idx + 1}/{len(batches)} 批，共 {len(batch)} 张图片...")
        progress_bar.progress(batch_idx / len(batches))
        
        for file_idx, file in enumerate(batch):
            try:
                # 读取文件
                file_bytes = file.read()
                
                # OCR识别（异步）
                with st.spinner(f"OCR识别中: {file.name}..."):
                    ocr_text = asyncio.run(st.session_state.ocr_service.recognize(file_bytes))
                
                if not ocr_text or not ocr_text.strip():
                    all_results.append({
                        "success": False,
                        "filename": file.name,
                        "error": "OCR未识别到任何文字"
                    })
                    continue
                
                # LLM结构化（异步）
                with st.spinner(f"AI分析中: {file.name}..."):
                    voucher_data = asyncio.run(
                        st.session_state.llm_service.recognize_voucher(ocr_text)
                    )
                
                all_results.append({
                    "success": True,
                    "filename": file.name,
                    "ocr_text": ocr_text,
                    "voucher_data": voucher_data
                })
                
            except Exception as e:
                all_results.append({
                    "success": False,
                    "filename": file.name,
                    "error": str(e)
                })
        
        progress_bar.progress((batch_idx + 1) / len(batches))
    
    status_text.text("✅ 所有批次处理完成！")
    progress_bar.progress(1.0)
    
    # 保存结果
    st.session_state.recognition_results = all_results
    
    # 切换到结果页面
    st.success(f"识别完成！成功: {sum(1 for r in all_results if r['success'])}, 失败: {sum(1 for r in all_results if not r['success'])}")
    st.info("请切换到「识别结果」页面查看详情")

def result_page():
    """识别结果页面"""
    st.title("📊 识别结果")
    
    results = st.session_state.recognition_results
    
    if not results:
        st.info("暂无识别结果，请先上传凭证图片进行识别")
        return
    
    st.markdown("---")
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总计", len(results))
    with col2:
        success_count = sum(1 for r in results if r.get("success"))
        st.metric("成功", success_count, delta=f"{success_count/len(results)*100:.1f}%")
    with col3:
        failed_count = len(results) - success_count
        st.metric("失败", failed_count)
    with col4:
        total_entries = sum(len(r.get("voucher_data", {}).get("entries", [])) for r in results if r.get("success"))
        st.metric("分录总数", total_entries)
    
    st.markdown("---")
    
    # 导出Excel按钮
    if success_count > 0:
        if st.button("📥 导出Excel", type="primary"):
            export_excel(results)
    
    # 结果表格
    st.subheader("识别结果列表")
    
    # 准备表格数据
    table_data = []
    for idx, result in enumerate(results):
        voucher_data = result.get("voucher_data", {})
        entries = voucher_data.get("entries", [])
        
        table_data.append({
            "序号": idx + 1,
            "文件名": result["filename"],
            "状态": "✅ 成功" if result.get("success") else "❌ 失败",
            "凭证日期": voucher_data.get("voucher_date", "-"),
            "凭证类型": voucher_data.get("voucher_type", "-"),
            "分录数": len(entries),
            "错误信息": result.get("error", "-")
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 详情展示
    st.markdown("---")
    st.subheader("凭证详情")
    
    selected_idx = st.selectbox("选择要查看的凭证", range(len(results)), format_func=lambda x: results[x]["filename"])
    
    if selected_idx is not None:
        result = results[selected_idx]
        
        if result.get("success"):
            voucher_data = result.get("voucher_data", {})
            
            # 基本信息
            col1, col2 = st.columns(2)
            with col1:
                st.write("**凭证日期:**", voucher_data.get("voucher_date", "-"))
                st.write("**凭证类型:**", voucher_data.get("voucher_type", "-"))
                st.write("**凭证号:**", voucher_data.get("voucher_no", "-"))
            with col2:
                st.write("**制单人:**", voucher_data.get("preparer", "-"))
                st.write("**附件张数:**", voucher_data.get("attachment_count", 0))
                st.write("**会计年度:**", voucher_data.get("fiscal_year", "-"))
            
            # 分录明细
            entries = voucher_data.get("entries", [])
            if entries:
                st.subheader("分录明细")
                entries_df = pd.DataFrame(entries)
                st.dataframe(entries_df, use_container_width=True, hide_index=True)
            
            # OCR原文
            if result.get("ocr_text"):
                with st.expander("查看OCR识别原文"):
                    st.text(result["ocr_text"])
        else:
            st.error(f"识别失败: {result.get('error', '未知错误')}")

def export_excel(results: List):
    """导出Excel"""
    try:
        # 收集所有成功的凭证数据
        vouchers = []
        for result in results:
            if result.get("success") and result.get("voucher_data"):
                vouchers.append(result["voucher_data"])
        
        if not vouchers:
            st.error("没有可导出的凭证数据")
            return
        
        # 生成Excel
        excel_service = ExcelService()
        excel_bytes = excel_service.generate_excel(vouchers)
        
        # 下载
        st.download_button(
            label="📥 下载Excel文件",
            data=excel_bytes,
            file_name=f"凭证导出_{time.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )
        
    except Exception as e:
        st.error(f"导出失败: {str(e)}")

def config_page():
    """API配置页面"""
    st.title("⚙️ API配置")
    
    st.info("💡 只需填写API Key，其他配置使用系统默认值")
    
    st.markdown("---")
    
    # OCR配置
    st.subheader("🔍 OCR服务配置（百度OCR）")
    
    ocr_api_key = st.text_input("API Key", type="password", key="ocr_api_key", value=st.session_state.ocr_config.get("api_key", ""))
    ocr_secret_key = st.text_input("Secret Key", type="password", key="ocr_secret_key", value=st.session_state.ocr_config.get("secret_key", ""))
    
    if st.button("💾 保存OCR配置", key="save_ocr"):
        if ocr_api_key and ocr_secret_key:
            try:
                st.session_state.ocr_service = OCRService(
                    provider="baidu",
                    api_key=ocr_api_key,
                    secret_key=ocr_secret_key,
                    endpoint=None  # 使用默认值
                )
                st.session_state.ocr_config = {
                    "api_key": ocr_api_key,
                    "secret_key": ocr_secret_key
                }
                st.success("✅ OCR配置保存成功")
            except Exception as e:
                st.error(f"配置失败: {str(e)}")
        else:
            st.warning("请填写完整的API Key和Secret Key")
    
    st.markdown("---")
    
    # LLM配置
    st.subheader("🤖 大模型服务配置（DeepSeek）")
    
    llm_api_key = st.text_input("API Key", type="password", key="llm_api_key", value=st.session_state.llm_config.get("api_key", ""))
    
    if st.button("💾 保存大模型配置", key="save_llm"):
        if llm_api_key:
            try:
                st.session_state.llm_service = LLMService(
                    provider="deepseek",
                    api_key=llm_api_key,
                    model=None,  # 使用默认值
                    endpoint=None  # 使用默认值
                )
                st.session_state.llm_config = {
                    "api_key": llm_api_key
                }
                st.success("✅ 大模型配置保存成功")
            except Exception as e:
                st.error(f"配置失败: {str(e)}")
        else:
            st.warning("请填写API Key")
    
    st.markdown("---")
    
    # API获取说明
    with st.expander("📖 API获取说明"):
        st.markdown("""
        ### OCR服务
        - **百度OCR**: 访问 [百度智能云](https://cloud.baidu.com/product/ocr) 创建应用获取API Key和Secret Key
        
        ### 大模型服务
        - **DeepSeek**: 访问 [DeepSeek开放平台](https://platform.deepseek.com/) 获取API Key
        """)

if __name__ == "__main__":
    main()

