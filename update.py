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
    except Exception as e:
        print(f"请求 {ip_type} 出错: {e}")
    return None

def main():
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    
    # 建立全局去重集合
    seen_ips = set()
    
    # 按照 v4, v6 顺序处理
    for ip_ver in ['v4', 'v6']:
        print(f"--- 正在处理 {ip_ver} 数据 ---")
        res = get_data(ip_ver)
        
        if not res or res.get("code") != 200:
            print(f"警告: {ip_ver} 数据获取失败")
            continue

        info = res.get("info", {})
        
        # 严格顺序：移动 -> 电信 (已移除联通)
        target_lines = [("CM", "移动"), ("CT", "电信")]
        
        for code, name in target_lines:
            line_data = info.get(code) or info.get(code.lower())

            if not line_data or not isinstance(line_data, list):
                print(f"[-] {ip_ver} {name}: 无新数据")
                continue
            
            count_before = len(all_links)
            for item in line_data:
                ip = item.get("ip")
                
                # 核心去重：如果 IP 已经出现过，直接跳过
                if not ip or ip in seen_ips:
                    continue
                
                seen_ips.add(ip)
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                lat_raw = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                lat_display = f"{lat_raw}ms"
                
                # 别名格式：线路名_IP版本_地区_延迟ms_时间
                remark = f"{name}_{tag}_{colo}_{lat_display}_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)
            
            print(f"[+] {ip_ver} {name}: 有效新增 {len(all_links) - count_before} 个 IP")

    if all_links:
        content = "\n".join(all_links)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(encoded_content)
        print(f"[{beijing_time}] 更新成功：去重后保留 {len(all_links)} 个唯一 IP 节点。")
    else:
        print("错误：未抓取到有效数据。")

if __name__ == "__main__":
    main()
