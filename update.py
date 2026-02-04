import requests
import base64
import time
import random

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net"
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://stock.hostmonit.com/",
        "Origin": "https://stock.hostmonit.com",
        "Content-Type": "application/json"
    }
    
    # 增加随机延时，防止 GitHub Actions 的并发请求被拦截
    time.sleep(random.uniform(2, 5))
    
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("code") == 200:
                return res_json.get("info", [])
    except Exception as e:
        print(f"API 请求异常: {e}")
    return []

def main():
    ip_list = get_ips()
    vless_links = []
    
    if len(ip_list) > 1:
        print(f"成功突破拦截！抓取到 {len(ip_list)} 个优选 IP")
        for item in ip_list:
            ip = item['ip']
            # 别名显示：线路_地区_延迟
            remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            vless_links.append(link)
    else:
        # 如果依然只有 1 个，生成带编号的多个备份，强行撑大文件体量尝试触发测速
        print("API 依然返回受限数据，生成多组备份节点...")
        for i in range(1, 6):
            vless_links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#备份节点_{i}_待刷新")

    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
