import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
# 1. 你的 UUID
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")

# 2. 你的原始域名（HOST/SNI）
HOST = "gvm.cotco.dns-dynamic.net" 

# 3. API 密钥与固定参数
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_data(ip_type='v4'):
    """从 API 获取最新的优选 IP 数据"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        # 增加超时处理确保脚本不会因 API 响应慢而卡死
        response = requests.post(url, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"获取 {ip_type} 数据失败: {e}")
    return None

def main():
    # 生成当前北京时间后缀，用于在 v2rayN 列表中核对同步状态
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() # 用于全局去重，确保 100% 节点纯净度
    
    # 依次处理 IPv4 和 IPv6 
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            continue

        info = res.get("info", {})
        # 按照 移动 -> 电信 的优先顺序进行同步抓取
        for code, name in [("CM", "移动"), ("CT", "电信")]:
            line_data = info.get(code) or info.get(code.lower())
            if not line_data or not isinstance(line_data, list):
                continue
            
            for item in line_data:
                ip = item.get("ip")
                if not ip or ip in seen_ips:
                    continue
                seen_ips.add(ip) 
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                lat_raw = str(item.get("latency", "0")).lower().replace("ms", "")
                
                # 节点别名增加时间戳，如果 v2rayN 备注时间更新，则代表同步成功
                remark = f"{name}_{tag}_{colo}_{lat_raw}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                # 构造符合 V2Ray 标准的 VLESS 链接
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 1. 拼接原始链接内容
        content = "\n".join(all_links).strip()
        
        # 2. Base64 编码处理
        encoded_str = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # 3. 【100% 同步修复】彻底移除编码字符串中所有的换行、回车和不可见字符
        # 这是解决 v2rayN “获取内容成功但导入失败”的核心，只有导入成功，IP 才会更新
        final_content = "".join(encoded_str.split())
        
        # 4. 强制以 UTF-8 无 BOM 格式写入文件
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(final_content)
            
        print(f"[{beijing_time}] 同步成功！已抓取 {len(all_links)} 个实时优选节点。")
    else:
        print("警告：API 未返回数据，请检查网络或 API Key 状态。")

if __name__ == "__main__":
    main()
