from cv2 import cornerEigenValsAndVecs
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from matplotlib.pyplot import ginput
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import qrcode
import socket
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Union


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class Item(BaseModel):
    name: str
    description: str
    alcoholType: AlcoholType
    b64ImgStr: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )


class Category(BaseModel):
    name: str
    submittedBy: str

    def as_dict(self):
        return {"name": self.name, "submittedBy": self.submittedBy}


class Rating(BaseModel):
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


class CategoryResponse(BaseModel):
    name: str
    submittedBy: str


class CategoriesResponse(BaseModel):
    items: list[CategoryResponse] = []


class SuccessMessage(BaseModel):
    successMessage: str


categories_columns = ["name", "submittedBy"]
items_columns = [
    "name",
    "description",
    "alcohol_type",
    "b64_img_str",
    "avg_rating",
    "num_ratings",
]
ratings_columns = ["item_id", "rating"]

# categories_df = pd.DataFrame(columns=categories_columns)
# items_df = pd.DataFrame(columns=items_columns)
# ratings_df = pd.DataFrame(columns=ratings_columns)

global categories
global items
global ratings


@app.on_event("startup")
def init_data():
    global categories
    global items
    global ratings
    categories = []
    items = []
    ratings = []


@app.get("/all-categories", response_model=CategoriesResponse)
async def getAllCategories():
    temp = CategoriesResponse(items=categories)
    return temp


"""

def checkitemExists(itemId):
    if itemId not in items_df.index:
        raise FastAPI.HTTPException(status_code=409, detail=f"Item does not exist")


def checkRatingValidInputType(rating):
    if type(rating) != int:
        raise FastAPI.HTTPException(
            status_code=409, detail=f"Non-numeric rating entered for item"
        )
"""


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def image_to_byte_array(image: Image) -> bytes:
    # BytesIO is a fake file stored in memory
    imgByteArr = io.BytesIO()
    # image.save expects a file as a argument, passing a bytes io ins
    image.save(imgByteArr, format=image.format)
    # Turn the BytesIO object back into a bytes object
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


@app.get(
    "/{port}/qr-code",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def getQrCode(port, webPath="", fillColor="black", backgroundColor="white"):
    address = "http://" + get_ip() + ":" + port + "/" + webPath
    # Creating an instance of QRCode class
    qr = qrcode.QRCode(version=1, box_size=10, border=5)

    # Adding data to the instance 'qr'
    qr.add_data(address)

    qr.make(fit=True)
    img = qr.make_image(fill_color=fillColor, back_color=backgroundColor)

    return Response(content=image_to_byte_array(img), media_type="image/png")


@app.get("/all-items", response_model=ItemsResponse)
async def getAllItems():
    return ItemsResponse(items=items)


"""
@app.get("/item/{item_id}", response_model=ItemResponse)
async def getItemById(itemId):
    checkitemExists(itemId)
    return items_df.loc[itemId]
"""


@app.post("/item", response_model=SuccessMessage)
async def createNewItem(item: Item):
    if item.name.lower() in [i.name.lower() for i in items]:
        raise HTTPException(status_code=409, detail=f"Item already exists")

    items.append(item)

    return {"New item created successfully"}


@app.post("/category", response_model=SuccessMessage)
async def createNewCategory(category: Category):
    if category.name.lower() in [c.name.lower() for c in categories]:
        raise HTTPException(status_code=409, detail=f"Category already exists")

    categories.append(category)

    return {"successMessage": "New category created successfully"}


""" @app.post("/rating/{item_id}", response_model=SuccessMessage)
async def createNewRating(itemId, rating: Rating):
    # Check for invalid data entries
    checkitemExists(itemId)
    checkRatingValidInputType(rating.rating)

    # Add rating to stored df
    ratings_df.append(rating)

    # Calculate avg
    item_only_df = ratings_df.query("Courses == {}".format(itemId))
    newAvg = item_only_df["rating"].mean()

    # Set new avg
    items_df.at[itemId, "avg_rating"] = newAvg

    return {"Rating entered successfully!"} """


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
