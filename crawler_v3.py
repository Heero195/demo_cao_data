import requests
from bs4 import BeautifulSoup
import csv
import time
import re

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://mollymax.co.uk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_comic_list(page):
    url = f"{BASE_URL}/truyen-moi-nhat/trang-{page}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        links = []
        seen = set()
        
        # Lấy tất cả link truyên tranh trên trang
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Pattern check: /truyen-tranh/ten-truyen (không có /chuong-...)
            if "/truyen-tranh/" in href and href.count("/") == 2:
                full_url = href if href.startswith("http") else BASE_URL + href
                if full_url not in seen:
                    seen.add(full_url)
                    links.append(full_url)
        return links
    except Exception as e:
        print(f"Error getting page {page}: {e}")
        return []

def get_comic_details(url):
    print(f"  Crawling detail: {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        data = {
            "ten_truyen_tieng_viet": "",
            "nguon_tieng_viet": url,
            "chap_da_dich": "0",
            "last_updated_tieng_viet": "",
            "so_luong_doc": "0",
            "ten_truyen_original": "N/A",
            "nguon_original": "N/A",
            "chap_original": "N/A",
            "last_update_original": "N/A",
            "tag": "update"
        }
        
        # 1. Tên truyện
        title_tag = soup.find("h1")
        if title_tag:
            data["ten_truyen_tieng_viet"] = title_tag.get_text(strip=True)
            
        # 2. Thông tin info (lượt xem, tình trạng)
        info_rows = soup.select(".detail-info .row")
        status_text = "Đang cập nhật"
        for row in info_rows:
            text = row.get_text()
            if "Lượt xem" in text:
                cols = row.find_all("div")
                if len(cols) >= 2:
                    data["so_luong_doc"] = cols[1].get_text(strip=True)
            elif "Tình trạng" in text:
                cols = row.find_all("div")
                if len(cols) >= 2:
                    status_text = cols[1].get_text(strip=True)
        
        # Tag logic dựa trên tình trạng
        if "Hoàn thành" in status_text:
            data["tag"] = "end"
        
        # 3. Danh sách chương (Lấy chương mới nhất)
        chap_list_div = soup.select_one(".chapts")
        if chap_list_div:
            # Dòng đầu tiên thường là chương mới nhất
            first_chap_row = chap_list_div.select_one(".d-flex.border-bottom")
            if first_chap_row:
                spans = first_chap_row.find_all("span")
                if len(spans) >= 2:
                    data["chap_da_dich"] = spans[0].get_text(strip=True)
                    data["last_updated_tieng_viet"] = spans[1].get_text(strip=True)
        
        return data
    except Exception as e:
        print(f"    Error detail {url}: {e}")
        return None

def main():
    output_file = "truyen_data.csv"
    fields = [
        "ten_truyen_tieng_viet", "nguon_tieng_viet", "chap_da_dich", 
        "last_updated_tieng_viet", "so_luong_doc", "ten_truyen_original", 
        "nguon_original", "chap_original", "last_update_original", "tag"
    ]
    
    print("===== STARTING CRAWLER V3 =====")
    
    # Khởi tạo file với tiêu đề
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
    
    count = 0
    for page in range(1, 6): # Quét 5 trang
        print(f"Processing Page {page}...")
        links = get_comic_list(page)
        print(f"  Found {len(links)} comics.")
        
        for link in links:
            details = get_comic_details(link)
            if details:
                # Ghi ngay vào file
                with open(output_file, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writerow(details)
                count += 1
            time.sleep(1) # Nghỉ 1s tránh bị block
            
    print(f"===== DONE! Saved {count} comics to {output_file} =====")

if __name__ == "__main__":
    main()
