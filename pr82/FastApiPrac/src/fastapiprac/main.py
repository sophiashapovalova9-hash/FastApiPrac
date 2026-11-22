import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="FastAPIPractice",
    description="First FastAPI application",
    docs_url="/docs",
    redoc_url="/redoc"
)

DATA_PATH = "src/fastapiprac/data.json"


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    genre: str
    price: float
    in_stock: bool


@app.get("/books", response_model=list[Book])
async def get_books():
    data = load_data()
    return data["books"]


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    data = load_data()
    for book in data["books"]:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", response_model=Book, status_code=201)
async def add_book(book: Book):
    data = load_data()
    for b in data["books"]:
        if b["id"] == book.id:
            raise HTTPException(status_code=400, detail="Book with this ID already exists")
    data["books"].append(book.model_dump())
    save_data(data)
    return book


@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    data = load_data()
    for i, book in enumerate(data["books"]):
        if book["id"] == book_id:
            deleted = data["books"].pop(i)
            save_data(data)
            return {"message": "Book deleted", "book": deleted}
    raise HTTPException(status_code=404, detail="Book not found")


@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, new_book: Book):
    data = load_data()
    for i, book in enumerate(data["books"]):
        if book["id"] == book_id:
            updated = new_book.model_dump()
            updated["id"] = book_id
            data["books"][i] = updated
            save_data(data)
            return updated
    raise HTTPException(status_code=404, detail="Book not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)