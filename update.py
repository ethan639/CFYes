import requests
import json
import base64
import os

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    # 尝试模拟真实的浏览器请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        data = res.json()
        if data.get("code") == 200:
            return data.get("info", [])
        else:
            print(f"API 返回错误: {data.get('msg')}")
    except Exception as e:
        print(f"请求失败: {e}")
    return []

def main():
    ip_list = get_ips()
    
    # 如果抓取不到 IP，不要清空文件，直接退出
    if not ip_list:
        print("未获取到 IP 数据，停止更新以保留旧数据。")
        return

    vless_links = []
    for item in ip_list:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        vless_links.append(link)
    
    combined_text = "\n".join(vless_links)
    final_sub = base64.b64encode(combined_text.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成 {len(vless_links)} 个节点。")

if __name__ == "__main__":
    main()
