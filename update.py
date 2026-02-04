import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
# 建议改用已验证证书的子域名，确保握手成功
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
MAX_IP_COUNT = 15  # 你想要抓取的有效 IP 数量
# ==========================================

def get_ips():
    """多源抓取逻辑：解决 GitHub Actions 被拦截的问题"""
    ips = []
    # 源 1: 你原始使用的 API (容易拦截 GitHub)
    url1 = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url1, json=payload, timeout=10).json()
        if res.get("code") == 200:
            ips.extend(res.get("info", []))
    except:
        pass

    # 源 2: 备用公共接口 (专门供应给 GitHub Actions，不会拦截)
    if len(ips) < 2:
        try:
            url2 = "https://cf.090227.xyz/getIP"
            res2 = requests.get(url2, timeout=10).json()
            for item in res2:
                ips.append({
                    "ip": item['Address'], 
                    "line": "CM", 
                    "colo": "HK", 
                    "latency": item['Latency']
                })
        except:
            pass
    return ips

def main():
    raw_ip_list = get_ips()
    
    # 过滤掉无效 IP (如 1.0.x.x) 并限制抓取数量
    valid_ips = []
    for item in raw_ip_list:
        ip = item['ip']
        if not ip.startswith(("1.0.", "1.1.", "1.2.")): # 排除假优选 IP
            valid_ips.append(item)
        if len(valid_ips) >= MAX_IP_COUNT:
            break

    # 如果所有源都抓不到，生成一个域名节点保底
    if not valid_ips:
        valid_ips = [{"ip": HOST, "line": "Backup", "colo": "Direct", "latency": "0"}]

    links = []
    for item in valid_ips:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        # 核心：无论连接哪个 IP，SNI 必须是你的有效域名
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)
    
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
