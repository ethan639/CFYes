import requests
import json
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  # 如果你的路径不是根目录，请修改这里
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    try:
        res = requests.post(url, json={"key": "iDetkO9Z", "type": "v4"}, timeout=10).json()
        return res.get("info", []) if res.get("code") == 200 else []
    except:
        return []

def main():
    ip_list = get_ips()
    vless_links = []
    for item in ip_list:
        ip = item['ip']
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        # 构建 VLESS 标准格式
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        vless_links.append(link)
    
    # 转换为 V2Ray 订阅所需的 Base64 格式
    combined_text = "\n".join(vless_links)
    final_sub = base64.b64encode(combined_text.encode('utf-8')).decode('utf-8')
    
    # 将结果保存到本地文件
    with open("sub.txt", "w") as f:
        f.write(final_sub)

if __name__ == "__main__":
    main()
