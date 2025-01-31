import os
import textract
from lightrag import LightRAG
from lightrag.llm import hf_model_complete, hf_embedding
from lightrag.utils import EmbeddingFunc

def calling_vector_db(category, channel_num):    
    db_path = f'DB/{category}_{channel_num}/{category}_{channel_num}_db'
    if not os.path.exists(db_path):
        os.mkdir(db_path)
    return db_path
    
def calling_rag(db_path, model, tokenizer):    
    rag = LightRAG(
        working_dir=db_path,
        llm_model_func=hf_model_complete,
        llm_model_name='meta-llama/Llama-3.2-3B-Instruct',
        embedding_func=EmbeddingFunc(
            embedding_dim=384,
            max_token_size=5000,
            func=lambda texts: hf_embedding(
                texts,
                tokenizer=tokenizer,
                embed_model=model
            )
        ),
    )
    
    return rag

def insert_rag(category, channel_num, model, tokenize):
    db_path = calling_vector_db(category, channel_num)
    stt_path = f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.txt'
    recommend_path = f'DB/{category}_{channel_num}/recommend_file.csv'
    rag = calling_rag(db_path, model, tokenize)
    with open(stt_path) as f:
        rag.insert(f.read())
    text_content = textract.process(recommend_path)
    rag.insert(text_content.decode('utf-8'))