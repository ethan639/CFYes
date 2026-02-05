import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
# 1. 你的 UUID，建议在 GitHub Secrets 中设置
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")

# 2. 目标域名（HOST/SNI）
HOST = "gvm.cotco.dns-dynamic.net" 

# 3. 其他固定参数
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_data(ip_type='v4'):
    """从 API 获取优选 IP 数据"""
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"请求 {ip_type} 失败: {e}")
    return None

def main():
    # 生成北京时间戳用于节点备注
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    seen_ips = set() # 用于全局去重，防止重复 IP 出现
    
    # 依次处理 IPv4 和 IPv6 
    for ip_ver in ['v4', 'v6']:
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            continue

        info = res.get("info", {})
        # 严格按照：移动(CM) -> 电信(CT) 的顺序处理
        for code, name in [("CM", "移动"), ("CT", "电信")]:
            line_data = info.get(code) or info.get(code.lower())
            if not line_data or not isinstance(line_data, list):
                continue
            
            for item in line_data:
                ip = item.get("ip")
                # 过滤空 IP 或重复 IP
                if not ip or ip in seen_ips:
                    continue
                
                seen_ips.add(ip) 
                
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                lat_raw = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                
                # 构造节点别名
                remark = f"{name}_{tag}_{colo}_{lat_raw}ms_{beijing_time}"
                # 处理 IPv6 地址的方括号格式
                address = f"[{ip}]" if ":" in ip else ip
                
                # 拼接 VLESS 链接
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        # 1. 拼接明文内容并去除首尾空白
        content = "\n".join(all_links).strip()
        
        # 2. 进行 Base64 编码
        encoded_bytes = base64.b64encode(content.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        
        # 3. 【核心优化】彻底移除编码后字符串中所有的换行、回车和空格
        # 这样生成的 sub.txt 会是纯粹的一行长字符串，100% 解决 v2rayN 导入失败报错
        final_content = "".join(encoded_str.split())
        
        # 4. 写入文件
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(final_content)
            
        print(f"[{beijing_time}] 更新成功，共生成 {len(all_links)} 个节点。")
    else:
        print("未发现有效节点数据，请检查 API 或 KEY 是否过期。")

if __name__ == "__main__":
    main()
