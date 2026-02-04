import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 使用你已配置的 CNAME 子域名
PATH = "/"  
PORT = 443
# ==========================================

def get_real_ips():
    """从网页源代码中精准提取包含优选 IP 的数据块"""
    url = "https://stock.hostmonit.com/CloudFlareYes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 精准匹配：只抓取那些常见的 CF 优选 IP 段（如 141.101, 104.xx, 172.xx, 198.xx）
        # 排除掉 1.0.x.x 或 1.1.x.x 等干扰项
        raw_ips = re.findall(r'(?:141\.101|104\.|172\.|198\.41)\.\d{1,3}\.\d{1,3}', response.text)
        
        # 简单去重并只取前 10 个最活跃的
        unique_ips = []
        for ip in raw_ips:
            if ip not in unique_ips:
                unique_ips.append(ip)
        return unique_ips[:10]
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def main():
    ip_list = get_real_ips()
    vless_links = []
    
    if ip_list:
        print(f"成功抓取到 {len(ip_list)} 个真实优选 IP")
        for i, ip in enumerate(ip_list):
            remark = f"CF_真实优选_{i+1}"
            # 这里的 SNI 和 Host 必须是你的 cs 子域名
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 如果爬虫失效，使用你之前“能用”的域名模式作为保底
        print("未抓取到有效 IP，返回域名保底模式")
        vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_能上网但延迟显示-1")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
