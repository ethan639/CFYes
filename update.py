import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
# 保持使用你验证可用的子域名
HOST = "cs.cotco.dns-dynamic.net" 
PATH = "/"  
PORT = 443
# 你想要抓取的有效 IP 数量
MAX_COUNT = 30 
# ==========================================

def get_ips():
    """使用对 GitHub Actions 友好的备用接口抓取大量 IP"""
    ips = []
    try:
        # 这个接口专门解决 API 屏蔽 GitHub 的问题
        res = requests.get("https://cf.090227.xyz/getIP", timeout=15).json()
        if isinstance(res, list):
            for i in res:
                ips.append({
                    "ip": i['Address'], 
                    "line": "CM", # 移动线路通常最快
                    "latency": i['Latency']
                })
    except Exception as e:
        print(f"备用接口抓取失败: {e}")
    
    # 如果备用接口也挂了，才尝试原始 API
    if not ips:
        url = "https://api.hostmonit.com/get_optimization_ip"
        payload = {"key": "iDetkO9Z", "type": "v4"}
        try:
            res = requests.post(url, json=payload, timeout=10).json()
            if res.get("code") == 200:
                ips.extend(res.get("info", []))
        except:
            pass
    return ips

def main():
    ip_data = get_ips()
    links = []
    
    # 过滤掉 1.0.x.x 等无效 IP
    valid_ips = [i for i in ip_data if not i['ip'].startswith(("1.0.", "1.1.", "1.2."))]
    
    if valid_ips:
        for item in valid_ips[:MAX_COUNT]:
            ip = item['ip']
            # 备注包含延迟信息
            remark = f"CF_优选_{item.get('line','HK')}_{item.get('latency','0')}ms"
            # 这里的参数必须和你之前“可用”的节点完全一致
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)
    
    # 无论是否抓到 IP，都加上你那个“唯一可用”的域名节点作为终极保底
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功抓取并生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
