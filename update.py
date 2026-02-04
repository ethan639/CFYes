import requests
import base64
import json

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    # 模拟网页端的真实请求头，这是成功的关键
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://stock.hostmonit.com/",
        "Origin": "https://stock.hostmonit.com",
        "Content-Type": "application/json"
    }
    # 尝试拉取所有线路的数据
    payload = {"key": "iDetkO9Z", "type": "v4"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        res_data = response.json()
        if res_data.get("code") == 200:
            info = res_data.get("info", [])
            # 只有抓到超过 1 个 IP 时才返回列表
            if len(info) > 0:
                return info
    except Exception as e:
        print(f"API 获取失败: {e}")
    return []

def main():
    ip_list = get_ips()
    vless_links = []
    
    if ip_list:
        print(f"成功抓取到 {len(ip_list)} 个优选 IP")
        for item in ip_list:
            ip = item['ip']
            # 备注包含详细线路和延迟，方便 V2Ray 识别
            remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 如果依然抓不到，生成一个包含明确提示的节点
        print("API 依然拦截，生成备份节点...")
        vless_links = [f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#接口维护_抓取失败_请稍后再试"]

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
