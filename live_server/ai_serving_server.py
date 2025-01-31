import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from live_llm import calling_llm
from live_tts import run_tts
from category_map import category_map
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from live_streaming import load_channels
from pydantic import BaseModel
import pandas as pd
import os

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

class Chat(BaseModel):
    category: str
    channel: int
    text: str
    voice: bool
    who: str

@app.post('/chat')
async def chat(response: Chat):
    category, channel, text, voice, who = response.category, response.channel, response.text, response.voice, response.who
    category = category_map.get(category)
    output_txt = await calling_llm(category, channel, text)
    
    voice = response.get('Voice')
    who = response.get('Who')
    
    if voice:
        voice_complete = run_tts(category, channel, who, output_txt)
        if voice_complete:
            voice_path = f'{category}_{channel}/voice.wav'
            return JSONResponse(content={'text': output_txt, 'voice': voice_path})
    
    return JSONResponse(content={'text': output_txt, 'voice': '/'})

class Sentiment(BaseModel):
    category: str
    channel: str
    
@app.post('/sentiment')
async def sentiment(response: Sentiment):
    category, channel = response.category, response.channel
    category = category_map.get(category)
    
    if not os.path.exists('DB/sentiment_scores.csv'):
        return {"score":None}
    
    df = pd.read_csv('DB/sentiment_scores.csv')
    sentiment_score = df.loc[
        (df['category']==category) & (df['channel']==int(channel))
    ]
    if sentiment_score.empty:
        return {"score":None}
    return sentiment_score.to_dict(orient='records')
    

    

# 정적 파일 제공: /streaming 경로에서 DB 디렉토리를 정적으로 제공
app.mount("/db", StaticFiles(directory="DB"), name="db")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=1702)
