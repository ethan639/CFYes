import requests
import base64
import time

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 建议使用已验证证书的子域名
PATH = "/"  
PORT = 443
MAX_IP_COUNT = 15  # 你想要抓取的有效 IP 数量
# ==========================================

def get_ips():
    """尝试从多个源抓取优选 IP"""
    ips = []
    # 源 1: 官方 API
    url1 = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url1, json=payload, timeout=10).json()
        if res.get("code") == 200:
            ips.extend(res.get("info", []))
    except:
        pass

    # 源 2: 备用公共接口 (防止 API 拦截 GitHub Actions)
    if not ips:
        try:
            url2 = "https://cf.090227.xyz/getIP"
            res2 = requests.get(url2, timeout=10).json()
            # 格式化数据以匹配你的原始逻辑
            for item in res2:
                ips.append({"ip": item['Address'], "line": "CM", "colo": "HK", "latency": item['Latency']})
        except:
            pass
    return ips

def main():
    ip_list = get_ips()
    
    # 限制抓取数量
    final_ip_list = ip_list[:MAX_IP_COUNT]

    # 如果所有源都失败，生成保底域名节点
    if not final_ip_list:
        final_ip_list = [{"ip": HOST, "line": "Backup", "colo": "Direct", "latency": "0"}]

    links = []
    for item in final_ip_list:
        ip = item['ip']
        # 排除无效的假 IP (如 1.0.1.1)
        if ip.startswith(("1.0.", "1.1.", "1.2.")):
            continue
            
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)
    
    # 如果过滤后没节点了，强制加一个域名节点
    if not links:
        links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底")
    
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成 {len(links)} 个有效节点")

if __name__ == "__main__":
    main()
