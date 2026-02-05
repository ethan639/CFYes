import requests
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
# 建议在 GitHub Secrets 中设置 USER_ID 以保护安全
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
                
                # 别名格式匹配图 4: 线路_版本_地区_延迟_时间
                remark = f"{name}_{tag}_{colo}_{lat}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                # 构造 VLESS 链接
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 核心改动：不再进行 Base64 编码，直接保存明文链接
        # 这种方式 100% 避免了因编码换行导致的导入失败
        content = "\n".join(all_links).strip()
        
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[{beijing_time}] 成功生成 {len(all_links)} 个节点")
    else:
        print("未获取到节点数据")

if __name__ == "__main__":
    main()
