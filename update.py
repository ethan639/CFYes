import requests
import json
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        res = requests.post(url, json=payload, timeout=15).json()
        if res.get("code") == 200:
            return res.get("info", [])
    except Exception as e:
        print(f"抓取失败: {e}")
    return []

def main():
    ip_list = get_ips()
    if not ip_list:
        print("错误：未能获取到 IP 数据")
        exit(1) # 强制报错，防止 Actions 继续执行错误的推送

    vless_links = []
    for item in ip_list:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        # 标准 VLESS 格式
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        vless_links.append(link)
    
    combined_text = "\n".join(vless_links)
    final_sub = base64.b64encode(combined_text.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成节点，文件大小: {len(final_sub)} 字节")

if __name__ == "__main__":
    main()
