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
    # 生成北京时间时间戳 (UTC+8)
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    
    # 按照 v4, v6 顺序处理
    for ip_ver in ['v4', 'v6']:
        print(f"--- 正在处理 {ip_ver} 数据 ---")
        res = get_data(ip_ver)
        
        info = {}
        if res and res.get("code") == 200:
            info = res.get("info", {})
        else:
            print(f"警告: {ip_ver} API 获取失败")

        # 优化逻辑：删除联通(CU)，仅保留移动(CM)和电信(CT)
        # 排序：移动 -> 电信
        target_lines = [("CM", "移动"), ("CT", "电信")]
        
        for code, name in target_lines:
            # 兼容大小写 Key
            line_data = info.get(code) or info.get(code.upper()) or info.get(code.lower())
            
            if not line_data or not isinstance(line_data, list):
                print(f"[-] {ip_ver} {name}: 无数据")
                continue
            
            print(f"[+] {ip_ver} {name}: 抓取到 {len(line_data)} 个 IP")
            
            for item in line_data:
                ip = item.get("ip")
                if not ip: continue
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                
                # 格式化延迟：确保带 ms
                lat_raw = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                lat_display = f"{lat_raw}ms"
                
                # 别名格式：线路名_IP版本_地区_延迟ms_时间
                remark = f"{name}_{tag}_{colo}_{lat_display}_{beijing_time}"
                
                # IPv6 适配
                address = f"[{ip}]" if ":" in ip else ip
                
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        content = "\n".join(all_links)
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))
        print(f"[{beijing_time}] 同步完成，已移除联通重复线路，剩余 {len(all_links)} 个节点")
    else:
        print("致命错误: 未抓取到任何数据")

if __name__ == "__main__":
    main()
