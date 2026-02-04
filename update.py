import base64

# ================= 配置区 =================
USER_ID = "f4055c9e-8500-4638-b13a-0e65fec24936"
HOST = "cs.cotco.dns-dynamic.net" # 保持使用你已设置的 CNAME 子域名
PATH = "/"  
PORT = 443

# 直接从你的截图 20.png 中提取的高质量优选 IP
STATIC_IPS = [
    {"ip": "141.101.114.165", "loc": "香港_移动", "ms": "55"},
    {"ip": "198.41.208.196", "loc": "香港_移动", "ms": "52"},
    {"ip": "141.101.115.104", "loc": "香港_联通", "ms": "52"},
    {"ip": "198.41.208.70", "loc": "香港_联通", "ms": "52"},
    {"ip": "104.25.199.208", "loc": "法郎_电信", "ms": "161"},
    {"ip": "172.67.252.93", "loc": "加速器_电信", "ms": "161"}
]
# ==========================================

def main():
    vless_links = []
    
    # 循环生成基于真实优选 IP 的节点
    for item in STATIC_IPS:
        ip = item['ip']
        remark = f"优选_{item['loc']}_{item['ms']}ms"
        # 核心：将服务器地址直接设为优选 IP，SNI 设为你的域名
        link = f"vless://{USER_ID}@{ip}:{PORT}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={PATH}#{remark}"
        vless_links.append(link)

    # 编码并写入文件
    combined = "\n".join(vless_links)
    final_sub = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with open("sub.txt", "w") as f:
        f.write(final_sub)
    print(f"成功生成 {len(vless_links)} 个静态优选节点！")

if __name__ == "__main__":
    main()
