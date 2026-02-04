import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 已验证证书有效的子域名
PATH = "/"  
PORT = 443
MAX_COUNT = 20 # 想要抓取的有效 IP 数量
# ==========================================

def get_ips():
    """尝试多源抓取，突破 GitHub 拦截"""
    # 尝试源 1 (备用源，对 GitHub 友好)
    try:
        res = requests.get("https://cf.090227.xyz/getIP", timeout=10).json()
        if isinstance(res, list):
            return [{"ip": i['Address'], "line": "CM", "latency": i['Latency']} for i in res]
    except:
        pass
    
    # 尝试源 2 (原始 API)
    url = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url, json=payload, timeout=10).json()
        if res.get("code") == 200:
            return res.get("info", [])
    except:
        return []
    return []

def main():
    ip_data = get_ips()
    links = []
    
    # 如果抓到了数据，过滤掉假 IP (1.0.x.x)
    valid_ips = [i for i in ip_data if not i['ip'].startswith(("1.0.", "1.1.", "1.2."))]
    
    if valid_ips:
        for item in valid_ips[:MAX_COUNT]:
            ip = item['ip']
            remark = f"CF_{item.get('line','优选')}_{item.get('latency','0')}ms"
            # 这里的 SNI 和 Host 必须是你的有效子域名
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    else:
        # 如果彻底没抓到，生成域名保底，防止 sub.txt 变空
        links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_若-1请直连")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功抓取并生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
