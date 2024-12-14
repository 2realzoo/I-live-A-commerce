import os
import textract
import nest_asyncio
from lightrag import LightRAG
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc

def calling_vector_db(category, channel_num):    
    db_path = f'./{category}_{channel_num}/{category}_{channel_num}_db'
    if not os.path.exists(db_path):
        os.mkdir(db_path)
    return db_path
    
def calling_rag(db_path):    
    rag = LightRAG(
        working_dir=db_path,
        llm_model_func=ollama_model_complete,
        llm_model_name='',
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embedding(
                texts,
                embed_model='nomic-embed-text'
            )
        ),
    )
    
    return rag

def insert_recommend_rag(category, channel_num):
    db_path = calling_vector_db(category, channel_num)
    recommend_path = f'{category}_{channel_num}/recommend_file.csv'
    text_content = textract.process(recommend_path)
    rag = calling_rag(db_path)
    nest_asyncio.apply()
    rag.insert(text_content.decode('utf-8'))
    
def insert_stt_rag(category, channel_num):
    db_path = calling_vector_db(category, channel_num)
    stt_path = f'{category}_{channel_num}/streaming_{category}_{channel_num}.txt'
    rag = calling_rag(db_path)
    nest_asyncio.apply()
    
    with open(stt_path) as f:
        rag.insert(f.read())
        