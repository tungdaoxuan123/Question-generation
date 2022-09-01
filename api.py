from email import message
import re
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel, validator, ValidationError, conint
from typing import List
import json

from generate_quetion import summarize, QG

#MONGODB START HERE
from pymongo import MongoClient

client = MongoClient('mongodb://mongodb', port=27017)

mydb = client["mydatabase"]

mycol = mydb["text"]   

#MONGODB END HERE

#handel exeption
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    # Change here to LOGGER
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}.Detail: {err}"})
#

@app.get('/')
async def index():
    return {'message': "This is the home page of this API. Go to /apiv1/ or /apiv2/?name="}

from pydantic import BaseModel, Extra
class Details(BaseModel):
    challenge: str = ""
    text: str = ""
    class Config:
        extra = 'ignore'



def trim(text):
    text = text.replace('\n'," ")
    text = text.replace('\t'," ")
    text = " ".join(text.split())
    return text

def boundary(text):
    if not text:
        message = "pls input text"
        return False,message
    #paragraph cannot too short or too long
    if len(text)>= 1500:
        message = "Paragrpah is too long"
        return False, message
    elif len(text) < 300:
        message= "Paragraph is too short"
        return False, message
    return True, "successed"

#check ki tu xam xam:

def checkWeird(text, chal):
    for i in text:
        if i == '’':
            i = "'"
        if ord(i)>126 :
            return True
    for i in chal:
        if i == '’':
            i = "'"
        if ord(i)>126:
            return True
    return False

#check ki tu xam xam end

@app.post("/foo")
async def create_item(request: Request):
    input = await request.body()
    outputs = []
    # for element in input_list:
    items = json.loads(input)
    if("challenge" not in items):
        return "pls input challenge"
    if("text" not in items):
        return "pls input text"
        
    challenge = items['challenge']
    text = items['text']

    if(not isinstance(challenge, str)or not isinstance(text, str)):
        return "wrong input type"

    myDict = {"challenge": challenge, "text":text}
    mycol.insert_one(myDict)
    if(checkWeird(text,challenge)):
        return "nhap gi ki qua"

    if(not challenge):
        return "pls input challenge"
    if(not trim(challenge) == "nlp3"):
        return "nhap lai challenge, nlp3 moi dung"
    result , message = boundary(text)
    if not result:
        return JSONResponse(content = message)

    text = trim(text)
    questions = QG(summarize(text))
    if not questions:
        message = "0 questions were made, check your input paragraph"
        return JSONResponse(content = message)
    return JSONResponse(content = [message, questions])



@app.post('/apiv3/')
async def api3(item: Details):
    myDict = {"challenge": item.challenge, "text":item.text}
    mycol.insert_one(myDict)
    if(not item.challenge):
        return "xin nhap challenge"
    if(not trim(item.challenge) == "nlp3"):
        return "nhap lai challenge, nlp3 moi dung"
    result , message = boundary(item.text)
    if not result:
        return JSONResponse(content = message)

    text = trim(item.text)
    questions = QG(summarize(text))
    if not questions:
        message = "0 questions were made, check your input paragraph"
        return JSONResponse(content = message)
    return JSONResponse(content = [message, questions])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000, debug=True)
