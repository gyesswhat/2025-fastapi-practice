from typing import Union, List

from pydantic import BaseModel
from fastapi import FastAPI, Query, Path
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}


# 순서에 유의할 것
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

# 사전정의 값: 그 외의 값 입력하면 에러 남 왜냐하면 ModelName으로 타입 정의되었으니까
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

# 경로 변환기
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

####################
# 쿼리 매개변수
####################

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]

# http://localhost:8000/items/?skip=2&limit=3 등으로 테스트 가능

# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
#     item = {"item_id": item_id}
#     if q:
#         item.update({"q": q})
#     if not short:
#         item.update(
#             {"description": "This is an amazing item that has a long description"}
#         )
#     return item

# http://localhost:8000/items/3?q=gyeore
# http://localhost:8000/items/3?q=gyeore&short=1
# http://localhost:8000/items/3?q=gyeore&short=True
# http://localhost:8000/items/3?q=gyeore&short=on
# 그 외 yes 등....

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "Long Long Description............."}
        )
    return item

# http://localhost:8000/users/1/items/computer
# http://localhost:8000/users/1/items/computer?q=gyeore&short=True

# @app.get("/items/{item_id}")
# async def read_user_item(
#         item_id: str, needy: str, skip: int = 0, limit: Union[int, None] = None
# ):
#     item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
#     return

# http://localhost:8000/items/foo?needy=hello&skip=3&limit=10
# needy: 필수적인 str
# skip: 기본값이 0인 int
# limit: 선택적인 int

@app.post("/items/")
async def create_item(item: Item): # Pydantic 모델로 선언된 그 함수 매개변수는 요청 본문에서 가져옴
    item_dict = item.dict()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

##########
# 쿼리 매개변수와 문자열 검증
##########

# @app.get("/items/")
# async def read_items(q: Union[str, None] = None):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results;

# regex도 공부해보기...
# @app.get("/items")
# async def read_items(q: Union[str, None] = Query(default=None, min_length=3, max_length=50, pattern="^fixedquery$")):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results;
# http://localhost:8000/items?q=012345678901234567890123456789012345678901234567891


# @app.get("/items/")
# async def read_items(q: str = Query(default="fixedquery", min_length=3)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

# @app.get("/items/")
# async def read_items(q: Union[List[str], None] = Query(default=None)):
#     query_items = {"q": q}
#     return query_items

# @app.get("/items/")
# async def read_items(q: List[str] = Query(default=["foo", "bar"])):
#     query_items = {"q": q}
#     return query_items

# @app.get("/items/")
# async def read_items(q: list = Query(default=[])):
#     query_items = {"q": q}
#     return query_items
# 이 경우 FastAPI는 리스트의 내용을 검사하지 않음을 명심하기 바랍니다.
# 예를 들어, List[int]는 리스트 내용이 정수인지 검사(및 문서화)합니다. 하지만 list 단독일 경우는 아닙니다.


# @app.get("/items/")
# async def read_items(
#         q: Union[str, None] = Query(default=None, title="Query string", description="Query string for the items to search in the database that have a good match", min_length=3)
# ):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results
# title, description은 문서화를 위해 존재하는 메타데이터

# @app.get("/items/")
# async def read_items(q: Union[str, None] = Query(default=None, alias="item-query")):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results
# 유효한 파이썬 변수명이 아님에도 사용하고 싶을 때
# http://127.0.0.1:8000/items/?item-query=foobaritems

@app.get("/items/")
async def read_items(
        q: Union[str, None] = Query(
            default=None,
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        )
):
    results = {"items" : [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# http://localhost:8000/items/?q=abcfixedqueryabc
# docs에서 deprecated로 보임

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item, q: str | None = None):
#     result = {"item_id": item_id, **item.dict()}
#     if q:
#         result.update({"q": q})
#     return result

######################
# 경로 매개변수와 숫자 검증
######################

@app.get("/items/{item_id}")
async def read_items(
        q: str,
        item_id: int = Path(description="The ID of the item to get"),
        # q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
# http://localhost:8000/items/1?item-query=strstr
# http://localhost:8000/items/3?q=asdf

@app.get("/items/{item_id}/")
async def read_items(
        *,
        item_id: int = Path(description="The ID of the item to get", ge=0, le=1000),
        q: str,
        size: float = Query(gt=0, lt=10.5)
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results
# ge: 크거나 같음
# gt: 크거나
# le: 작거나 같음
# lt: 작거나
# 숫자 검증은 float 값에도 작동
# http://localhost:8000/items/0/?q=asdf&size=10.4