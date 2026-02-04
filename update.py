import requests
import base64
import json
import os

# ================= 配置区 =================
# 建议在 GitHub Settings -> Secrets 中配置以下变量，更加安全
USER_ID = os.environ.get("USER_ID", "f4055c9e-8500-4638-b13a-0e65fec24936")
HOST = os.environ.get("HOST", "cs.cotco.dns-dynamic.net")
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
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
        print("未能获取优选 IP 数据，请检查 API KEY 或网络连接")
        return

    links = []
    lines = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    # 提取 IP 并拼接 VLESS 链接
    for code, name in lines.items():
        ip_info = res.get("info", {}).get(code, [])
        for item in ip_info:
            ip = item.get("ip")
            if not ip:
                continue
            
            # 优化：别名仅保留“CF_线路名”
            remark = f"CF_{name}"
            
            # 构造 VLESS 链接
            # Address 使用抓取到的 IP，SNI 和 Host 使用原始域名
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)

    # 优化：既然已经能抓到 IP，此处已移除“域名保底”项

    if not links:
        print("抓取到的 IP 列表为空，未生成 sub.txt")
        return

    # Base64 编码
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    # 写入 sub.txt
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    
    print(f"成功更新 sub.txt，共生成 {len(links)} 个优选节点")

if __name__ == "__main__":
    main()
