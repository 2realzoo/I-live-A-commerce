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
from live_sentiment import process_and_calculate_score
import torch 

def clear_cuda_memory():
    """CUDA 메모리 정리 함수."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        print("[INFO] CUDA 메모리가 초기화되었습니다.")
        
def update(category_str, channel):

    category = category_map.get(category_str, 0)
    channel_num = channel
    
    voice2text(category, channel_num) 
    clear_cuda_memory()
    summ = run_summary(category, channel_num)
    clear_cuda_memory()
    print(f'요약 : {category}_{channel_num}' , summ)
    topic = ner_predict(summ)
    clear_cuda_memory()
    print(f'토픽 : {category}_{channel_num}', topic)
    recommend(category, channel_num, topic, topic)
    clear_cuda_memory()
    sentiment_score = process_and_calculate_score(category, channel_num)
    clear_cuda_memory()
    print(f'점수 : {category}_{channel_num}',sentiment_score)
    insert_rag(category, channel_num)
    clear_cuda_memory()
    
    
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
                seconds = 210, 
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
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    asyncio.create_task(sync_db(scheduler))
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=1703) 