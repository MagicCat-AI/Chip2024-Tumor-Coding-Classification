import json
import re
from ICD_O_H_Rag import ICD_O_H_api_rag
from ICD_O_M_Rag import ICD_O_M_api_rag
from api import pathological_classification, pathological_classification_plus, \
    ICD_10_classification_plus, ICD_O_M_classification_plus
from ICD_10_Rag import ICD_10_api_rag


def extract_10_codes(text):
    """
    从文本中提取符合 Cxx.x 格式的 ICD-10 代码。

    参数:
    text (str): 输入的文本

    返回:
    str: 提取到的第一个匹配的 ICD-10 代码
    """
    # 定义匹配模式，匹配 C 字母后面跟随两位数字和一个点的格式
    pattern = r'C\d{2}\.\d'

    # 使用正则表达式查找所有匹配的部分
    matches = re.findall(pattern, text)

    # 返回第一个匹配的结果
    return matches[0] if matches else None


def extract_M_code(text):
    """
    从文本中提取符合 xxxx/x 格式的 ICD-O-M 代码。

    参数:
    text (str): 输入的文本

    返回:
    str: 提取到的第一个匹配的 ICD-O-M 代码
    """
    # 定义匹配模式，匹配四位数字和斜杠的组合
    pattern = r'\b\d{4}/\d\b'

    # 使用正则表达式查找所有匹配的部分
    matches = re.findall(pattern, text)

    # 返回第一个匹配的结果
    return matches[0] if matches else None


# JSON 文件路径
file_path = 'test_b.json'

# 存储结果的列表
results = []

# 读取 JSON 文件
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 遍历数据
i = 0
for item in data:
    i += 1
    print(f'{i}/{len(data)}')

    # 初始化结果字典
    result = {}
    id = i
    text = item['text']
    result['id'] = str(id)  # ID
    result['date_of_first_diagnosis'] = ''  # 初次诊断日期
    result['gender'] = ''  # 性别
    result['location'] = ''  # 位置
    result['ICD-O-P'] = ''  # ICD-O-P

    ###### 病理分类
    try:
        # 初次提取病理分类
        result['pathological_classification'] = pathological_classification(text)

        # 再次提取病理分类
        result['pathological_classification'] = \
        pathological_classification_plus(result['pathological_classification']).tool_calls[0].function.arguments

        # 解析 JSON 字符串
        pathological_classification_string = json.loads(result['pathological_classification'])

        # 提取 "pathological_classification" 对应的文本
        classification = pathological_classification_string["pathological_classification"]
        result['pathological_classification'] = classification
    except Exception as e:
        result['pathological_classification'] = None
        print(f'Pathological classification error: {e}')
    print(f'Pathological classification for case {result["id"]} is {result["pathological_classification"]}')

    ###### ICD-10
    try:
        # 初次提取 ICD-10 分类
        result['ICD-10'] = ICD_10_api_rag(result['pathological_classification'], 'ICD-10')

        # 再次提取 ICD-10 分类
        result['ICD-10'] = ICD_10_classification_plus(result['ICD-10']).tool_calls[0].function.arguments

        # 解析 JSON 字符串
        ICD_10_classification_string = json.loads(result['ICD-10'])

        # 提取 "ICD_10_classification" 对应的文本
        classification = ICD_10_classification_string["ICD_10_classification"]
        result['ICD-10'] = classification
    except Exception as e:
        result['ICD-10'] = None
        print(f'ICD-10 classification error: {e}')

    # 提取 ICD-10 代码
    result['ICD-10'] = extract_10_codes(result['ICD-10'])
    print(f'Final extracted ICD-10 code for case {result["id"]} is {result["ICD-10"]}')

    ###### ICD-O-M
    try:
        # 初次提取 ICD-O-M 分类
        result['ICD-O-M'] = ICD_O_M_api_rag(result['pathological_classification'], 'ICD-O-M')

        # 再次提取 ICD-O-M 分类
        result['ICD-O-M'] = ICD_O_M_classification_plus(result['ICD-O-M']).tool_calls[0].function.arguments

        # 解析 JSON 字符串
        ICD_O_M_classification_string = json.loads(result['ICD-O-M'])

        # 提取 "ICD_O_M_classification" 对应的文本
        classification = ICD_O_M_classification_string["ICD_O_M_classification"]
        result['ICD-O-M'] = classification
    except Exception as e:
        result['ICD-O-M'] = None
        print(f'ICD-O-M classification error: {e}')

    # 提取 ICD-O-M 代码
    result['ICD-O-M'] = extract_M_code(result['ICD-O-M'])
    print(f'Final extracted ICD-O-M code for case {result["id"]} is {result["ICD-O-M"]}')

    ###### ICD-O-H
    try:
        # 初次提取 ICD-O-H 分类
        result['ICD-O-H'] = ICD_O_H_api_rag(result['pathological_classification'])
    except Exception as e:
        result['ICD-O-H'] = None
        print(f'ICD-O-H classification error: {e}')

    # 打印最终提取的 ICD-O-H 代码
    print(f'Final extracted ICD-O-H code for case {result["id"]} is {result["ICD-O-H"]}')

    # 将结果添加到结果列表
    results.append(result)

# 将结果写入 JSON 文件
with open('result.json', 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, indent=4)