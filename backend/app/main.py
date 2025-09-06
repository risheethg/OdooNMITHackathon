from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import router as auth_router# Assuming your router is in routes/auth_routes.py
from app.routes.project_routes import router as project_router
from app.routes.chat_routes import router as chat_router
from app.routes.task_routes import router as task_router
from app.routes.websocket_routes import router as websocket_router



app = FastAPI(title = "SynergySphere – Advanced Team Collaboration Platform")
 #--- CORS Middleware Configuration ---
 #Define the list of origins that are allowed to make requests to this API.
 #In production, you should restrict this to your actual frontend domain.
 #Using ["*"] is insecure for production but often acceptable for development.
origins = [
    "http://localhost",
    "http://localhost:3000", # Common for React
    "http://localhost:8080", # Common for Vue
    "http://localhost:4200", # Common for Angular
    "http://localhost:5173", # Common for Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)
# --- Include Routers ---
# It's good practice to add middleware before including routers.
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(chat_router)
app.include_router(task_router)
app.include_router(websocket_router)






# --- Root Endpoint ---
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the SynergySphere API!"}
