import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")
HOST = "gvm.cotco.dns-dynamic.net" 
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_data(ip_type='v4'):
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, timeout=20)
        return response.json() if response.status_code == 200 else None
    except: return None

def main():
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() 
    
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200: continue
        info = res.get("info", {})

        for code, name in [("CM", "移动"), ("CT", "电信")]:
            line_data = info.get(code) or info.get(code.lower())
            if not line_data or not isinstance(line_data, list): continue
            
            for item in line_data:
                ip = item.get("ip")
                if not ip or ip in seen_ips: continue
                seen_ips.add(ip) 
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                lat = str(item.get("latency", "0")).lower().replace("ms", "")
                
                remark = f"{name}_{tag}_{colo}_{lat}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 核心：确保内容是纯粹的一行且没有任何尾部空格
        content = "\n".join(all_links).strip()
        # 编码并彻底清除所有换行符
        encoded_str = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        final_content = "".join(encoded_str.split()) # 终极手段：移除所有空白符
        
        # 使用 'wb' 模式写入，防止 Python 自动添加系统换行符
        with open("sub.txt", "wb") as f:
            f.write(final_content.encode('utf-8'))
        print(f"[{beijing_time}] 生成成功，节点数: {len(all_links)}")
