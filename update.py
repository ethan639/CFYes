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
    """获取数据，增加超时重试"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("code") == 200:
                return res_json
        print(f"[{ip_type}] 接口返回异常: {response.status_code}")
    except Exception as e:
        print(f"[{ip_type}] 网络请求失败: {e}")
    return None

def safe_int_latency(latency_val):
    """鲁棒的延迟解析逻辑"""
    if latency_val is None:
        return 999
    s = str(latency_val).lower().replace("ms", "").strip()
    try:
        return int(float(s))
    except:
        return 999

def main():
    # 生成北京时间时间戳 (UTC+8)
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    
    # 按照要求顺序：先 v4 后 v6
    for ip_ver in ['v4', 'v6']:
        print(f"正在处理 {ip_ver}...")
        res = get_data(ip_ver)
        if not res:
            continue
            
        info = res.get("info", {})
        # 严格按照图示顺序：移动 -> 联通 -> 电信
        for code, name in [("CM", "移动"), ("CU", "联通"), ("CT", "电信")]:
            line_data = info.get(code, [])
            if not isinstance(line_data, list):
                continue
            
            # 组内按延迟排序
            sorted_data = sorted(line_data, key=lambda x: safe_int_latency(x.get("latency", 999)))
            
            for item in sorted_data:
                ip = item.get("ip")
                if not ip: continue
                
                # 针对 IPv6 地址添加方括号
                address = f"[{ip}]" if ":" in ip else ip
                
                colo = item.get("colo", "Default")
                # 确保延迟显示带有 ms 单位
                lat_raw = str(item.get("latency", "Unknown"))
                lat_display = lat_raw if "ms" in lat_raw.lower() else f"{lat_raw}ms"
                
                # 别名优化：移动_IPv4_LAX_51ms_08:45
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                remark = f"{name}_{tag}_{colo}_{lat_display}_{beijing_time}"
                
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        content = "\n".join(all_links)
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))
        print(f"[{beijing_time}] 成功同步 {len(all_links)} 个节点。格式已优化。")
    else:
        print("未获取到节点数据。")

if __name__ == "__main__":
    main()
