from typing import List
import jieba
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from api import chat
from rank_bm25 import BM25Okapi

def preprocessing_func(text: str) -> List[str]:
    return list(jieba.cut(text))

###加载文档
loader = TextLoader(r'ICD-O-M.txt', encoding='utf-8')
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0,
    length_function=len,
    separators=['\n']
)
docs = text_splitter.split_documents(documents)


texts = [i.page_content for i in docs]
texts_processed = [preprocessing_func(t) for t in texts]
vectorizer = BM25Okapi(texts_processed)
embeddings = HuggingFaceEmbeddings(model_name='gte-large-zh')


db = FAISS.from_documents(docs, embeddings)
db.save_local('FAISS')




def rrf(vector_results: List[str], text_results: List[str], k: int = 30, m: int = 60):
    """
    使用RRF算法对两组检索结果进行重排序

    params:
    vector_results (list): 向量召回的结果列表,每个元素是专利ID
    text_results (list): 文本召回的结果列表,每个元素是专利ID
    k(int): 排序后返回前k个
    m (int): 超参数

    return:
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
def ICD_O_M_api_rag(query,type):
    bm25_res = vectorizer.get_top_n(preprocessing_func(query), texts, n=40)
    vector_res = db.similarity_search(query, k=40)
    vector_results = [i.page_content for i in vector_res]
    text_results = [i for i in bm25_res]
    rrf_res = rrf(vector_results, text_results)
    prompt = '''
    任务目标：根据病人的病理分期{}并根据检索出的{}文档分析病人的{}
    任务要求：
        1、先分析病人的病理分期再结合文档回答问题
        2、病人的{}只存在一个
        3、若检索出的文档不包含用户问题的答案，你必须选择一个检索结果
        4、要求更加具体地选择而不是更加广泛地选择
    检索出的文档：
    {}
    '''

    res = chat(prompt.format(query,type,type,type, ''.join(rrf_res)))
    return res


