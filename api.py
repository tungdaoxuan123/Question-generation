from email import message
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

from generate_quetion import summarize, QG



app = FastAPI()

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
        message = "please input something"
        return False,message
    #paragraph cannot too short or too long
    if len(text)>= 1500:
        message = "Paragrpah is too long"
        return False, message
    elif len(text) < 300:
        message= "Paragraph is too short"
        return False, message
    return True, "successed"

@app.post('/apiv3/')
async def api3(item: Details):
    if(not item.challenge):
        return "xin nhap challenge"
    if(not item.challenge == "nlp3"):
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
