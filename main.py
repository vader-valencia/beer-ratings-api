from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import cv2
import pandas as pd

app = FastAPI()

class NewItem(BaseModel):
    item: str
    encoded_b64_img_str: str

class NewRating(BaseModel):
    itemId: int
    rating: int

items_columns = ["item", "encoded_b64_img_str", "num_ratings", "avg_rating"]
ratings_columns = ["item_id", "rating"]

items_df = pd.DataFrame()
ratings_df = pd.DataFrame()
    

@app.get("/all-ratings")
async def getAllRatings():
    temp = [{"name": "Beer1", "submittedBy":"Joseph"},{"name": "Beer2", "submittedBy":"JoJoseph"}]
    return {"data":temp}

@app.get("/rating/{item_id}")
async def getRatingById(item_id):
    return {"item_id": item_id}

@app.post("/new-item/")
async def createNewItem(item: NewItem):
    return item

@app.post("/rating/")
async def createNewRating(rating: NewRating):
    if rating.itemId not in items_df['item']:
        raise FastAPI.HTTPException(status_code=409, detail=f'Item does not exist')
    
    if type(rating.rating) != int:
         raise FastAPI.HTTPException(status_code=409, detail=f'Non-numeric rating entered for item')

    ratings_df.append(rating)

    # Calculate avg
    item_only_df=ratings_df.query("Courses == {}".format(rating.itemId))
    newAvg = item_only_df['rating'].mean()

    # Set new avg
    items_columns.at[rating.itemId,'avg_rating']=newAvg