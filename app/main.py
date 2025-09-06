from fastapi import FastAPI
from routes.route import router

app = FastAPI(title = "SynergySphere – Advanced Team Collaboration Platform")

app.include_router(router)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the SynergySphere API!"}