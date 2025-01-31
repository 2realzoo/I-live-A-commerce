import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from live_streaming import load_channels
from live_stt import voice2text
from live_summarization import run_summary
from live_ner import ner_predict
from live_recommend import recommend
from live_rag import insert_rag
from category_map import category_map
from live_sentiment import run_sentiment_score
import torch 
from transformers import (AutoModelForSpeechSeq2Seq, 
                          AutoProcessor, 
                          PreTrainedTokenizerFast, 
                          BartForConditionalGeneration, 
                          AutoTokenizer, 
                          BertForTokenClassification,
                          AutoModelForCausalLM,
                          AutoTokenizer,
                          AutoModel
                          )
import kss

    
def update(category_str, channel):
    category = category_map.get(category_str, 0)
    channel_num = channel
    
    voice2text(category, channel_num, stt_model, stt_processor) 
    summ = run_summary(category, channel_num, summary_model, summary_tokenizer)
    print(f'요약 : {category}_{channel_num}' , summ)
    
    topic = ner_predict(summ, ner_model, ner_tokenizer, splitter)
    print(f'토픽 : {category}_{channel_num}', topic)
    
    recommend(category, channel_num, topic, topic)
    
    sentiment_score = run_sentiment_score(category, channel_num, sent_model, sent_tokenizer)
    print(f'점수 : {category}_{channel_num}',sentiment_score)
    
    insert_rag(category, channel_num, rag_model, rag_tokenizer)
    
    # CUDA 메모리 정리
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    
async def sync_db(scheduler):
    exisiting_jobs = set()
    
    while True:
        channels = load_channels()
        current_jobs = {(ch['Category'], ch['Channel']) for ch in channels}
        
        new_jobs = current_jobs - exisiting_jobs
        for category, channel in new_jobs:
            job_id = f'{category}_{channel}'
            scheduler.add_job(
                update,
                'interval', 
                seconds = 90, 
                args = [category, channel],
                id = job_id
            )

        removed_jobs = exisiting_jobs - current_jobs
        for category, channel in removed_jobs:
            job_id = f'{category}_{channel}'
            scheduler.remove_job(job_id)
            
        exisiting_jobs = current_jobs
        
        await asyncio.sleep(5)

@asynccontextmanager
async def stream(app:FastAPI):
    global stt_model, stt_processor, summary_model, summary_tokenizer, ner_model, ner_tokenizer, sent_model, sent_tokenizer, rag_model, rag_tokenizer, splitter
    
    print("[INFO] 모델 로드 시작...")

    # GPU 0번 할당
    device0 = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] STT 모델 로드 중... (GPU 0)")
    stt_model = AutoModelForSpeechSeq2Seq.from_pretrained(
        'openai/whisper-large-v3', torch_dtype=torch.float16, use_safetensors=True
    ).to(device0).half()
    stt_processor = AutoProcessor.from_pretrained('openai/whisper-large-v3')

    print(f"[INFO] 요약 모델 로드 중... (GPU 0)")
    summary_model = BartForConditionalGeneration.from_pretrained("EbanLee/kobart-summary-v3").to(device0).half()
    summary_tokenizer = PreTrainedTokenizerFast.from_pretrained("EbanLee/kobart-summary-v3")

    # GPU 1번 할당
    device1 = "cuda:1" if torch.cuda.device_count() > 1 else "cuda:0"
    print(f"[INFO] NER 모델 로드 중... (GPU 1)")
    ner_model = BertForTokenClassification.from_pretrained("KPF/KPF-bert-ner").to(device1).half()
    ner_tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")

    print(f"[INFO] 감성 분석 모델 로드 중... (GPU 1)")
    checkpoint_path = "/home/metaai2/jinjoo_work/llama_finetuning/sentiment/llama3.2-3b-sentiment-2"
    base_model = "Bllossom/llama-3.2-Korean-Bllossom-3B"
    sent_model = AutoModelForCausalLM.from_pretrained(checkpoint_path).to(device1).half()
    sent_tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    print(f"[INFO] RAG 모델 로드 중... (GPU 1)")
    rag_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2').to(device1).half()
    rag_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

    splitter = kss.split_sentences
    
    print("[INFO] 모든 모델 로드 완료!")
    
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    asyncio.create_task(sync_db(scheduler))
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=1703) 