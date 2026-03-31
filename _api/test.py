from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/api/test")
def read_test():
    return PlainTextResponse("Test Successful: Version 2.5")
