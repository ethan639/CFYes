import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
# 使用你已经验证可用的子域名
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
MAX_IP_COUNT = 30  # 设置你想要抓取的 IP 数量
# ==========================================

def get_ips():
    """多源抓取逻辑：确保在 GitHub 环境下也能拿到大量 IP"""
    ips = []
    # 源 1: 对 GitHub 极其友好的公共接口
    try:
        res = requests.get("https://cf.090227.xyz/getIP", timeout=10).json()
        if isinstance(res, list):
            for i in res:
                ips.append({"ip": i['Address'], "line": "CM", "latency": i['Latency']})
    except:
        pass
    
    # 源 2: 你的原始 API (作为备用)
    if not ips:
        url = "https://api.hostmonit.com/get_optimization_ip"
        payload = {"key": "iDetkO9Z", "type": "v4"}
        try:
            res = requests.post(url, json=payload, timeout=10).json()
            if res.get("code") == 200:
                ips.extend(res.get("info", []))
        except:
            pass
    return ips

def main():
    ip_list = get_ips()
    links = []
    
    # 如果抓到了数据，过滤掉假 IP (1.0.x.x)
    valid_ips = [i for i in ip_list if not i['ip'].startswith(("1.0.", "1.1.", "1.2."))]
    
    if valid_ips:
        for item in valid_ips[:MAX_IP_COUNT]:
            ip = item['ip']
            remark = f"CF_优选_{item.get('line','HK')}_{item.get('latency','0')}ms"
            # 核心：地址用优选 IP，SNI 和 Host 必须用你验证过的域名
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    else:
        # 如果彻底没抓到，生成你现在“可用”的那个域名节点保底
        links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#保底域名节点")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功抓取并生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
