import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
# ！！！请确认你的路径，如果不是 / 请修改此处 ！！！
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url, json=payload, timeout=15).json()
        return res.get("info", []) if res.get("code") == 200 else []
    except:
        return []

def main():
    ip_list = get_ips()
    # 如果没抓到 IP，生成一个基础域名节点，方便调试
    if not ip_list:
        ip_list = [{"ip": HOST, "line": "Backup", "colo": "Direct", "latency": "0"}]

    links = []
    for item in ip_list:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        # 确保 VLESS 参数完整
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)
    
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
