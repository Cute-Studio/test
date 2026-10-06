import requests
import json
import time
from urllib.parse import urlencode, urlparse, parse_qs

def build_gacha_url(base_url: str, params: dict) -> str:
    """拼接原神抽卡API完整链接，自动url编码参数"""
    query_str = urlencode(params)
    if "?" in base_url:
        full_url = f"{base_url}&{query_str}"
    else:
        full_url = f"{base_url}?{query_str}"
    return full_url


# ====================== 在这里修改你的参数 ======================
base_url = "https://public-operation-hk4e.mihoyo.com/gacha_info/api/getGachaLog"

param_dict = {
    "authkey_ver": 1,
    "sign_type": 2,
    "lang": "zh-cn",
    "region": "cn_gf01",
    "authkey": "API密钥",#填入原本密钥就行
    "game_biz": "hk4e_cn",
    "gacha_type": 301,#卡池ID
    "page": 1,#没啥用，但是由于是山代码不留着，可能会崩
    "size": 20,#每次输出的数量
    "end_id": 0
}
# 自动拼接生成完整链接
full_url = build_gacha_url(base_url, param_dict)
# ==============================================================


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

all_records = []
current_end_id = "0"

while True:
    # 修改end_id参数（解析URL方式，比字符串replace更可靠）
    url_parts = urlparse(full_url)
    query = parse_qs(url_parts.query)
    query["end_id"] = [current_end_id]
    new_query = urlencode(query, doseq=True)
    req_url = url_parts._replace(query=new_query).geturl()

    resp = requests.get(req_url, headers=headers, timeout=20)
    res_json = resp.json()
    print("本次请求返回：", res_json)

    if res_json["retcode"] != 0:
        print(f"接口错误，停止")
        break

    record_list = res_json["data"]["list"]
    if not record_list:
        print("全部记录拉取完毕")
        break

    all_records.extend(record_list)
    current_end_id = record_list[-1]["id"]
    print(f"累计获取：{len(all_records)} 条")
    time.sleep(1)

out_data = {
    "gacha_type": "301",
    "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total": len(all_records),
    "list": all_records
}

with open("genshin_wish_result.json", "w", encoding="utf-8") as f:
    json.dump(out_data, f, ensure_ascii=False, indent=2)

print("导出完成！文件 genshin_wish_result.json")
