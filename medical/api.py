import json
from openai import OpenAI
from zhipuai import ZhipuAI

# API密钥
quen_key = ""#通义千问
glm_key = ""#智谱清言


def pathological_classification(r):
    """
    从病人的病例中提取并分析肿瘤或白血病的病理诊断。

    参数:
        r (str): 病人的病例描述。

    返回:
        str: 具体 的病理诊断结果。
    """
    prompt = '''
    任务目标：查看病人的病例并分析病人肿瘤的病例诊断
    任务要求：
        1、要求输出尽可能具体的病理诊断和病理分期
        2、病人的病理诊断应该为肿瘤类或者白血病类，如果出现其他类请再次分析病例
        3、如果讷有具体的细胞类型，请提供具体的细胞类型

    病人的病例：
    {}
    '''

    # 格式化提示语句，将病例信息插入到模板中
    prompt = prompt.format(r)

    # 初始化OpenAI客户端
    client = OpenAI(
        api_key=quen_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 发送请求给通义千问模型
    completion = client.chat.completions.create(
        model="qwen-max",  # 使用Qwen-Max模型
        messages=[
            {'role': 'user', 'content': prompt}
        ],
    )

    # 解析响应
    response = completion.model_dump_json()
    response = json.loads(response)
    result = response['choices'][0]['message']['content']
    return result


def pathological_classification_plus(r):
    """
    对病人的病理信息进行二次提取，以获取更详细的肿瘤病理诊断。

    参数:
        r (str): 病人的病例描述。

    返回:
        dict: 包含具体肿瘤病理诊断的结果。
    """
    client = ZhipuAI(api_key=glm_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_train_info",
                "description": "尽可能抽出病人具体的肿瘤病理诊断",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pathological_classification": {
                            "description": "肿瘤病理诊断",
                            "type": "string",
                        }
                    },
                    "required": ["pathological_classification"]
                },
            }
        },
    ]

    messages = [
        {
            "role": "user",
            "content": r
        }
    ]

    # 发送请求给GLM-4 Plus模型
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=messages,
        tools=tools,
    )

    # 提取响应中的消息内容
    result = response.choices[0].message
    return result


def chat(r):
    """
    与通义千问模型进行通用对话。

    参数:
        r (str): 用户输入的消息。

    返回:
        str: 模型生成的回复。
    """
    client = OpenAI(
        api_key=quen_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 发送请求给通义千问模型
    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {'role': 'user', 'content': r}
        ],
    )

    # 解析响应
    response = completion.model_dump_json()
    response = json.loads(response)
    result = response['choices'][0]['message']['content']
    return result


def ICD_10_classification_plus(r):
    """
    抽取病人的ICD-10编码。

    参数:
        r (str): 病人的病例描述。

    返回:
        dict: 包含ICD-10编码的结果。
    """
    client = ZhipuAI(api_key=glm_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_train_info",
                "description": "抽出病人病理最终的ICD-10编码",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ICD_10_classification": {
                            "description": "ICD-10编码",
                            "type": "string",
                        }
                    },
                    "required": ["ICD_10_classification"]
                },
            }
        },
    ]

    messages = [
        {
            "role": "user",
            "content": r
        }
    ]

    # 发送请求给GLM-4 Plus模型
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=messages,
        tools=tools,
    )

    # 提取响应中的消息内容
    result = response.choices[0].message
    return result


def ICD_O_M_classification_plus(r):
    """
    抽取病人的ICD-O-M编码。

    参数:
        r (str): 病人的病例描述。

    返回:
        dict: 包含ICD-O-M编码的结果。
    """
    client = ZhipuAI(api_key=glm_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_train_info",
                "description": "抽出病人病理最终的ICD-O-M编码",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ICD_O_M_classification": {
                            "description": "ICD-O-M编码",
                            "type": "string",
                        }
                    },
                    "required": ["ICD_O_M_classification"]
                },
            }
        },
    ]

    messages = [
        {
            "role": "user",
            "content": r
        }
    ]

    # 发送请求给GLM-4 Plus模型
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=messages,
        tools=tools,
    )

    # 提取响应中的消息内容
    result = response.choices[0].message
    return result


def ICD_O_H_classification_plus(r):
    """
    抽取病人的ICD-O-H编码。

    参数:
        r (str): 病人的病例描述。

    返回:
        dict: 包含ICD-O-H编码的结果。
    """
    client = ZhipuAI(api_key=glm_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_train_info",
                "description": "抽出文本最终的确认的编码数字",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ICD_O_H_classification": {
                            "description": "ICD-O-H编码",
                            "type": "string",
                        }
                    },
                    "required": ["ICD_O_H_classification"]
                },
            }
        },
    ]

    messages = [
        {
            "role": "user",
            "content": f'''
    任务目标：抽出文本最终的确认的编码数字
    任务要求：
        1、编码数字有5,6,7,8,9五种
        2、只需要抽出编码数字
    文本：
    {r}
    '''
        }
    ]

    # 发送请求给GLM-4 Plus模型
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=messages,
        tools=tools,
    )

    # 提取响应中的消息内容
    result = response.choices[0].message
    return result