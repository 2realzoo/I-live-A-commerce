import uvicorn
import asyncio
from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import FileResponse
from streaming import Streaming
from before_streaming_sum import BeforeSum
from log_analysis import log_graph

app = FastAPI()

@app.post('/streaming')
async def stream(num:int=Form(...), category:int=Form(...)):
    st = Streaming(num, category)
    st.run()
    streaming_file = f'streaming_{num}.mp4'
    like_graph = log_graph(num)
    
    return FileResponse(streaming_file, media_type='video/mp4')
    

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=1700) 