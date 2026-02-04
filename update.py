import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 使用你已配置好的 CNAME 子域名
PATH = "/"  
PORT = 443
# ==========================================

def get_ips_from_web():
    """直接爬取网页公开的 IP 列表"""
    url = "https://stock.hostmonit.com/CloudFlareYes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 使用正则表达式提取网页中的 IP 地址
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
        # 去重并排除掉一些常见的 DNS 或 本机 IP
        unique_ips = list(set([ip for ip in ips if not ip.startswith('127.') and not ip.startswith('0.')]))
        return unique_ips[:15] # 只要前15个最新的
    except Exception as e:
        print(f"网页抓取失败: {e}")
        return []

def main():
    ip_list = get_ips_from_web()
    vless_links = []
    
    if ip_list:
        print(f"成功通过爬虫抓取到 {len(ip_list)} 个实时优选 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_自动优选_{i+1}"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 如果爬虫也失败，才使用备份
        print("所有抓取方式均失效，请检查网络连接")
        vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#抓取失败_检查仓库Actions")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
