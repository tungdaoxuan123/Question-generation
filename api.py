from email import message
import uvicorn
from fastapi import FastAPI
from generate_quetion import summarize, QG
app = FastAPI()

@app.get('/')
async def index():
    return {'message': "This is the home page of this API. Go to /apiv1/ or /apiv2/?name="}

from pydantic import BaseModel
class Details(BaseModel):
    challenge: str = "nlp3"
    text: str

def boundary(text):
    #paragraph cannot too short or too long
    if len(text)>= 1500:
        message = "Paragrpah is too long"
        return False, message
    elif len(text) < 500:
        message= "Paragraph is too short"
        return False, message
    return True, "successed"

@app.post('/apiv3/')
async def api3(item: Details):
    result , message = boundary(item.text)
    if not result:
        return message
    questions = QG(item.text)
    if not questions:
        message = "0 questions were made, check your input paragraph"
        return message
    return message, questions

if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=5000, debug=True)