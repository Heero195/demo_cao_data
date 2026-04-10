import requests
from bs4 import BeautifulSoup
import time
import json

BASE_URL = "https://mollymax.co.uk"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ========================
# 1. LẤY DANH SÁCH TRUYỆN
# ========================
def get_list(page=1):
    url = f"{BASE_URL}/truyen-moi-nhat/trang-{page}"
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code} | URL: {url}")
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    seen = set()

    # Lấy tất cả link /truyen-tranh/...
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Phải chứa /truyen-tranh/ và KHÔNG chứa /chuong- (vì đó là link chapter)
        if "/truyen-tranh/" in href and "/chuong-" not in href:
            # Tạo link tuyệt đối
            if href.startswith("/"):
                full_link = BASE_URL + href
            elif href.startswith("http"):
                full_link = href
            else:
                continue
            
            # Bỏ qua link trang chủ danh mục (nếu có)
            if full_link.endswith("/truyen-tranh") or full_link.endswith("/truyen-tranh/"):
                continue

            if full_link in seen:
                continue

            title = a.get_text(strip=True)
            # Bỏ qua nếu title là số (view count), rỗng, hoặc quá ngắn
            if title and not title.replace(".", "").isdigit() and len(title) > 2:
                seen.add(full_link)
                data.append({
                    "title": title,
                    "link": full_link
                })

    print(f"Found {len(data)} truyen on page {page}")
    return data


# ========================
# 2. LẤY CHAPTER
# ========================
def get_chapters(comic_url):
    res = requests.get(comic_url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    seen = set()

    skip_names = {"Đọc từ đầu", "Đọc mới nhất", "Doc tu dau", "Doc moi nhat"}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/truyen-tranh/" in href and "/chuong-" in href:
            full_link = BASE_URL + href if href.startswith("/") else href
            if full_link in seen:
                continue
            seen.add(full_link)

            name = a.get_text(strip=True)
            if name and name not in skip_names:
                data.append({
                    "name": name,
                    "link": full_link
                })

    return data


# ========================
# 3. LẤY ẢNH TRONG CHAPTER
# ========================
def get_images(chapter_url):
    res = requests.get(chapter_url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    image_list = []

    selectors = [
        ".page-chapter img",
        ".reading-detail img",
        ".chapter-content img",
        "#chapter-content img",
        ".box-doc img",
        "img[data-src]",
    ]

    for sel in selectors:
        imgs = soup.select(sel)
        if imgs:
            for img in imgs:
                src = img.get("data-src") or img.get("src")
                if src and src not in image_list:
                    image_list.append(src)
            if image_list:
                break

    return image_list


# ========================
# MAIN
# ========================
if __name__ == "__main__":
    all_data = []
    TOTAL_PAGES = 1

    for page in range(1, TOTAL_PAGES + 1):
        print(f"\n===== PAGE {page} =====")
        comics = get_list(page)

        for comic in comics[:3]:  # test 3 truyen
            print(f"\nDang crawl: {comic['title']}")
            chapters = get_chapters(comic["link"])
            print(f"  Chapters: {len(chapters)}")

            comic["chapters"] = []

            for chap in chapters[:2]:  # lay 2 chapter dau
                print(f"   -> {chap['name']}")
                images = get_images(chap["link"])
                print(f"      Anh: {len(images)}")
                comic["chapters"].append({
                    "name": chap["name"],
                    "images": images
                })
                time.sleep(1)

            all_data.append(comic)
            time.sleep(1)

    print(f"\n==== DONE: {len(all_data)} truyen ====")

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Da luu vao output.json")

    for c in all_data[:2]:
        print(f"\n[{c['title']}]")
        for chap in c.get("chapters", []):
            print(f"  {chap['name']}: {len(chap['images'])} anh")
