from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    print("Incoming request:", body)
    return {"message": "received", "data": body}