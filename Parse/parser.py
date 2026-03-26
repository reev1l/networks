import csv
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://github.com/login")
    page.fill("#login_field", "reevl1") 
    page.fill("#password", "gsx12_528ll")
    page.click("input[name='commit']")
    page.wait_for_selector("img.avatar")
    print("Auth successful")

    page.goto("https://github.com/trending")
    page.wait_for_selector("article.Box-row")

    data = []
    print("Parcing trending repositories")

    repos = page.locator("article.Box-row").all()

    for repo in repos:
        title_element = repo.locator("h2 a")
        title = title_element.inner_text().replace('\n', '').replace(' ', '')
        
        desc_element = repo.locator("p.col-9")
        description = desc_element.inner_text().strip()
        
        lang_element = repo.locator("span[itemprop='programmingLanguage']")
        language = lang_element.inner_text()
        
        stars_element = repo.locator("a[href$='/stargazers']").first
        stars = stars_element.inner_text().strip()

        data.append([title, description, language, stars])


    filename = "data.csv"
    with open(filename, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Repository", "Description", "Language", "Stars"])
        writer.writerows(data)

    print(f"Parcing completed.")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)