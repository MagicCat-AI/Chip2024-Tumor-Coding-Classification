import re

def check_is_isolated(key,query):
    # 使用正则表达式检查 NK 是否是独立的单词
    pattern = r'(?<![a-zA-Z])'+key+'(?![a-zA-Z])'
    match = re.search(pattern, query)

    return match is not None  # 返回是否匹配成功


def contains_keywords(key,query):
    text = query.lower()
    for keyword in key:
        if keyword in text:
            return True  # 找到关键词，返回True和关键词
    return False  # 未找到关键词，返回False
def ICD_O_H_api_rag(query):
    pp = '9'
    if 'NK' in query:
        if check_is_isolated('NK',query) == True:
            pp = '8'
            return pp
    # 检测 7
    elif 'ALK' in query:
        if check_is_isolated('ALK', query) == True:
            pp = '7'
            return pp
    # 检测 5
    elif 'T' in query:
        if check_is_isolated('T', query) == True:
            pp = '5'
            return pp
    # 检测 6
    elif 'B' in query:
        if check_is_isolated('B', query) == True:
            pp = '6'
            if contains_keywords(['腺泡腺癌','原发性中枢神经系统淋巴瘤','淋巴组织'], query) == True:
                pp = '9'
                return pp
            return pp
    return pp