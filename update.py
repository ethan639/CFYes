import requests
import json
import base64
import os

# ================= 配置区 =================
# 必须确认你的 UUID 和 路径(PATH) 与服务端一致
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  # 如果是 Workers 搭建，通常为 / 或 /uuid
PORT = 443
# ==========================================

def get_ips():
    """
    从 API 获取优选 IP。增加伪装 Headers 以降低被拦截风险。
    """
    url = "https://api.hostmonit.com/get_optimization_ip"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        data = response.json()
        if data.get("code") == 200:
            return data.get("info", [])
        else:
            print(f"API 返回异常: {data.get('msg')}")
    except Exception as e:
        print(f"网络请求失败: {e}")
    return []

def main():
    ip_list = get_ips()
    
    # 逻辑优化：如果 API 暂时抓不到数据，生成基于域名的节点防止文件变成 0 Bytes
    if not ip_list:
        print("未抓取到实时 IP，生成域名备份节点以保证订阅有效性...")
        ip_list = [
            {"ip": HOST, "line": "Backup", "colo": "Any", "latency": "0"}
        ]

    vless_links = []
    for item in ip_list:
        ip = item['ip']
        # 别名：包含线路、数据中心和延迟信息，方便在 V2Ray 中识别
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        
        # 拼接标准的 VLESS WS+TLS 格式链接
        link = (
            f"vless://{USER_ID}@{ip}:{PORT}"
            f"?encryption=none&security=tls&sni={HOST}"
            f"&type=ws&host={HOST}&path={PATH}"
            f"#{remark}"
        )
        vless_links.append(link)
    
    # 将所有链接按换行符连接
    combined_text = "\n".join(vless_links)
    
    # 进行 Base64 编码（这是 V2Ray 订阅文件的标准要求）
    final_sub = base64.b64encode(combined_text.encode('utf-8')).decode('utf-8')
    
    # 写入文件
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    
    print(f"任务完成！成功生成 {len(vless_links)} 个节点信息。")

if __name__ == "__main__":
    main()
