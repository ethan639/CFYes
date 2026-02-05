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

def get_optimization_data(ip_type='v4'):
    """从 API 获取指定类型的优选数据 (v4 或 v6)"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    headers = {'Content-Type': 'application/json'}
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"获取 {ip_type} 数据失败: {e}")
    return None

def process_data(res, ip_type_label, beijing_time):
    """处理数据并生成链接列表"""
    if not res or res.get("code") != 200:
        return []

    lines_order = [("CM", "移动"), ("CU", "联通"), ("CT", "电信")]
    info_data = res.get("info", {})
    temp_links = []

    for code, name in lines_order:
        line_data = info_data.get(code, [])
        # 组内按延迟排序
        sorted_data = sorted(line_data, key=lambda x: int(x.get("latency", "999").replace("ms", "")) if "ms" in x.get("latency", "") else 999)

        for item in sorted_data:
            ip = item.get("ip")
            colo = item.get("colo", "Default")
            latency = item.get("latency", "Unknown")
            if not ip: continue
            
            # 格式：IPv4_移动_LAX_53ms_08:45 或 IPv6_电信_Default_3ms_08:45
            remark = f"{ip_type_label}_{name}_{colo}_{latency}_{beijing_time}"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            temp_links.append(link)
    return temp_links

def main():
    # 生成北京时间时间戳
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    
    # 分别获取 v4 和 v6 数据
    print("正在抓取 IPv4 数据...")
    res_v4 = get_optimization_data('v4')
    print("正在抓取 IPv6 数据...")
    res_v6 = get_optimization_data('v6')

    # 按照顺序合并：先 v4 列表，后 v6 列表
    all_links = []
    all_links.extend(process_data(res_v4, "IPv4", beijing_time))
    all_links.extend(process_data(res_v6, "IPv6", beijing_time))

    if not all_links:
        print("未获取到任何有效节点")
        return

    # Base64 编码并保存
    combined = "\n".join(all_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    
    print(f"[{beijing_time}] 成功更新 sub.txt！包含 {len(all_links)} 个节点 (v4+v6)。")

if __name__ == "__main__":
    main()
