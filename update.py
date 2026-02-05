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
            res_json = response.json()
            if res_json.get("code") == 200:
                return res_json
    except:
        pass
    return None

def safe_int_latency(latency_val):
    if latency_val is None: return 999
    s = str(latency_val).lower().replace("ms", "").strip()
    try:
        return int(float(s))
    except:
        return 999

def main():
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set()
    
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res: continue
            
        info = res.get("info", {})
        # 严格顺序：移动 -> 联通 -> 电信
        for code, name in [("CM", "移动"), ("CU", "联通"), ("CT", "电信")]:
            line_data = info.get(code, [])
            if not isinstance(line_data, list): continue
            
            # 过滤掉延迟异常的数据（如 0ms 或 超过 1000ms）
            valid_data = [item for item in line_data if 0 < safe_int_latency(item.get("latency")) < 1000]
            sorted_data = sorted(valid_data, key=lambda x: safe_int_latency(x.get("latency", 999)))
            
            for item in sorted_data:
                ip = item.get("ip")
                if not ip or ip in seen_ips: continue
                
                seen_ips.add(ip)
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                lat_val = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                
                # 别名格式：线路_IP版本_地区_延迟ms_时间
                remark = f"{name}_{tag}_{colo}_{lat_val}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                # 构造节点
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        content = "\n".join(all_links)
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))
        print(f"[{beijing_time}] 更新完成：去重后保留 {len(all_links)} 个节点")

if __name__ == "__main__":
    main()
