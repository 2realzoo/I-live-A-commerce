import uvicorn
import asyncio
import os
from pathlib import Path
from fastapi import FastAPI, Form, BackgroundTasks, Body
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import FileResponse, JSONResponse
from live_streaming import main, channels
from live_stt import voice2text
from live_recommend import recommend
from live_rag import insert_stt_rag, insert_recommend_rag
from live_graph import run_cusum
from live_llm import calling_llm
from live_tts import run_tts

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


#패시브 작동
#방송당 300초 주기로 업데이트
def update(category_str, channel):
    category = category_map.get(category_str, 0)
    channel_num = channel
    
    #run_cusum(category, channel_num)
    
    #voice2text(category, channel_num) 
    #insert_stt_rag(category, channel_num)
    #summary generation 함수
    #NER함수
    #recommend(category, channel_num, entire_topic, detail_topic)
    #insert_recommend_rag(category, channel_num)    


async def sync_db(scheduler):
    exisiting_jobs = set()
    
    while True:
        current_jobs = {(ch['Category'], ch['Channel']) for ch in channels}
        
        new_jobs = current_jobs - exisiting_jobs
        for category, channel in new_jobs:
            job_id = f'{category}_{channel}'
            scheduler.add_job(
                update(category, channel), 
                'interval', 
                seconds = 300, 
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
    asyncio.create_task(main())
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    asyncio.create_task(sync_db(scheduler))
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)

@app.get('/home')
async def home():
    return JSONResponse(content=channels)
    

#유저에게 요청이 들어왔을때 작동
#def send_video(ts_file_path):
#    ts_files = [f for f in os.listdir(ts_file_path) if f.endswith('.ts')]
#    if not ts_files:
#        return None
#    ts_files.sort(key=lambda f: os.path.getmtime(os.path.join(ts_file_path, f)), reverse=True)
#    return os.path.join(ts_file_path, ts_files[0])

@app.post('/analysis')
async def analysis(request:dict=Body(...)):
    
    category_str = request.get('Category')
    category = category_map.get(category_str, 0)
    channel_num = request.get('Channel')

    #그래프 디스플레이
    graph_path = f'DB/{category}_{channel_num}/{category}_{channel_num}_graph.png'
    #감성 분석 디스플레이
    #감성 분석 함수
    
    return JSONResponse(content={'Chart':graph_path})
    
@app.post('chat/')
async def chat(request:dict=Body(...)):
    
    category_str = request.get('Category')
    category = category_map.get(category_str, 0)
    channel_num = request.get('Channel')
    
    input_txt = request.get('Text')
    output_txt = calling_llm(category, channel_num, input_txt)
    
    voice = request.get('Voice')
    who = request.get('Who')
    
    if voice == True:
        voice_complete = run_tts(category, channel_num, who, output_txt)
        if voice_complete:
            voice_path = f'DB/{category}_{channel_num}/voice.wav'
            return JSONResponse(content={'Text':output_txt, 'Voice': voice_path})

    return JSONResponse(content={'Text':output_txt, 'Voice':'/'})
    

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=1700) 