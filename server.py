import uvicorn
import asyncio
from fastapi import FastAPI, Form, BackgroundTasks
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import FileResponse
from streaming import Streaming, main, channels

@asynccontextmanager
async def stream(app:FastAPI):
    scheduler = BackgroundScheduler()
    asyncio.create_task(main())
    scheduler.add_job(lambda: None, 'interval', seconds = 5)
    scheduler.start()
    
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)
    

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=1700) 