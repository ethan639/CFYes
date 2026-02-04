import requests
import base64
import time

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
# 使用你已经设置了 CNAME 的子域名，成功率更高
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
# ==========================================

def get_ips_source1():
    """源1: hostmonit API"""
    url = "https://api.hostmonit.com/get_optimization_ip"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        res = requests.post(url, json={"key": "iDetkO9Z", "type": "v4"}, headers=headers, timeout=10).json()
        return res.get("info", []) if res.get("code") == 200 else []
    except:
        return []

def get_ips_source2():
    """源2: 备用公共接口"""
    url = "https://cf.090227.xyz/getIP" # 这是一个常用的备用优选IP源
    try:
        res = requests.get(url, timeout=10).json()
        return res if isinstance(res, list) else []
    except:
        return []

def main():
    # 尝试多源抓取
    ip_list = get_ips_source1()
    if not ip_list:
        print("源1失败，尝试源2...")
        ip_list = get_ips_source2()

    vless_links = []
    if ip_list:
        print(f"成功抓取到 {len(ip_list)} 个优选 IP")
        for item in ip_list[:15]: # 取前15个最优IP
            ip = item.get('ip') or item.get('Address')
            line = item.get('line') or "CF"
            latency = item.get('latency') or "0"
            remark = f"CF_{line}_{latency}ms"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 兜底：如果还抓不到，生成 5 个使用 cs 子域名的节点
        print("所有 API 均拦截，生成 CNAME 备份节点")
        for i in range(1, 6):
            vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#子域名备份_{i}")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
