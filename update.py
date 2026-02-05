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

def safe_int_latency(latency_str):
    """安全地将延迟字符串转换为整数，解决图13中的TypeError"""
    if isinstance(latency_str, int):
        return latency_str
    try:
        # 移除 'ms' 并转换
        return int(str(latency_str).lower().replace("ms", "").strip())
    except:
        return 999

def main():
    # 获取北京时间
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    
    # 按照 v4, v6 顺序处理
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            continue
            
        info = res.get("info", {})
        # 严格按照图中顺序：移动 -> 联通 -> 电信
        for code, name in [("CM", "移动"), ("CU", "联通"), ("CT", "电信")]:
            line_data = info.get(code, [])
            if not isinstance(line_data, list):
                continue
            
            # 组内排序：由低到高
            sorted_data = sorted(line_data, key=lambda x: safe_int_latency(x.get("latency", 999)))
            
            for item in sorted_data:
                ip = item.get("ip")
                colo = item.get("colo", "Default")
                lat = item.get("latency", "Unknown")
                if not ip: continue
                
                # 节点备注格式
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                remark = f"{tag}_{name}_{colo}_{lat}_{beijing_time}"
                
                # 构造符合 v2rayN 规范的 VLESS 链接
                link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 进行最终的 Base64 编码导出
        content = "\n".join(all_links)
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))
        print(f"[{beijing_time}] 成功同步 {len(all_links)} 个节点到 sub.txt")

if __name__ == "__main__":
    main()
