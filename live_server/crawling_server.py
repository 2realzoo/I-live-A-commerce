import uvicorn
import asyncio
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from live_streaming import main

@asynccontextmanager
async def stream(app:FastAPI):
    asyncio.create_task(main())
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=1701)
