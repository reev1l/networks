import psycopg2
from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()
DB_DSN = "postgresql://postgres:gsx13_528ll@127.0.0.1:5432/parse"

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id SERIAL PRIMARY KEY,
                title TEXT,
                description TEXT,
                language TEXT,
                stars TEXT
            )
        """)
        conn.commit()

@app.get("/parse")
def run(url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://github.com/login")
        page.fill("#login_field", "reevl1") 
        page.fill("#password", "gsx12_528ll")
        page.click("input[name='commit']")
        page.wait_for_selector("img.avatar")

        page.goto(url)
        page.wait_for_selector("article.Box-row")

        repos = page.locator("article.Box-row").all()

        with psycopg2.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                for repo in repos:
                    try:
                        title_element = repo.locator("h2 a")
                        title = title_element.inner_text().replace('\n', '').replace(' ', '')
                        
                        desc_element = repo.locator("p.col-9")
                        description = desc_element.inner_text().strip()
                        
                        lang_element = repo.locator("span[itemprop='programmingLanguage']")
                        language = lang_element.inner_text()
                        
                        stars_element = repo.locator("a[href$='/stargazers']").first
                        stars = stars_element.inner_text().strip()

                        cur.execute(
                            "INSERT INTO repositories (title, description, language, stars) VALUES (%s, %s, %s, %s)",
                            (title, description, language, stars)
                        )
                    except Exception:
                        pass
                conn.commit()

        browser.close()

@app.get("/data")
def get_data():
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, description, language, stars FROM repositories")
            rows = cur.fetchall()
            
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "language": row[3],
                    "stars": row[4]
                }
                for row in rows
            ]