import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

sys.path.append(parent_dir)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import blog
import uvicorn
# Create the FastAPI app
app = FastAPI(debug=True)
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(
    blog.router
)

# Define a simple route for testing
@app.get("/")
def get_app():
    return "hey this is blog page"


# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
