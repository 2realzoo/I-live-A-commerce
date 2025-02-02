import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from live_streaming import channels
from live_stt import voice2text
from live_rag import insert_rag
from live_summarization import run_summary
from live_ner import ner_predict
from live_recommend import recommend

category_map = {
    '뷰티' : 1,
    '푸드' : 2,
    '패션' : 3,
    '라이프' : 4,
    '여행/체험' : 5,
    '키즈' : 6,
    '테크' : 7,
    '취미레저' : 8,
    '문화생활' : 9 
}

def update(category_str, channel):
    category = category_map.get(category_str, 0)
    channel_num = channel
    
    voice2text(category, channel_num) 
    
    summ = run_summary(category, channel_num)
    topic = ner_predict(summ)
    recommend(category, channel_num, topic, topic)
    insert_rag(category, channel_num)
    
async def sync_db(scheduler):
    exisiting_jobs = set()
    
    while True:
        current_jobs = {(ch['Category'], ch['Channel']) for ch in channels}
        
        new_jobs = current_jobs - exisiting_jobs
        for category, channel in new_jobs:
            job_id = f'{category}_{channel}'
            scheduler.add_job(
                update,
                'interval', 
                seconds = 100, 
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
    #일정 주기마다 돌아갈 수 있도록 만듦
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    asyncio.create_task(sync_db(scheduler)) #AI Update 함수
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=1800) 