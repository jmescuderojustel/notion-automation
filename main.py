import requests
import sys
import asyncio
from pyppeteer import launch

token = sys.argv[1]
links_page_id = sys.argv[2]
headers = {"Authorization": "Bearer " + token, "Notion-Version": "2022-06-28"}


def get_page_url(page_id):
    api_url = "https://api.notion.com/v1/pages/" + page_id
    response = requests.get(api_url, headers=headers)
    response_json = response.json()
    page_properties = response_json["properties"]

    if "URL" in page_properties:
        return page_properties["URL"]["url"]

    return ""


def get_page_content(page_id):
    api_url = "https://api.notion.com/v1/blocks/" + page_id + "/children?page_size=100"
    response = requests.get(api_url, headers=headers)
    response_json = response.json()
    page_blocks = response_json["results"]

    pages_html = ""

    for block in page_blocks:
        placeholder = ""
        property_name = block["type"]

        match block["type"]:
            case "heading_1":
                placeholder = "<h1>__content__</h1>"
            case "heading_2":
                placeholder = "<h2>__content__</h2>"
            case "heading_3":
                placeholder = "<h3>__content__</h3>"
            case "heading_4":
                placeholder = "<h4>__content__</h4>"
            case "heading_5":
                placeholder = "<h5>__content__</h5>"
            case "paragraph":
                placeholder = "<p>__content__</p>"
            case "code":
                placeholder = "<code>__content__</code>"
            case "quote":
                placeholder = "<p><i>__content__</i><p/>"

        if (
            "rich_text" in block[property_name]
            and len(block[property_name]["rich_text"]) > 0
            and "plain_text" in block[property_name]["rich_text"][0]
        ):
            content = block[property_name]["rich_text"][0]["plain_text"]
            pages_html += placeholder.replace("__content__", content)

    return pages_html


def get_database_page_ids(database_id):
    api_url = "https://api.notion.com/v1/databases/" + database_id + "/query"
    response = requests.post(api_url, headers=headers, data={})
    response_json = response.json()
    pages = response_json["results"]
    pages_id_mapping = map(lambda x: x["id"], pages)
    pages_ids = list(pages_id_mapping)
    return pages_ids


async def main():
    link_page_ids = get_database_page_ids(links_page_id)
    pages_html = []

    for page_id in link_page_ids:
        url = get_page_url(page_id)
        content = get_page_content(page_id)
        pages_html.append(content)

    all_html = "<html><head></head><body style='font-family: Verdana,Sans Serif'>"

    for page in pages_html:
        all_html += page + "<p style='page-break-after: always;'>&nbsp;</p><p style='page-break-before: always;'>&nbsp;</p>"

    all_html += "</body>"
    
    text_file = open("all.html", "w")
    text_file.write(all_html)
    text_file.close()

    browser = await launch()
    page = await browser.newPage()
    await page.goto(
        "file://C:/Dev/Repositories/jmescuderojustel/notion-automation/all.html"
    )
    await page.emulateMedia("screen")
    await page.pdf({"path": "all.pdf", "format": "A4"})
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
