import requests
import base64
import os
from datetime import datetime, timedelta

# ================= 配置区 =================
USER_ID = os.environ.get("USER_ID", "63e36f02-9f04-4c72-b6b3-ccf59a72fff0")
HOST = os.environ.get("HOST", "gvm.cotco.dns-dynamic.net")
PATH = "/"
PORT = 443
KEY = "o1zrmHAF" 
# ==========================================

def get_data(ip_type='v4'):
    url = 'https://api.hostmonit.com/get_optimization_ip'
    data = {"key": KEY, "type": ip_type}
    try:
        response = requests.post(url, json=data, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            # 打印详细日志，方便在 Action 中排查数据缺失
            print(f"[{ip_type}] API 返回代码: {res_json.get('code')}")
            return res_json
    except Exception as e:
        print(f"[{ip_type}] 请求异常: {e}")
    return None

def main():
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
    all_links = []
    
    # 定义需要抓取的运营商映射
    lines_to_fetch = [("CM", "移动"), ("CU", "联通"), ("CT", "电信")]
    
    for ip_ver in ['v4', 'v6']:
        print(f"开始抓取 {ip_ver} 数据...")
        res = get_data(ip_ver)
        if not res or res.get("code") != 200:
            print(f"跳过 {ip_ver}: 接口无响应或 Key 错误")
            continue
            
        info = res.get("info", {})
        
        # 严格按照：移动 -> 联通 -> 电信 顺序排列
        for code, name in lines_to_fetch:
            # 兼容性处理：如果 info 中不存在该 key，则尝试小写或跳过
            line_data = info.get(code) or info.get(code.lower())
            
            if not line_data or not isinstance(line_data, list):
                print(f" ! 警告: {ip_ver} 中未找到 {name} 数据")
                continue
            
            print(f" + 成功抓取 {ip_ver} {name}: {len(line_data)} 个 IP")
            
            for item in line_data:
                ip = item.get("ip")
                if not ip: continue
                
                # 别名组件及格式处理
                tag = "IPv4" if ip_ver == 'v4' else "IPv6"
                colo = item.get("colo", "Default")
                lat_raw = str(item.get("latency", "Unknown")).lower().replace("ms", "")
                
                # 严格执行要求格式：线路名_IP版本_地区_延迟ms_时间
                remark = f"{name}_{tag}_{colo}_{lat_raw}ms_{beijing_time}"
                address = f"[{ip}]" if ":" in ip else ip
                
                link = f"vless://{USER_ID}@{address}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
                all_links.append(link)

    if all_links:
        content = "\n".join(all_links)
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))
        print(f"[{beijing_time}] 全部更新完成，共生成 {len(all_links)} 个节点")
    else:
        print("错误: 未能抓取到任何有效节点，请确认 API KEY 额度")

if __name__ == "__main__":
    main()
