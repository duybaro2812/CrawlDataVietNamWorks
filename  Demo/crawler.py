import requests
import pandas as pd
from tqdm import tqdm
import time

# Cấu hình API và URL
API_URL = "https://ms.vietnamworks.com/job-search/v1.0/search"
BASE_URL = "https://www.vietnamworks.com"


def fetch_page(page: int, hits_per_page: int = 50, max_retries: int = 3):

#   Gửi request đến API VietnamWorks để lấy dữ liệu job của 1 trang.
#   Có retry nếu lỗi mạng hoặc API tạm ngắt.

    payload = {
        "userId": 0,
        "query": "",
        "filter": [
            {"field": "jobFunction", "value": '[{"parentId":5,"childrenIds":[-1]}]'}  # ngành CNTT
        ],
        "ranges": [],
        "order": [],
        "page": page,
        "hitsPerPage": hits_per_page,
        "retrieveFields": [
            "jobTitle", "companyName", "prettySalary", "skills",
            "alias", "jobId", "approvedOn", "expiredOn"
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.api+json",
        # Thêm dòng này để giả lập trình duyệt, tránh lỗi 403 Forbidden
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(max_retries):
        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"Lỗi khi tải trang {page}: {e}. Thử lại ({attempt + 1}/{max_retries})...")
            time.sleep(2)
    print(f"❌ Bỏ qua trang {page} sau {max_retries} lần thử thất bại.")
    return {"data": []}

# Crawl
def crawl_all():
    print("🚀 Bắt đầu crawl dữ liệu...")
    start = time.time()

    # Lấy trang đầu để biết tổng số trang
    first_page = fetch_page(0)
    meta = first_page.get("meta", {})
    nb_pages = meta.get("nbPages", 1)

    all_jobs = []

    for page in tqdm(range(nb_pages), desc="Đang crawl dữ liệu"):
        data = fetch_page(page)
        # Sleep nhẹ để an toàn
        time.sleep(0.5)

        for job in data.get("data", []):
            jobTitle = job.get("jobTitle", "").strip()
            companyName = job.get("companyName", "").strip()
            prettySalary = job.get("prettySalary", "Thương lượng")
            skills = ", ".join([s.get("skillName", "") for s in job.get("skills", [])]) if job.get("skills") else ""

            alias = job.get("alias", "")
            jobId = job.get("jobId", "")
            jobUrl = f"{BASE_URL}/{alias}-{jobId}-jv" if alias and jobId else ""

            approvedOn = job.get("approvedOn", "")
            expiredOn = job.get("expiredOn", "")

            all_jobs.append({
                "jobTitle": jobTitle,
                "companyName": companyName,
                "salary": prettySalary,
                "skills": skills,
                "jobUrl": jobUrl,
                "approvedOn": approvedOn,
                "expiredOn": expiredOn
            })

    df = pd.DataFrame(all_jobs)
    df.to_csv("vnworks_it_jobs.csv", index=False, encoding="utf-8-sig")
    df.to_excel("vnworks_it_jobs.xlsx", index=False)

    print(f"\n✅ Đã crawl {len(df)} jobs từ {nb_pages} trang vào file vnworks_it_jobs.csv.")
    print(f"⏱ Thời gian thực hiện: {time.time() - start:.2f} giây.")
    print(df.head())
    return df


if __name__ == "__main__":
    crawl_all()