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
        print("未能获取到数据")
        return

    # 生成北京时间时间戳 (UTC+8)
    utc_now = datetime.utcnow()
    beijing_time = (utc_now + timedelta(hours=8)).strftime("%H:%M")

    # 1. 定义线路抓取顺序 (匹配图中：移动 -> 联通 -> 电信)
    lines_order = [
        ("CM", "移动"),
        ("CU", "联通"),
        ("CT", "电信")
    ]
    
    info_data = res.get("info", {})
    links = []

    # 2. 核心逻辑：按线路顺序循环，每组内部单独按延迟排序
    for code, name in lines_order:
        line_data = info_data.get(code, [])
        
        # 定义内部排序规则：延迟由低到高
        def sort_latency(x):
            try:
                return int(x.get("latency", "999").replace("ms", ""))
            except:
                return 999
        
        # 对当前线路内部进行排序
        sorted_line_data = sorted(line_data, key=sort_latency)

        # 3. 生成该线路的 VLESS 链接
        for item in sorted_line_data:
            ip = item.get("ip")
            colo = item.get("colo", "Unknown")
            latency = item.get("latency", "Unknown")
            
            if not ip:
                continue
            
            # 备注格式：线路_地区_延迟_时间
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
    
    print(f"[{beijing_time}] 成功更新 sub.txt！顺序已匹配图中列表：移动->联通->电信。")

if __name__ == "__main__":
    main()
