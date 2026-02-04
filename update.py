import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 已验证可用的子域名
PATH = "/"  
PORT = 443
MAX_IP_COUNT = 30 # 抓取 30 个有效 IP
# ==========================================

def get_ips_from_web():
    """直接从网页 stock.hostmonit.com/CloudFlareYes 抓取真实 IP"""
    url = "https://stock.hostmonit.com/CloudFlareYes"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://stock.hostmonit.com/'
    }
    try:
        # 请求网页内容
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # 匹配页面中的 IP 格式（排除 1.0.1.1 等假地址）
            raw_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
            valid_ips = []
            for ip in raw_ips:
                # 严格过滤无效 IP 段
                if not ip.startswith(("1.0.", "1.1.", "1.2.", "0.", "127.")):
                    valid_ips.append(ip)
            return list(dict.fromkeys(valid_ips)) # 去重
    except Exception as e:
        print(f"网页抓取发生错误: {e}")
    return []

def main():
    ip_list = get_ips_from_web()
    links = []
    
    if ip_list:
        print(f"实测抓取成功！从网页获取到 {len(ip_list)} 个 IP")
        for i, ip in enumerate(ip_list[:MAX_IP_COUNT]):
            remark = f"CF_Web优选_{i+1}"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    
    # 终极保底：确保订阅文件不为空且包含验证可用的域名节点
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"订阅文件已更新，当前体积: {len(final_sub)} 字节")

if __name__ == "__main__":
    main()
