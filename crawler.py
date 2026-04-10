import requests
from bs4 import BeautifulSoup
import time

BASE = "https://mollymax.co.uk"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ========================
# 1. LẤY DANH SÁCH TRUYỆN
# ========================
def get_list(page=1):
    url = f"{BASE}/truyen-moi-nhat/trang-{page}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    items = soup.select(".item-manga")

    data = []
    seen = set()

    for item in items:
        try:
            a = item.select_one("a")
            link = BASE + a["href"]

            # tránh trùng do carousel clone
            if link in seen:
                continue
            seen.add(link)

            title = a.get("title", "").strip()

            data.append({
                "title": title,
                "link": link
            })

        except:
            continue

    return data


# ========================
# 2. LẤY CHAPTER
# ========================
def get_chapters(comic_url):
    res = requests.get(comic_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    chapters = soup.select(".list-chapter a")

    data = []

    for chap in chapters:
        try:
            data.append({
                "name": chap.text.strip(),
                "link": BASE + chap["href"]
            })
        except:
            continue

    return data


# ========================
# 3. LẤY ẢNH TRONG CHAPTER
# ========================
def get_images(chapter_url):
    res = requests.get(chapter_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    imgs = soup.select(".page-chapter img")

    image_list = []

    for img in imgs:
        src = img.get("src") or img.get("data-src")
        if src:
            image_list.append(src)

    return image_list


# ========================
# MAIN
# ========================
if __name__ == "__main__":
    all_data = []

    # 👉 số trang muốn crawl
    TOTAL_PAGES = 2

    for page in range(1, TOTAL_PAGES + 1):
        print(f"\n===== PAGE {page} =====")

        comics = get_list(page)

        for comic in comics:
            print("Đang crawl:", comic["title"])

            chapters = get_chapters(comic["link"])

            comic["chapters"] = []

            # 👉 giới hạn test (tránh bị block)
            for chap in chapters[:2]:
                print("   ->", chap["name"])

                images = get_images(chap["link"])

                comic["chapters"].append({
                    "name": chap["name"],
                    "images": images
                })

                time.sleep(1)  # tránh bị block

            all_data.append(comic)

            time.sleep(1)

    print("\nDONE:", len(all_data))

    # in thử
    for c in all_data[:2]:
        print(c)