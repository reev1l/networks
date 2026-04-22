import time
import psycopg2
from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()
DB_DSN = "postgresql://postgres:gsx13_528ll@mydb:5432/parse"


def init_db():
    for _ in range(10):
        try:
            with psycopg2.connect(DB_DSN) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS books (
                            id SERIAL PRIMARY KEY,
                            title TEXT,
                            price TEXT,
                            availability TEXT
                        )
                    """)
                    conn.commit()
            return
        except Exception:
            time.sleep(3)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/parse")
def parse_books():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://books.toscrape.com/")
        page.wait_for_selector("article.product_pod")

        books = page.locator("article.product_pod").all()

        with psycopg2.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                for book in books:
                    try:
                        title = book.locator("h3 a").get_attribute("title")
                        price = book.locator("p.price_color").inner_text().strip()
                        availability = book.locator("p.instock.availability").inner_text().strip()

                        cur.execute(
                            "INSERT INTO books (title, price, availability) VALUES (%s, %s, %s)",
                            (title, price, availability)
                        )
                    except Exception:
                        pass
                conn.commit()

        browser.close()

    return {"status": "ok"}


@app.get("/data")
def get_data():
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, price, availability FROM books")
            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "price": row[2],
                    "availability": row[3]
                }
                for row in rows
            ]