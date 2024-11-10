方法描述文档

1.方法说明

本方法旨在设计一个医疗Agent来完成编码分类任务，其包含一套RAG系统和基于概率统计的ICD-O-H分类方法，RAG系统先将我们提供的数据入库建立一个医疗编码向量库，其中包含病人的病例对应的ICD-10和ICD-O-M编码。

将病人病例输入给Agent，Agent会调用通义千问商业api‘quen-max’对医疗病例进行分析，提取具体的病理分期，再通过检索向量库和rrf算法召回确认病理分期对应的可能的所有编码并返回给Agent。

对于ICD-10和ICD-O-M编码：
Agent会对可能的所有编码进行具体的分析并确认最终的编码答案。

对于ICD-O-H编码：
Agent会根据基于概率统计的ICD-O-H分类方法来直接对病例进行ICD-O-H分类。





2.安装环境

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple







3.运行
将gte-large-zh权重下载到medical目录下的gte-large-zh目录中
先在api.py中填写你的智谱清言和通义千问APIkey
直接运行run.py





4.说明

若运行时出现报错，很有可能是因为网络问题，建议使用热点流量。