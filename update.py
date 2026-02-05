import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
# 优先从 GitHub Secrets 读取，若无则使用默认值
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
        print(f"请求 {ip_type} 失败: {e}")
    return None

def main():
    # 生成北京时间时间戳 (UTC+8)
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() # 用于全局 IP 去重
    
    # 按照 IPv4, IPv6 顺序处理
    for ip_ver in ['v4', 'v6']:
        print(f"正在处理 {ip_ver}...")
        res = get_data(ip_ver)
        
        if not res or res.get("code") != 200:
            print(f"警告: {ip_ver} API 返回异常")
            continue

        info = res.get("info", {})
        
        # 严格线路顺序：移动 -> 电信 (联通 IP 将通过去重逻辑自动过滤)
        for code, name in [("CM", "移动"), ("CT", "电信")]:
            line_data = info.get(code) or info.get(code.lower())
            
            if not line_data or not isinstance(line_data, list):
                continue
            
            for item in line_data:
                ip = item.get("ip")
                
                # 全局去重逻辑：如果该 IP 已出现过（不论哪个运营商），则跳过
                if not ip or ip in seen_ips:
                    continue
                
                seen_ips.add(ip)
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                
                # 格式化延迟：确保带有 ms 单位
                lat_raw = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                lat_display = f"{lat_raw}ms"
                
                # 最终别名格式：移动_IPv4_LAX_51ms_08:45
                remark = f"{name}_{tag}_{colo}_{lat_display}_{beijing_time}"
                
                # IPv6 地址自动加方括号
                address = f"[{ip}]" if ":" in ip else ip
                
                # 拼接 VLESS 链接
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # Base64 编码输出，与图 20 格式一致
        content = "\n".join(all_links)
        encoded_data = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(encoded_data)
        print(f"[{beijing_time}] 同步完成，共保留 {len(all_links)} 个唯一节点。")
    else:
        print("错误: 未抓取到有效数据")

if __name__ == "__main__":
    main()
