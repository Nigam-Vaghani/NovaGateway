# dummy_backend.py
import sys
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()

# Unique ID based on the port it runs on
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

@app.get("/health")
def health():
    return {"status": "ok"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    return {"message": f"Hello from backend running on port {PORT}", "path": path}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
