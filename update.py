import requests
import base64
import json

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/",
        "Content-Type": "application/json"
    }
    all_ips = []
    # 尝试拉取 IPv4 的所有优选数据
    try:
        payload = {"key": "iDetkO9Z", "type": "v4"}
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                all_ips = data.get("info", [])
    except Exception as e:
        print(f"API 获取失败: {e}")
    return all_ips

def main():
    ip_list = get_ips()
    vless_links = []
    
    # 如果抓到了 IP（正常会有几十个）
    if len(ip_list) > 0:
        print(f"成功！抓取到 {len(ip_list)} 个优选 IP")
        for item in ip_list:
            ip = item['ip']
            # 备注包含详细线路信息
            remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 失败保底，增加详细备注以便你在 v2rayN 里看到错误原因
        print("API 依然返回空数据，请检查 key 或 Headers")
        vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#接口拦截_请检查域名解析")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
