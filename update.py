import requests
import base64
import json
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")
HOST = os.environ.get("HOST", "gvm.cotco.dns-dynamic.net")
# ==========================================

PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 

def get_optimization_ip():
    url = 'https://api.hostmonit.com/get_optimization_ip'
    headers = {'Content-Type': 'application/json'}
    data = {"key": KEY, "type": "v4"}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"获取 IP 失败: {e}")
    return None

def main():
    res = get_optimization_ip()
    if not res or res.get("code") != 200:
        print("未能获取到 IP 数据")
        return

    # 生成北京时间时间戳 (UTC+8)
    utc_now = datetime.utcnow()
    beijing_time = (utc_now + timedelta(hours=8)).strftime("%H:%M")

    # 1. 汇总所有线路数据
    raw_ips = []
    lines_map = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    info_data = res.get("info", {})
    for code, name in lines_map.items():
        line_data = info_data.get(code, [])
        for item in line_data:
            item['line_name'] = name
            raw_ips.append(item)

    # 2. 根据延迟从小到大排序
    def sort_key(x):
        try:
            return int(x.get("latency", "999").replace("ms", ""))
        except:
            return 999

    sorted_ips = sorted(raw_ips, key=sort_key)

    # 3. 生成链接
    links = []
    for item in sorted_ips:
        ip = item.get("ip")
        name = item.get("line_name")
        colo = item.get("colo", "Unknown")
        latency = item.get("latency", "Unknown")
        
        if not ip:
            continue
        
        # 备注格式：线路_地区_延迟_时间 (例如: 移动_LAX_51ms_08:45)
        remark = f"{name}_{colo}_{latency}_{beijing_time}"
        
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)

    if not links:
        print("链接列表为空")
        return

    # 4. Base64 编码并保存
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    
    print(f"[{beijing_time}] 成功更新 sub.txt，节点已按延迟排序并添加时间戳。")

if __name__ == "__main__":
    main()
