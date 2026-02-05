import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
# 恢复使用您指定的原始域名
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
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"请求 {ip_ver} 失败: {e}")
    return None

def main():
    # 生成北京时间用于节点重命名
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() # 自动过滤移动/联通重复 IP
    
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
                
                # 别名格式：线路_版本_地区_延迟_时间
                remark = f"{name}_{tag}_{colo}_{lat_raw}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                # 构造 VLESS 链接，保持 sni 和 host 为原域名
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 1. 先拼接所有链接并去除首尾空白
        content = "\n".join(all_links).strip()
        # 2. Base64 编码
        encoded_bytes = base64.b64encode(content.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        # 3. 核心修复：彻底剔除所有换行符和回车符，这是解决“导入失败”的关键
        final_content = encoded_str.replace('\n', '').replace('\r', '').strip()
        
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"[{beijing_time}] 订阅已生成，包含 {len(all_links)} 个节点")
    else:
        print("未获取到数据")

if __name__ == "__main__":
    main()
