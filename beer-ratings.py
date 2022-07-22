from fastapi import FastAPI
from pydantic import BaseModel
import imghdr

app = FastAPI()

class Item(BaseModel):
    name: str
    submittedBy: str
    photo: imghdr

class Rating(BaseModel):
    itemId: int
    rating: int


@app.get("/all-ratings")
async def getAllRatings():
    return {"message": "Hello World"}

@app.get("/rating-by-id/{item_id}")
async def getRatingById(item_id):
    return {"item_id": item_id}

@app.post("/new-item/")
async def createNewItem(item: Item):
    return item

@app.post("/rating/")
async def createNewRating(rating: Rating):
    return rating