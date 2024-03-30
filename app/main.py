import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

sys.path.append(parent_dir)

from fastapi import FastAPI, Request, middleware
from fastapi.middleware.cors import CORSMiddleware
from app.routers import blog
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
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
class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Print request details before entering the function
        print("----- Request Details:")
        print(f"Request {request.items}")
        print(f"Method: {request.method}")
        print(f"Path: {request.url.path}")
        print(f"Headers: {request.headers}")
        body = await request.body()
        print(body)
        # print(f"Body: {body.decode('utf-8')}")  # Read request body (if applicable)

        response = await call_next(request)

        return response


app.add_middleware(RequestLoggerMiddleware)


app.include_router(
    blog.router
)



# Define a simple route for testing
@app.get("/")
def get_app():
    return "hey this is blog page"


# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
