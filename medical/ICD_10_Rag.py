from typing import List
import jieba
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from api import chat
from rank_bm25 import BM25Okapi


def preprocessing_func(text: str) -> List[str]:
    """
    使用jieba对文本进行分词处理

    参数:
    text (str): 需要分词的文本

    返回:
    List[str]: 分词后的结果列表
    """
    return list(jieba.cut(text))


### 加载文档
# 使用TextLoader加载ICD-10.txt文件
loader = TextLoader(r'ICD-10.txt', encoding='utf-8')
documents = loader.load()

# 使用RecursiveCharacterTextSplitter将文档分割成小块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # 每个块的最大长度
    chunk_overlap=0,  # 块之间的重叠部分
    length_function=len,  # 计算长度的函数
    separators=['\n']  # 分割符
)
docs = text_splitter.split_documents(documents)

# 提取每个文档的内容
texts = [i.page_content for i in docs]

# 对每个文档内容进行预处理（分词）
texts_processed = [preprocessing_func(t) for t in texts]

# 使用BM25Okapi创建一个BM25索引
vectorizer = BM25Okapi(texts_processed)

# 使用HuggingFaceEmbeddings创建一个嵌入模型
embeddings = HuggingFaceEmbeddings(model_name='gte-large-zh')

# 使用FAISS从文档和嵌入模型创建向量存储
db = FAISS.from_documents(docs, embeddings)
# 保存FAISS向量存储到本地
db.save_local('FAISS')


def rrf(vector_results: List[str], text_results: List[str], k: int = 30, m: int = 60):
    """
    使用RRF算法对两组检索结果进行重排序

    参数:
    vector_results (List[str]): 向量召回的结果列表,每个元素是文档ID
    text_results (List[str]): 文本召回的结果列表,每个元素是文档ID
    k (int): 排序后返回前k个
    m (int): 超参数

    返回:
    重排序后的结果列表,每个元素是(文档ID, 融合分数)
    """
    doc_scores = {}

    # 遍历两组结果,计算每个文档的融合分数
    for rank, doc_id in enumerate(vector_results):
        doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1 / (rank + m)
    for rank, doc_id in enumerate(text_results):
        doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1 / (rank + m)

    # 将结果按融合分数排序
    sorted_results = [d for d, _ in sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:k]]

    return sorted_results


def ICD_10_api_rag(query: str, type: str):
    """
    根据查询和类型，使用BM25和向量搜索进行文档检索，并通过RRF算法融合结果，最后调用chat API生成回答

    参数:
    query (str): 用户查询
    type (str): 查询类型

    返回:
    res (str): 生成的回答
    """
    # 使用BM25获取top n个相关文档
    bm25_res = vectorizer.get_top_n(preprocessing_func(query), texts, n=40)

    # 使用向量搜索获取top k个相关文档
    vector_res = db.similarity_search(query, k=40)
    vector_results = [i.page_content for i in vector_res]

    # 获取BM25检索结果
    text_results = [i for i in bm25_res]

    # 使用RRF算法融合两组检索结果
    rrf_res = rrf(vector_results, text_results)

    # 构建提示模板
    prompt = '''
    任务目标：根据病人的病理{}并根据检索出的{}文档分析病人的{}
    任务要求：
        1、先分析病人的病理分期再结合文档回答问题
        2、病人的{}只存在一个
        3、若检索出的文档不包含用户问题的答案，你必须选择一个检索结果
        4、要求更加具体地选择而不是更加广泛地选择
    检索出的文档：
    {}
    '''

    # 调用chat API生成回答
    res = chat(prompt.format(query, type, type, type, ''.join(rrf_res)))
    return res