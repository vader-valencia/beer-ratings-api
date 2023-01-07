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

origins = ["https://localhost", "https://localhost:8000", "https://localhost:3000", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Category(BaseModel):
    id: Union[int, None] = Field(
        default=None, title="The unique identifier of the category"
    )
    name: str
    submittedBy: str


class Rating(BaseModel):
    rating: float = Field(ge=0.0, le=5.0)


class Item(BaseModel):
    id: Union[int, None] = Field(
        default=None, title="The unique identifier of the item"
    )
    name: str
    description: str
    submittedBy: str
    categoryId: int
    image: Union[str, None] = Field(
        default=None, description="Optional image of the Item"
    )
    rating: Union[float, None] = Field(
        default=0,
        description="[Calculated Field] Average rating of the item, nonzero after first rating",
        ge=0,
        le=5,
    )
    numRatings: Union[int, None] = Field(
        default=0, description="[Calculated Field] Total number of ratings"
    )


class ItemsResponse(BaseModel):
    items: list[Item] = []


class CategoriesResponse(BaseModel):
    items: list[Category] = []


class SuccessMessage(BaseModel):
    successMessage: str


global categories, items, ratings


@app.on_event("startup")
def init_data():
    global categories, items, ratings
    categories = []
    items = []
    ratings = []


@app.get("/categories", response_model=CategoriesResponse)
async def getAllCategories():
    temp = CategoriesResponse(items=categories)
    return temp


@app.get("/categories/{id}", response_model=Category)
async def getCategoryById(id: int):
    for category in categories:
        if category.id == id:
            return category
    raise HTTPException(status_code=404, detail=f"Invalid categoryId")


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
    address = "https://" + get_ip() + ":" + port + "/" + webPath
    # Creating an instance of QRCode class
    qr = qrcode.QRCode(version=1, box_size=10, border=5)

    # Adding data to the instance 'qr'
    qr.add_data(address)

    qr.make(fit=True)
    img = qr.make_image(fill_color=fillColor, back_color=backgroundColor)

    return Response(content=image_to_byte_array(img), media_type="image/png")


@app.get("/{categoryName}/items", response_model=ItemsResponse)
async def getItemsByCategoryName(categoryName: str):
    if categoryName.lower() not in [c.name.lower() for c in categories]:
        raise HTTPException(status_code=422, detail=f"Invalid category")

    filteredItems = []
    for item in items:
        if item.name == categoryName.lower():
            filteredItems.append(item)
    return ItemsResponse(items=filteredItems)


"""
@app.get("/{categoryId}/items", response_model=ItemsResponse)
async def getItemsByCategoryId(categoryId: int):
    filteredItems = []
    for item in items:
        if item.categoryId == categoryId:
            filteredItems.append(item)
    return ItemsResponse(items=filteredItems)
"""


@app.get("/items", response_model=ItemsResponse)
async def getAllItems():
    return ItemsResponse(items=items)


@app.get("/items/{itemId}", response_model=Item)
async def getItemById(itemId: int):
    for item in items:
        if item.id == itemId:
            return item
    raise HTTPException(status_code=404, detail=f"Invalid itemId")


@app.post("/items", response_model=SuccessMessage)
async def createNewItem(item: Item):
    if item.name.lower() in [i.name.lower() for i in items]:
        raise HTTPException(status_code=409, detail=f"Item already exists")

    if item.categoryId not in [c.id for c in categories]:
        raise HTTPException(status_code=422, detail=f"Invalid categoryId")

    item.id = len(items)
    items.append(item)

    return {"successMessage": "New item created successfully"}


@app.post("/categories", response_model=SuccessMessage)
async def createNewCategory(category: Category):
    if category.name.lower() in [c.name.lower() for c in categories]:
        raise HTTPException(status_code=409, detail=f"Category already exists")

    category.id = len(categories)
    categories.append(category)

    return {"successMessage": "New category created successfully"}


@app.post("/ratings/{itemId}", response_model=SuccessMessage)
async def createNewRating(itemId: int, rating: Rating):
    for item in items:
        if item.id == itemId:
            newAverage = (item.numRatings * item.rating + rating.rating) / (
                item.numRatings + 1
            )
            item.rating = newAverage
            item.numRatings += 1

            # Add rating to stored df
            ratings.append(rating)

            return {"successMessage": "Rating entered successfully!"}

    raise HTTPException(status_code=404, detail=f"Invalid itemId")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile="C:/Users/j22va/Desktop/Certificates/cert.pem ",
        ssl_keyfile="C:/Users/j22va/Desktop/Certificates/key.pem",
    )
