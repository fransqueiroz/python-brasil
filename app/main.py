import os
from enum import Enum
import string
from typing import List
from typing import Optional
from unicodedata import decimal, name
from urllib import response
from fastapi import Cookie, FastAPI, Header, status, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, validator

import sqlalchemy as db

database_url = os.getenv('DATABASE_URL')
engine = db.create_engine(database_url)
connection = engine.connect()
metadata = db.MetaData()

app = FastAPI(debug=True)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Department(str, Enum):
    MATH = "math"
    ENGLISH = "english"
    CHEMISTRY = "chemistry"
    COMPUTER_SCIENCE = "computer_science"


class Employee(BaseModel):
    id: int = Field(description="Employee ID")
    department: Department = Field(
        description="The department the employee belongs to.",
    )
    age: int = Field(description="The age of the employee")
    gender: str = Field(min_length=1, description="The gender of the employee")

class ProductDescription(BaseModel):
    name: str = Field(description="The name of the product")

    class Config:
        orm_mode = True

class Product(BaseModel):
    product_id: int = Field(description="Product ID")
    product_description: ProductDescription = Field(description="Description product")
    model: str = Field(description="The model of the product")
    price: float = Field(description="The gender of the employee")

    class Config:
        orm_mode = True


@app.get("/", status_code=status.HTTP_200_OK)
async def home():
    return 'home'

@app.get("/employees/{employee_id}", response_model=Employee, status_code=status.HTTP_200_OK)
async def get_employees(employee_id: int, age: int, department: Department, gender: str = None):

    try:

        employeer = Employee(id= employee_id,department= department,age=age,gender=gender)

        return employeer

    except ValidationError as e:
        return 'teste'

#@app.get("/products", response_model=Product, status_code=status.HTTP_200_OK)
@app.get("/products", status_code=status.HTTP_200_OK)
async def products():

    page = 2
    limit = 10

    product = db.Table('irr_product', metadata, autoload=True, autoload_with=engine)
    product_description = db.Table('irr_product_description', metadata, autoload=True, autoload_with=engine)
    query = db.select([product.columns.product_id,product_description.columns.name,product.columns.model,product.columns.price]).offset((page-1)*limit).limit(limit)
    data = connection.execute(query).fetchall()
    return data

@app.get("/products/{product_id}", status_code=status.HTTP_200_OK)
async def product(product_id):
    product = db.Table('irr_product', metadata, autoload=True, autoload_with=engine)
    product_description = db.Table('irr_product_description', metadata, autoload=True, autoload_with=engine)
    query = db.select([product.columns.product_id,product_description.columns.name,product.columns.model,product.columns.price]).where(product.columns.product_id == product_id)
    data = connection.execute(query).fetchmany(1)
    return data