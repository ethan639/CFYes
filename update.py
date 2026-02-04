import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net"  # 保持使用你验证可用的子域名
PATH = "/"  
PORT = 443
# ==========================================

def get_ips_from_txt():
    """直接解析纯文本优选库，避开所有 API 拦截"""
    urls = [
        "https://raw.githubusercontent.com/vfarid/v2ray-worker-proxy/main/ips.txt",
        "https://cf.090227.xyz/getIP"
    ]
    found_ips = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                # 使用正则提取所有符合 IP 格式的字符串
                ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', resp.text)
                for ip in ips:
                    # 排除掉常见的假 IP 段
                    if not ip.startswith(("1.0.", "1.1.", "1.2.", "0.")):
                        found_ips.append(ip)
            if len(found_ips) > 20: break
        except:
            continue
    return list(dict.fromkeys(found_ips))[:30]

def main():
    ip_list = get_ips_from_txt()
    links = []
    
    if ip_list:
        print(f"实测抓取成功！获取到 {len(ip_list)} 个真实 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_真实优选_{i+1}"
            # 这里的参数必须和你之前“可用”的域名节点完全一致
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    else:
        # 终极保底，确保你现在的连接不断
        print("警告：抓取失败，使用域名节点保底")
        links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底节点")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
