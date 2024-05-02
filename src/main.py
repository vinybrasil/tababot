import logging

import requests
from fastapi import FastAPI

from src.handlers import build_chain
from src.schemas import Request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('Initiating LLM')
chain = build_chain()
logging.info('LLM initiated')

app = FastAPI()

@app.get("/api/v1/healthcheck")
def healthcheck():
    return {"service": "tababot"}

def ask_llm(request: Request):
    try:
        res = chain.invoke(request.question)
        logging.info(f'Request {request.request_id}: success')
        request.answer = res
        return request

    except requests.exceptions.ConnectionError as e:
        logging.info(f'Request {request.request_id}: error = {str(e)}')
        request.error = f"cannot call LLM: {str(e)}"
        return request

@app.post("/api/v1/question")
def process_question(request: Request):
    logging.info(f'Request received: {request.request_id}')
    result = ask_llm(request)
    return result
