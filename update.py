import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 保持使用已验证的子域名
PATH = "/"  
PORT = 443
# ==========================================

def get_clean_ips():
    """只抓取真实的 CF 优选 IP 段，彻底屏蔽 1.x.x.x"""
    url = "https://stock.hostmonit.com/CloudFlareYes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 精准匹配：141.101, 104, 172, 162, 198 等真实段位
        pattern = r'(?:141\.101|104\.|172\.67|162\.159|198\.41)\.\d{1,3}\.\d{1,3}'
        raw_ips = re.findall(pattern, response.text)
        return list(dict.fromkeys(raw_ips))[:15]
    except:
        return []

def main():
    ip_list = get_clean_ips()
    vless_links = []
    
    if ip_list:
        print(f"成功！抓取到 {len(ip_list)} 个真实优选 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_优选_{i+1}"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 如果爬虫失效，使用你之前能上网的子域名保底
        print("抓取失败，使用子域名保底模式")
        vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#子域名保底_若-1请直连")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
