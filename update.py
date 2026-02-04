import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
# 必须使用已验证证书的子域名
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    """尝试多源抓取，确保 GitHub Actions 能拿到数据"""
    # 尝试源 1: 公共优选接口 (极难被封)
    try:
        res = requests.get("https://cf.090227.xyz/getIP", timeout=10).json()
        if isinstance(res, list):
            return [{"ip": i['Address'], "line": "CM", "latency": i['Latency']} for i in res]
    except:
        pass
    
    # 尝试源 2: 原始 API (备用)
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
    
    # 过滤掉 1.0.x.x 等无效假 IP
    valid_ips = [i for i in ip_data if not i['ip'].startswith(("1.0.", "1.1.", "1.2."))]
    
    if valid_ips:
        # 抓取前 15 个有效 IP
        for item in valid_ips[:15]:
            ip = item['ip']
            remark = f"CF_{item.get('line','HK')}_{item.get('latency','0')}ms"
            # 这里的 SNI 和 Host 必须正确对应你的边缘证书
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    else:
        # 如果彻底没抓到，生成子域名保底
        links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#子域名保底_若-1请直连")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
