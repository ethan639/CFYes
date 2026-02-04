import requests
import base64
import json
import os

# ================= 配置区 (请务必核对以下两项) =================
USER_ID = os.environ.get("USER_ID", "f4055c9e-8500-4638-b13a-0e65fec24936")
HOST = os.environ.get("HOST", "cs.cotco.dns-dynamic.net")
# =============================================================

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
        print(f"抓取失败: {e}")
    return None

def main():
    res = get_optimization_ip()
    if not res or res.get("code") != 200:
        return

    links = []
    lines_map = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    for code, name in lines_map.items():
        ip_info = res.get("info", {}).get(code, [])
        for item in ip_info:
            ip = item.get("ip")
            colo = item.get("colo", "Unknown")
            if not ip:
                continue
            
            remark = f"{name}_{colo}"
            # 关键：确保生成链接包含完整的 tls 和 ws 配置
            # 必须确保 host 和 sni 都等于你配置的真实域名
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)

    if not links:
        return

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    print(f"成功更新 sub.txt，共生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
