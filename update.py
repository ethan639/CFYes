import requests
import json
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  # 请确保这与你服务器端的 WebSocket 路径一致
PORT = 443
# ==========================================

def get_ips():
    # 使用备用公共 API 接口
    url = "https://api.hostmonit.com/get_optimization_ip"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/"
    }
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        # 增加重试机制
        res = requests.post(url, json=payload, headers=headers, timeout=15).json()
        if res.get("code") == 200 and res.get("info"):
            return res.get("info")
    except:
        pass
    return []

def main():
    ip_list = get_ips()
    
    # 如果抓不到优选 IP，至少生成一个正确的备份节点
    if not ip_list:
        print("未抓取到实时 IP，生成域名备份节点...")
        ip_list = [{"ip": HOST, "line": "移动/联通/电信", "colo": "Domain", "latency": "Direct"}]

    links = []
    for item in ip_list:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        # 严格 VLESS WS+TLS 格式
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)
    
    combined = "\n".join(links)
    b64_str = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(b64_str)
    print(f"成功生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
