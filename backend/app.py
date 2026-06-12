
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag import ai_model_response

app = FastAPI()

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class Query(BaseModel):
    query: str

# GET route (test purpose)
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

# POST route (main AI query)
@app.post("/query")
def query_model(q: Query):
    result = ai_model_response(q.query)
    return {"answer": result}
