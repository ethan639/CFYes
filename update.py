import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net"  # 保持使用你验证可用的子域名
PATH = "/"  
PORT = 443
# ==========================================

def get_real_ips():
    """从多个不封锁 GitHub 的源抓取真实优选 IP"""
    sources = [
        "https://raw.githubusercontent.com/vfarid/v2ray-worker-proxy/main/ips.txt",
        "https://cf.090227.xyz/getIP",
        "https://raw.githubusercontent.com/Alvin9999/new-pac/master/cloudflare.txt"
    ]
    ips = []
    for url in sources:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                # 提取所有符合 IP 格式的字符串
                raw_find = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', resp.text)
                for ip in raw_find:
                    # 彻底剔除 1.0.1.1 这种假优选
                    if not ip.startswith(("1.0.", "1.1.", "1.2.", "0.", "127.")):
                        ips.append(ip)
            if len(ips) > 50: break
        except: continue
    return list(dict.fromkeys(ips))[:40] # 去重并取前40个

def main():
    ip_list = get_real_ips()
    links = []
    
    if ip_list:
        print(f"实测抓取成功！获取到 {len(ip_list)} 个 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_真实优选_{i+1}"
            # 这里的参数必须和你验证可用的域名节点完全一致
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    
    # 终极保底：无论如何都带上你那个目前能用的域名节点
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
