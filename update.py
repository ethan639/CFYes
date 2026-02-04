import requests
import base64
import json
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
# 这是一个常用的优选 IP 公开接口，数据源通常来自 cf2dns 监控
IP_SOURCE_URL = "https://vfarid.github.io/cf-ip-scanner/history.json" 
# 或者直接使用 cf2dns 相关的公共接口
# ==========================================

def get_real_quality_ips():
    """从高质量优选池抓取 IP，而非扫描全网 IP 段"""
    ips = []
    # 策略 A: 抓取已知维护良好的优选 IP 列表
    sources = [
        "https://raw.githubusercontent.com/ymyuuu/IPDB/main/cloudflare.txt",
        "https://vfarid.github.io/cf-ip-scanner/history.json"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                # 如果是 JSON 格式 (针对第二个源)
                if url.endswith(".json"):
                    data = resp.json()
                    # 提取最近一次扫描中延迟低的 IP
                    for entry in data[:30]: 
                        ips.append(entry['ip'])
                else:
                    # 如果是 TXT 格式，提取 IP
                    found = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', resp.text)
                    ips.extend(found)
        except Exception as e:
            print(f"源 {url} 抓取失败: {e}")
            continue

    # 过滤掉无效和内网 IP
    valid_ips = [ip for ip in dict.fromkeys(ips) if not ip.startswith(("1.0.", "1.1.", "1.2.", "0.", "127."))]
    return valid_ips[:50] # 返回前 50 个最优质的

def main():
    final_ips = get_real_quality_ips()
    links = []
    
    # 1. 生成优选 IP 节点
    if final_ips:
        for i, ip in enumerate(final_ips):
            remark = f"CF_优选_{i+1}"
            # 注意：SNI 和 Host 必须是你配置区里的那个 HOST
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    
    # 2. 始终保留你的域名保底节点
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    # 3. Base64 编码输出
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    
    print(f"成功！生成了 {len(links)} 个节点。")
    print(f"第一个 IP 示例: {final_ips[0] if final_ips else '无'}")

if __name__ == "__main__":
    main()
