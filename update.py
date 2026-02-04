import requests
import base64
import json

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  # ！！！请务必确认你的服务端路径
PORT = 443
# ==========================================

def get_all_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://stock.hostmonit.com",
        "Referer": "https://stock.hostmonit.com/"
    }
    
    all_nodes = []
    # 分别请求 v4 的优选数据
    payload = {"key": "iDetkO9Z", "type": "v4"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        if res_data.get("code") == 200:
            return res_data.get("info", [])
    except Exception as e:
        print(f"API 请求出错: {e}")
    return []

def main():
    ip_list = get_all_ips()
    
    if not ip_list:
        print("未能从 API 获取到数据，生成域名备份节点...")
        ip_list = [{"ip": HOST, "line": "Backup", "colo": "Domain", "latency": "0"}]

    vless_links = []
    # 限制抓取数量，防止订阅链接过长，通常取前 20 个最优 IP
    for item in ip_list[:20]:
        ip = item['ip']
        # 备注包含：线路(移动/联通/电信)_地区_延迟
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        vless_links.append(link)
    
    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功更新！共抓取到 {len(vless_links)} 个优选节点。")

if __name__ == "__main__":
    main()
