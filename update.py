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
        response = requests.post(url, json=data, timeout=15)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def main():
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    
    # 按照 v4, v6 顺序抓取
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            continue
            
        info = res.get("info", {})
        # 严格按照：移动 -> 联通 -> 电信 顺序
        for code, name in [("CM", "移动"), ("CU", "联通"), ("CT", "电信")]:
            line_data = info.get(code, [])
            # 组内按延迟排序
            sorted_data = sorted(line_data, key=lambda x: int(x.get("latency", "999").replace("ms", "")) if "ms" in x.get("latency", "") else 999)
            
            for item in sorted_data:
                ip = item.get("ip")
                colo = item.get("colo", "Default")
                lat = item.get("latency", "Unknown")
                if not ip: continue
                
                # 别名格式优化
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                remark = f"{tag}_{name}_{colo}_{lat}_{beijing_time}"
                link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode("\n".join(all_links).encode()).decode())
        print(f"成功更新 {len(all_links)} 个节点")

if __name__ == "__main__":
    main()
