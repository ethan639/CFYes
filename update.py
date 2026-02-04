import requests
import base64
import json
import os

# ================= 配置区 (已按要求更新) =================
# UUID: 63e36f02-9f04-4c72-b6b3-ccf59a72fff0
# HOST: gvm.cotco.dns-dynamic.net
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")
HOST = os.environ.get("HOST", "gvm.cotco.dns-dynamic.net")
# ========================================================

PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 

def get_optimization_ip():
    """从 hostmonit 获取优选 IP 数据"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    headers = {'Content-Type': 'application/json'}
    data = {"key": KEY, "type": "v4"}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"获取 IP 失败: {e}")
    return None

def main():
    res = get_optimization_ip()
    if not res or res.get("code") != 200:
        print("API 返回异常，请检查网络或 KEY")
        return

    links = []
    lines_map = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    # 解析三网数据并生成格式为“线路_Colo”的 VLESS 链接
    for code, name in lines_map.items():
        ip_info = res.get("info", {}).get(code, [])
        for item in ip_info:
            ip = item.get("ip")
            # 提取 Colo 信息 (LAX, HKG 等)
            colo = item.get("colo", "Unknown")
            if not ip:
                continue
            
            # 备注格式: 移动_LAX
            remark = f"{name}_{colo}"
            
            # 核心链接参数：
            # Address -> 优选IP
            # Port -> 443
            # SNI & Host -> 新域名 (gvm.cotco.dns-dynamic.net)
            link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
            links.append(link)

    if not links:
        print("没有抓取到节点，不执行更新")
        return

    # 进行 Base64 编码以适配 v2rayN 订阅格式
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    
    print(f"sub.txt 已更新！UUID 和 HOST 已同步。共生成 {len(links)} 个节点。")

if __name__ == "__main__":
    main()
