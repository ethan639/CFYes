import requests
import base64
import json
import os

# ================= 配置区 =================
# UUID 和 HOST 已按要求更新
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")
HOST = os.environ.get("HOST", "gvm.cotco.dns-dynamic.net")
# ==========================================

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

    # 1. 汇总所有线路的 IP 数据到一个列表中
    raw_ips = []
    lines_map = {"CM": "移动", "CU": "联通", "CT": "电信"}
    
    info = res.get("info", {})
    for code, name in lines_map.items():
        line_data = info.get(code, [])
        for item in line_data:
            # 将线路名称注入每个 item，方便后续生成备注
            item['line_name'] = name
            raw_ips.append(item)

    # 2. 根据延迟 (latency) 进行排序
    # 提取数字部分进行比较，例如 "53ms" -> 53
    def get_latency_val(x):
        try:
            return int(x.get("latency", "999").replace("ms", ""))
        except:
            return 999

    sorted_ips = sorted(raw_ips, key=get_latency_val)

    # 3. 生成 VLESS 链接
    links = []
    for item in sorted_ips:
        ip = item.get("ip")
        name = item.get("line_name")
        colo = item.get("colo", "Unknown")
        latency = item.get("latency", "")
        
        if not ip:
            continue
        
        # 备注格式: 移动_LAX_53ms (增加延迟显示更直观)
        remark = f"{name}_{colo}_{latency}"
        
        # 构造链接
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        links.append(link)

    if not links:
        print("没有抓取到节点")
        return

    # 4. Base64 编码并保存
    combined = "\n".join(links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_sub)
    
    print(f"成功更新 sub.txt！已根据延迟对 {len(links)} 个节点进行排序。")

if __name__ == "__main__":
    main()
