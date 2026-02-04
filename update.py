import requests
import base64
import json
import os

# ================= 配置区 =================
USER_ID = os.environ.get("USER_ID", "f4055c9e-8500-4638-b13a-0e65fec24936")
HOST = os.environ.get("HOST", "cs.cotco.dns-dynamic.net")
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_optimization_ip():
    """获取三网优选 IP，包含 Colo 信息"""
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
    lines_map = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    # 提取 IP 并按“线路_Colo”格式拼接 VLESS 链接
    for code, name in lines_map.items():
        ip_info = res.get("info", {}).get(code, [])
        for item in ip_info:
            ip = item.get("ip")
            colo = item.get("colo", "Unknown") # 获取图中所示的 Colo 字段
            if not ip:
                continue
            
            # 优化：别名改为“线路_Colo”（例如：移动_LAX）
            remark = f"{name}_{colo}"
            
            # 构造 VLESS 链接
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)

    # 已根据要求移除“域名保底”项

    if not links:
        print("未抓取到有效节点")
        return

    # Base64 编码
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    # 写入 sub.txt
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    
    print(f"成功更新 sub.txt，共生成 {len(links)} 个节点，格式为 线路_Colo")

if __name__ == "__main__":
    main()
