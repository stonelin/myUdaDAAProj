# coding=utf8

from datetime import datetime
import xml.etree.cElementTree as ET
import re


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
chinese_words = re.compile(r'[\u4E00-\u9FFF]+')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# 菜系异常数据字典
CUISINE_LAN_MAPPING = {
    "Chinese_food": "chinese"
}
# 街道异常数据字典
STREET_LAN_MAPPING = {
    "光明zhong jie": "光明中街",
    "St. Shuangqiao": "双桥路",
    "Santilun West 6th Street": "三里屯西六街",
    "Xizhaosi Street": "夕照寺街",
    "Agricultural Exhibition Center":"农业展览馆",
    "Xierqi": "西二旗",
}
# 地址缩写 mapping
STREET_ABBR_MAPPING = {
    "St": "Street",
    "St.": "Street",
    "Ave": "Avenue",
    "Rd.": "Road",
    "road": "Road",
    "Str": "Street",
    "ave.": "Avenue"
}


# 处理菜系数据
def handle_cuisine(value):
    res = []
    for x in value.split(";"):
        if "中餐" in x:
            res.append("chinese")
        elif "饺子" in x:
            res.append("chinese")
        else:
            res.append(CUISINE_LAN_MAPPING.get(x, x))
    return res


def update_street_type(name):
    res = street_type_re.search(name)
    if not res:
        return name
    k = res.group()
    if k in STREET_ABBR_MAPPING:
        return street_type_re.sub(STREET_ABBR_MAPPING.get(k, k), name)
    else:
        return name


def handle_street(value):
    if not chinese_words.search(value):
        value = update_street_type(value)
    return STREET_LAN_MAPPING.get(value, value).strip()


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node["id"] = element.get("id")
        node["type"] = element.tag
        # node["visible"] = element.get("visible")

        node["created"] = {}
        node["created"]["version"] = int(element.get("version"))
        node["created"]["changeset"] = element.get("changeset")
        node["created"]["timestamp"] = datetime.strptime(element.get("timestamp"), "%Y-%m-%dT%H:%M:%SZ")
        node["created"]["user"] = element.get("user")
        node["created"]["uid"] = int(element.get("uid"))

        if element.get("lat") and element.get("lon"):
            node["pos"] = [float(element.get("lat")), float(element.get("lon"))]
        for tag in element.iter("tag"):
            k = tag.get("k")
            # print(k)
            if problemchars.search(k):
                continue
            if k == "cuisine":
                node["cuisine"] = handle_cuisine(tag.get("v"))
                continue
            elif ":" not in k:
                node[k] = tag.get("v")
            elif k.startswith("addr:"):
                node.setdefault("address", {})
                if k == "addr:street":
                    node["address"]["street"] = handle_street(tag.get("v"))
                else:
                    node["address"][k.split(":", 1)[1]] = tag.get("v")
        refs = [x.get("ref") for x in element.iter("nd")]
        if refs:
            node["node_refs"] = refs
        
        return node
    else:
        return None