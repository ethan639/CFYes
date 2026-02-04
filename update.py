import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
# ==========================================

def get_real_ips():
    """精准抓取网页中的真实优选 IP 段"""
    url = "https://stock.hostmonit.com/CloudFlareYes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 排除 1.0.x.x 和 1.1.x.x，只抓取 141.101 / 172 / 104 / 198 等开头的真实 CF IP
        pattern = r'(?:141\.101|104\.\d{1,3}|172\.\d{1,3}|198\.41)\.\d{1,3}\.\d{1,3}'
        raw_ips = re.findall(pattern, response.text)
        
        # 简单去重
        unique_ips = list(dict.fromkeys(raw_ips))
        return unique_ips[:10] # 只取前10个
    except:
        return []

def main():
    ip_list = get_real_ips()
    vless_links = []
    
    if ip_list:
        print(f"成功！抓取到 {len(ip_list)} 个真实优选 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_真实优选_{i+1}"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # ！！！关键：如果抓取失败，自动变回你之前能用的域名模式
        print("抓取不到真实 IP，自动切换到域名保底模式...")
        vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_虽然-1但能上网")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
