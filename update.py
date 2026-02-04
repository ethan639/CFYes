import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net"  # 保持使用你验证可用的子域名
PATH = "/"  
PORT = 443
MAX_COUNT = 50  # 增加抓取上限到 50 个
# ==========================================

def get_ips():
    """使用三个不同的高可用接口抓取 IP，确保不落空"""
    ips = []
    # 源 1: 公共优选源 (最稳定)
    try:
        res = requests.get("https://cf.090227.xyz/getIP", timeout=10).json()
        if isinstance(res, list):
            for i in res:
                ips.append({"ip": i['Address'], "line": "CM", "latency": i['Latency']})
    except: pass

    # 源 2: 备用源
    if len(ips) < 10:
        try:
            res = requests.get("https://vps789.com/public/cfip", timeout=10).json()
            for i in res['data']:
                ips.append({"ip": i['ip'], "line": "CF", "latency": i['delay']})
        except: pass

    # 源 3: 你的原始 API (最后尝试)
    if len(ips) < 5:
        url = "https://api.hostmonit.com/get_optimization_ip"
        try:
            res = requests.post(url, json={"key": "iDetkO9Z", "type": "v4"}, timeout=10).json()
            if res.get("code") == 200:
                ips.extend(res.get("info", []))
        except: pass
    
    return ips

def main():
    ip_data = get_ips()
    links = []
    
    # 严格过滤无效 IP 段
    valid_ips = [i for i in ip_data if not i['ip'].startswith(("1.0.", "1.1.", "1.2."))]
    
    if valid_ips:
        # 去重处理
        seen = set()
        for item in valid_ips:
            if item['ip'] not in seen:
                seen.add(item['ip'])
                remark = f"CF_优选_{item.get('line','HK')}_{item.get('latency','0')}ms"
                link = f"vless://{USER_ID}@{item['ip']}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                links.append(link)
            if len(links) >= MAX_COUNT: break
    
    # 终极保底：无论如何都带上你那个能用的域名节点
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功抓取并生成 {len(links)} 个节点")

if __name__ == "__main__":
    main()
