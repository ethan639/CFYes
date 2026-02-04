import requests
import base64
import time

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 建议改用已验证证书的子域名
PATH = "/"  
PORT = 443
MAX_IP_COUNT = 20  # 设置你想要抓取的有效 IP 数量
# ==========================================

def get_ips():
    ips = []
    # 源 1: 你的原始 API
    url1 = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url1, json=payload, timeout=10).json()
        if res.get("code") == 200:
            ips.extend(res.get("info", []))
    except:
        pass

    # 源 2: 备用公共接口 (专门解决 GitHub Actions 被拦截的问题)
    if len(ips) < 2:
        try:
            # 这个源直接返回大量 Cloudflare 优选 IP
            url2 = "https://cf.090227.xyz/getIP"
            res2 = requests.get(url2, timeout=10).json()
            for item in res2:
                ips.append({
                    "ip": item['Address'], 
                    "line": "CM", # 移动线路通常最快
                    "colo": "HK", 
                    "latency": item['Latency']
                })
        except:
            pass
    return ips

def main():
    raw_ip_list = get_ips()
    
    # 过滤掉无效 IP (如 1.0.x.x) 并限制数量
    valid_ips = []
    for item in raw_ip_list:
        ip = item['ip']
        # 排除测试 IP 确保节点可用
        if not ip.startswith(("1.0.", "1.1.", "1.2.")):
            valid_ips.append(item)
        if len(valid_ips) >= MAX_IP_COUNT:
            break

    # 如果还是没抓到，生成保底域名节点
    if not valid_ips:
        valid_ips = [{"ip": HOST, "line": "Backup", "colo": "Direct", "latency": "0"}]

    links = []
    for item in valid_ips:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)
    
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功抓取并生成 {len(links)} 个有效节点")

if __name__ == "__main__":
    main()
