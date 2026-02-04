import requests
import base64
import json
import os

# ================= 配置区 =================
# 如果你希望通过 GitHub Secret 保护隐私，可以使用 os.environ.get
USER_ID = os.environ.get("USER_ID", "f4055c9e-8500-4638-b13a-0e65fec24936")
HOST = os.environ.get("HOST", "cs.cotco.dns-dynamic.net")
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" # hostmonit 默认 KEY
# ==========================================

def get_optimization_ip():
    """获取三网优选 IP"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    headers = {'Content-Type': 'application/json'}
    data = {"key": KEY, "type": "v4"}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"抓取失败: {e}")
    return None

def main():
    res = get_optimization_ip()
    if not res or res.get("code") != 200:
        print("未能获取优选 IP 数据")
        return

    links = []
    lines = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    # 提取 IP 并拼接 VLESS 链接
    for code, name in lines.items():
        ip_info = res.get("info", {}).get(code, [])
        for item in ip_info:
            ip = item.get("ip")
            remark = f"CF_{name}_{ip}"
            # 这里的 SNI 和 Host 必须是你配置的 HOST
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)

    # 始终添加域名保底
    links.append(f"vless://{USER_ID}@{HOST}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#域名保底_稳如老狗")

    # Base64 编码
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    # 写入 sub.txt
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    print(f"成功更新 sub.txt，共 {len(links)} 个节点")

if __name__ == "__main__":
    main()
