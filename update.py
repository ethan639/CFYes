import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")
HOST = os.environ.get("HOST", "gvm.cotco.dns-dynamic.net")
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_data(ip_type='v4'):
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() 
    
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            continue

        info = res.get("info", {})
        # 严格按照：移动 -> 电信 排序
        # 由于联通 IP 与移动高度重合，去重后联通将自动消失
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
                
                # 别名：线路名_IP版本_地区_延迟ms_时间
                remark = f"{name}_{tag}_{colo}_{lat_raw}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 拼接内容并进行兼容性 Base64 编码
        content = "\n".join(all_links)
        encoded_str = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # 确保没有任何干扰导入的换行符
        final_content = encoded_str.replace('\n', '').replace('\r', '')
        
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"[{beijing_time}] 订阅更新成功，共 {len(all_links)} 个节点")

if __name__ == "__main__":
    main()
