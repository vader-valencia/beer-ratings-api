from cv2 import cornerEigenValsAndVecs
from fastapi import FastAPI, File, UploadFile
from matplotlib.pyplot import ginput
from pydantic import BaseModel
from enum import Enum
import pandas as pd

app = FastAPI()

class AlcoholType(Enum):
    Beer = 1
    Wine = 2
    Whiskey = 3
    Bourbon = 4
    Tequila = 5
    Seltzer = 6
    Amaro = 7
    Apertif = 8
    Vermouth = 9
    Brandy = 10
    Cognac = 11
    Gin = 12
    Liqeur = 13
    Cordial = 14
    Schnapps = 15
    ReadyMade = 16
    Rum = 17
    Scotch = 18
    Vodka = 19

class NewItem(BaseModel):
    name: str
    description: str
    alcoholType: AlcoholType
    b64ImgStr: str

class NewRating(BaseModel):
    rating: int

class ItemResponse(BaseModel):
    itemId: int
    name: str
    description: str
    alcoholType: AlcoholType
    b64ImgStr: str
    rating: float
    numRatings: int

class ItemsResponse(BaseModel):
    items: list[ItemResponse] = []

class SuccessMessage(BaseModel):
    successMessage: str

items_columns = ['name', 'description', 'alcohol_type', 'b64_img_str', 'avg_rating', 'num_ratings']
ratings_columns = ['item_id', 'rating']

items_df = pd.DataFrame()
ratings_df = pd.DataFrame()
    
def checkitemExists(itemId):
    if itemId not in items_df.index:
        raise FastAPI.HTTPException(status_code=409, detail=f'Item does not exist')

def checkRatingValidInputType(rating):
    if type(rating) != int:
        raise FastAPI.HTTPException(status_code=409, detail=f'Non-numeric rating entered for item')

@app.get('/all-items', response_model=ItemsResponse)
async def getAllItems():
    return items_df

@app.get('/item/{item_id}', response_model=ItemResponse)
async def getItemById(itemId):
    checkitemExists(itemId)

    return items_df.loc[itemId]

@app.post('/new-item/', response_model=SuccessMessage)
async def createNewItem(item: NewItem):
    if item.name.lower() in items_df['name'].lower():
        raise FastAPI.HTTPException(status_code=409, detail=f'Item already exists')

    items_df.append(item)

    return {'New item created successfully'}


@app.post('/rating/{item_id}', response_model=SuccessMessage)
async def createNewRating(itemId, rating: NewRating):
    # Check for invalid data entries
    checkitemExists(itemId)
    checkRatingValidInputType(rating.rating)

    # Add rating to stored df
    ratings_df.append(rating)

    # Calculate avg
    item_only_df=ratings_df.query('Courses == {}'.format(itemId))
    newAvg = item_only_df['rating'].mean()

    # Set new avg
    items_df.at[itemId,'avg_rating']=newAvg

    return {'Rating entered successfully!'}