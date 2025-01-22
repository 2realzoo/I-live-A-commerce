import os
import textract
import nest_asyncio
import asyncio
from lightrag import LightRAG
from lightrag.llm import hf_model_complete, hf_embedding
from transformers import AutoModel, AutoTokenizer
from lightrag.utils import EmbeddingFunc

def calling_vector_db(category, channel_num):    
    db_path = f'DB/{category}_{channel_num}/{category}_{channel_num}_db'
    if not os.path.exists(db_path):
        os.mkdir(db_path)
    return db_path
    
def calling_rag(db_path):    
    rag = LightRAG(
        working_dir=db_path,
        llm_model_func=hf_model_complete,
        llm_model_name='meta-llama/Llama-3.2-3B-Instruct',
        embedding_func=EmbeddingFunc(
            embedding_dim=384,
            max_token_size=5000,
            func=lambda texts: hf_embedding(
                texts,
                tokenizer=AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'),
                embed_model=AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            )
        ),
    )
    
    return rag

def insert_recommend_rag(category, channel_num):
    db_path = calling_vector_db(category, channel_num)
    recommend_path = f'DB/{category}_{channel_num}/recommend_file.csv'
    text_content = textract.process(recommend_path)
    rag = calling_rag(db_path)
    rag.insert(text_content.decode('utf-8'))
    
async def insert_stt_rag(category, channel_num):
    db_path = calling_vector_db(category, channel_num)
    stt_path = f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.txt'
    rag = calling_rag(db_path)
    nest_asyncio.apply()
    
    with open(stt_path) as f:
        rag.insert(f.read())
        
if __name__ == '__main__':
    asyncio.run(insert_stt_rag(7,1539266))