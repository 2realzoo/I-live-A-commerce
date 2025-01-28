import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from live_llm import calling_llm
from live_tts import run_tts
from category_map import category_map
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from live_streaming import load_channels

app = FastAPI()

# CORS 설정: React 앱에서 FastAPI 서버에 접근 가능하도록 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React 앱의 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/home')
async def home():
    channels = load_channels()
    return JSONResponse(content=channels)

@app.post('/chat')
async def chat(request: dict = Body(...)):
    category_str = request.get('Category')
    category = category_map.get(category_str, 0)
    channel_num = request.get('Channel')
    
    input_txt = request.get('Text')
    output_txt = await calling_llm(category, channel_num, input_txt)
    
    voice = request.get('Voice')
    who = request.get('Who')
    
    if voice:
        voice_complete = run_tts(category, channel_num, who, output_txt)
        if voice_complete:
            voice_path = f'{category}_{channel_num}/voice.wav'
            return JSONResponse(content={'Text': output_txt, 'Voice': voice_path})
    
    return JSONResponse(content={'Text': output_txt, 'Voice': '/'})

# 정적 파일 제공: /streaming 경로에서 DB 디렉토리를 정적으로 제공
app.mount("/db", StaticFiles(directory="DB"), name="db")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=1702)
