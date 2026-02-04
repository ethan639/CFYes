import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
# 必须使用你已验证有效的子域名
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
# ==========================================

def get_real_ips():
    """精准抓取网页中的真实优选 IP 段，排除测试地址"""
    url = "https://stock.hostmonit.com/CloudFlareYes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 1. 提取所有 IP 地址
        all_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
        
        # 2. 严格过滤：排除 1.x.x.x 和 0.x.x.x，保留 141.101 / 198.41 / 104 / 172 段位
        valid_ips = []
        for ip in all_ips:
            if ip.startswith(("141.101", "198.41", "104.", "172.67", "162.159")):
                if ip not in valid_ips:
                    valid_ips.append(ip)
        
        return valid_ips[:15] # 只要前15个最快的
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def main():
    ip_list = get_real_ips()
    vless_links = []
    
    if ip_list:
        print(f"成功！抓取到 {len(ip_list)} 个真实优选 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_真实优选_{i+1}"
            # 节点核心配置：地址为 IP，SNI 为你的域名
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # ！！！如果抓不到 IP，回退到之前“虽然-1但能上网”的域名模式
        print("未抓到有效 IP，返回域名保底模式")
        vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_若显示-1请直接连接")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
