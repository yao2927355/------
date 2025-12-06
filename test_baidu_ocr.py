#!/usr/bin/env python3
"""测试百度OCR接口"""
import base64
import httpx
import json
import sys

API_KEY = "H9rBK2VvMzYcjZsqsiz3DlYC"
SECRET_KEY = "xeY6MF0X3NMuIN8UWVJnwnYYXHwJKcaA"
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/multiple_invoice"
TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"


async def get_access_token():
    """获取访问令牌"""
    print("正在获取访问令牌...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": API_KEY,
                "client_secret": SECRET_KEY,
            }
        )
        result = response.json()
        if "access_token" in result:
            print(f"✓ 获取token成功: {result['access_token'][:20]}...")
            return result["access_token"]
        else:
            print(f"✗ 获取token失败: {result}")
            return None


async def test_ocr_with_url(image_url: str):
    """使用图片URL测试OCR（按照文档示例）"""
    print(f"\n使用图片URL: {image_url}")
    
    # 获取token
    access_token = await get_access_token()
    if not access_token:
        return
    
    # 按照文档示例，使用url参数
    from urllib.parse import urlencode
    form_data = {
        "url": image_url,
        "verify_parameter": "false",
        "probability": "false",
        "location": "false"
    }
    
    # 手动构建form data字符串（按照文档示例）
    payload = urlencode(form_data)
    print(f"✓ 请求参数: {payload[:100]}...")
    
    print(f"\n正在调用OCR接口: {OCR_URL}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OCR_URL,
                params={"access_token": access_token},
                content=payload.encode("utf-8"),  # 手动编码
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
            print(f"响应大小: {len(response.content)} bytes")
            
            result = response.json()
            
            print("\n" + "="*60)
            print("返回数据:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("="*60)
            
            # 检查错误
            if "error_code" in result:
                print(f"\n✗ OCR调用失败!")
                print(f"错误码: {result.get('error_code')}")
                print(f"错误信息: {result.get('error_msg')}")
                return False
            
            # 检查返回数据结构
            print(f"\n返回数据键: {list(result.keys())}")
            
            # 尝试提取文字
            text_lines = []
            
            # 格式1: words_result在顶层
            if "words_result" in result:
                words_result = result.get("words_result", [])
                text_lines = [item.get("words", "") for item in words_result]
                print(f"\n✓ 使用格式1 (accurate_basic) - 提取到 {len(text_lines)} 行文字")
            
            # 格式2: data字段
            elif "data" in result:
                data = result.get("data", {})
                print(f"\n✓ 使用格式2 (multiple_invoice) - data类型: {type(data)}")
                
                if isinstance(data, list):
                    for idx, invoice in enumerate(data):
                        if "words_result" in invoice:
                            words_result = invoice.get("words_result", [])
                            text_lines.extend([item.get("words", "") for item in words_result])
                    print(f"从 {len(data)} 个票据中提取到 {len(text_lines)} 行文字")
                elif isinstance(data, dict):
                    if "words_result" in data:
                        words_result = data.get("words_result", [])
                        text_lines = [item.get("words", "") for item in words_result]
                    print(f"从字典中提取到 {len(text_lines)} 行文字")
            
            if text_lines:
                print(f"\n✓ OCR识别成功! 提取到 {len(text_lines)} 行文字")
                print("\n识别文字内容:")
                print("-" * 60)
                for i, line in enumerate(text_lines[:20], 1):  # 只显示前20行
                    print(f"{i:2d}. {line}")
                if len(text_lines) > 20:
                    print(f"... (还有 {len(text_lines) - 20} 行)")
                print("-" * 60)
                return True
            else:
                print(f"\n✗ 未能提取到文字")
                return False
                
        except Exception as e:
            print(f"\n✗ 请求异常: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_ocr_with_image_file(image_path: str):
    """使用图片文件测试OCR"""
    print(f"\n正在读取图片: {image_path}")
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        print(f"✓ 图片大小: {len(image_data)} bytes")
    except Exception as e:
        print(f"✗ 读取图片失败: {e}")
        return
    
    # 获取token
    access_token = await get_access_token()
    if not access_token:
        return
    
    # Base64编码
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    print(f"✓ Base64编码长度: {len(image_base64)}")
    
    # 准备请求数据
    form_data = {
        "image": image_base64,
        "verify_parameter": "false",
        "probability": "false",
        "location": "false"
    }
    
    print(f"\n正在调用OCR接口: {OCR_URL}")
    print(f"请求参数: verify_parameter=false, probability=false, location=false")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OCR_URL,
                params={"access_token": access_token},
                data=form_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
            print(f"响应大小: {len(response.content)} bytes")
            
            result = response.json()
            
            print("\n" + "="*60)
            print("返回数据:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("="*60)
            
            # 检查错误
            if "error_code" in result:
                print(f"\n✗ OCR调用失败!")
                print(f"错误码: {result.get('error_code')}")
                print(f"错误信息: {result.get('error_msg')}")
                return False
            
            # 检查返回数据结构
            print(f"\n返回数据键: {list(result.keys())}")
            
            # 尝试提取文字
            text_lines = []
            
            # 格式1: words_result在顶层
            if "words_result" in result:
                words_result = result.get("words_result", [])
                text_lines = [item.get("words", "") for item in words_result]
                print(f"\n✓ 使用格式1 (accurate_basic) - 提取到 {len(text_lines)} 行文字")
            
            # 格式2: data字段
            elif "data" in result:
                data = result.get("data", {})
                print(f"\n✓ 使用格式2 (multiple_invoice) - data类型: {type(data)}")
                
                if isinstance(data, list):
                    for idx, invoice in enumerate(data):
                        if "words_result" in invoice:
                            words_result = invoice.get("words_result", [])
                            text_lines.extend([item.get("words", "") for item in words_result])
                    print(f"从 {len(data)} 个票据中提取到 {len(text_lines)} 行文字")
                elif isinstance(data, dict):
                    if "words_result" in data:
                        words_result = data.get("words_result", [])
                        text_lines = [item.get("words", "") for item in words_result]
                    print(f"从字典中提取到 {len(text_lines)} 行文字")
            
            if text_lines:
                print(f"\n✓ OCR识别成功! 提取到 {len(text_lines)} 行文字")
                print("\n识别文字内容:")
                print("-" * 60)
                for i, line in enumerate(text_lines[:20], 1):  # 只显示前20行
                    print(f"{i:2d}. {line}")
                if len(text_lines) > 20:
                    print(f"... (还有 {len(text_lines) - 20} 行)")
                print("-" * 60)
                return True
            else:
                print(f"\n✗ 未能提取到文字")
                return False
                
        except Exception as e:
            print(f"\n✗ 请求异常: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python test_baidu_ocr.py <图片路径>     # 使用本地图片文件")
        print("  python test_baidu_ocr.py --url <图片URL>  # 使用图片URL")
        print("\n示例:")
        print("  python test_baidu_ocr.py test_image.jpg")
        print("  python test_baidu_ocr.py --url https://baidu-ai.bj.bcebos.com/ocr/vat_invoice.jpeg")
        sys.exit(1)
    
    if sys.argv[1] == "--url" and len(sys.argv) >= 3:
        image_url = sys.argv[2]
        await test_ocr_with_url(image_url)
    else:
        image_path = sys.argv[1]
        await test_ocr_with_image_file(image_path)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

