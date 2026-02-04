import requests
import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cotco.dns-dynamic.net"
PATH = "/"  # 如果你是用 Workers 搭建，请确认路径是否正确
PORT = 443
# ==========================================

def get_ips():
    url = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key": "iDetkO9Z", "type": "v4"}
    try:
        # 增加 Headers 模拟浏览器
        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
        res = requests.post(url, json=payload, headers=headers, timeout=15).json()
        if res.get("code") == 200:
            return res.get("info")
    except Exception as e:
        print(f"获取 IP 失败: {e}")
    return []

def main():
    ip_list = get_ips()
    # 只有获取到真实优选 IP 才会生成，否则报错以提醒用户
    if not ip_list:
        print("未获取到优选 IP，请检查 API 状态")
        return

    links = []
    for item in ip_list:
        ip = item['ip']
        # 别名包含延迟和线路信息
        remark = f"CF_{item['line']}_{item['colo']}_{item['latency']}ms"
        # 拼接 VLESS 链接
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)
    
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功更新 {len(links)} 个优选节点")

if __name__ == "__main__":
    main()
