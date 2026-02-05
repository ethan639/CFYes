import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
# 1. 你的 UUID
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")

# 2. 目标域名（HOST/SNI），保留您的原始设置
HOST = "gvm.cotco.dns-dynamic.net" 

# 3. 接口配置
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_data(ip_type='v4'):
    """获取优选 IP 数据"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API 请求失败 ({ip_type}): {e}")
    return None

def main():
    # 生成北京时间后缀
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() # 用于 IP 去重
    
    # 抓取 IPv4 和 IPv6 优选 IP
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            continue

        info = res.get("info", {})
        # 严格顺序：移动(CM) -> 电信(CT)
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
                lat_raw = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                
                # 构造节点名称
                remark = f"{name}_{tag}_{colo}_{lat_raw}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                # 拼接标准 VLESS 链接
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 1. 拼接明文内容
        content = "\n".join(all_links).strip()
        
        # 2. Base64 编码
        encoded_str = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # 3. 【终极修复】彻底移除编码后字符串中所有的换行 (\n)、回车 (\r) 和空格
        # 这一步是为了解决图 10/11/12 中“导入订阅内容失败”的关键
        final_content = "".join(encoded_str.split())
        
        # 4. 写入文件
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(final_content)
            
        print(f"[{beijing_time}] 更新成功！共生成 {len(all_links)} 个节点。")
    else:
        print("未获取到有效节点数据。")

if __name__ == "__main__":
    main()
