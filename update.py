import requests
import base64
import re

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net"  
PATH = "/"  
PORT = 443
# ==========================================

def get_verified_ips():
    """修正后的抓取逻辑：多源聚合 + 强力正则"""
    # 增加目前社区维护最活跃的几个源
    sources = [
        "https://raw.githubusercontent.com/Alvin9999/new-pac/master/cloudflare.txt",
        "https://raw.githubusercontent.com/ymyuuu/IPDB/main/cloudflare.txt",
        "https://vfarid.github.io/cf-ip-scanner/history.json" # 如果是JSON需要特殊处理，这里先按文本抓取
    ]
    
    ips = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in sources:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                # 改进后的正则：支持匹配纯 IP，也支持匹配 IP:PORT 格式并只取 IP
                found = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', resp.text)
                for ip in found:
                    # 严格过滤无效段：剔除 1.0.0.x, 1.1.1.x, 0.x.x.x, 127.x.x.x
                    if not ip.startswith(("1.0.", "1.1.", "1.2.", "0.", "127.", "10.", "192.168.")):
                        ips.append(ip)
                print(f"源 {url} 成功提取到 {len(found)} 个潜在 IP")
        except Exception as e:
            print(f"连接源 {url} 失败: {e}")
            continue
            
    # 去重并截取前 50 个
    unique_ips = list(dict.fromkeys(ips))
    return unique_ips[:50]

def main():
    final_ips = get_verified_ips()
    links = []
    
    # 逻辑验证：如果抓取成功，生成节点
    if final_ips:
        for i, ip in enumerate(final_ips):
            remark = f"CF_Verified_{i+1}"
            # 修正：确保 SNI 和 Host 都正确传入
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    else:
        print("警告：未能抓取到任何有效 IP，请检查网络环境或源地址！")
    
    # 终极保底
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    
    print(f"任务结束：共生成 {len(links)} 个节点，已保存至 sub.txt")

if __name__ == "__main__":
    main()
