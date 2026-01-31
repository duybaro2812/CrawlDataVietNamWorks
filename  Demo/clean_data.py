import pandas as pd
import os

INPUT_FILE = "vnworks_it_jobs.csv"
OUTPUT_CSV = "vnworks_it_jobs_clean.csv"
OUTPUT_XLSX = "vnworks_it_jobs_clean.xlsx"

def categorize_level(title):
    if pd.isna(title):
        return 'Junior/Mid-level'
    t = str(title).lower()
    if any(x in t for x in ['intern', 'thực tập', 'fresh']): return 'Intern/Fresher'
    if any(x in t for x in ['senior', 'trưởng', 'lead', 'chuyên gia', 'senior']): return 'Senior/Lead'
    if any(x in t for x in ['manager', 'giám đốc', 'head', 'quản lý']): return 'Manager/Director'
    # Mặc định còn lại coi là Junior/Mid
    return 'Junior/Mid-level'

def clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Không tìm thấy file {INPUT_FILE}")
        return

    # Đọc dữ liệu
    df = pd.read_csv(INPUT_FILE)

    # Xóa trùng lặp theo jobUrl
    if "jobUrl" in df.columns:
        df = df.drop_duplicates(subset=["jobUrl"])

    # Chuẩn hóa text
    for col in ["jobTitle", "companyName", "salary", "skills"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # Thêm cột skills_list
    if "skills" in df.columns:
        df["skills_list"] = df["skills"].apply(lambda x: x.split(", ") if x else [])

    # Xử lý ngày tháng
    if "approvedOn" in df.columns:
        df["approvedOn"] = pd.to_datetime(df["approvedOn"], errors="coerce").dt.tz_localize(None)
    if "expiredOn" in df.columns:
        df["expiredOn"] = pd.to_datetime(df["expiredOn"], errors="coerce").dt.tz_localize(None)
    if "approvedOn" in df.columns and "expiredOn" in df.columns:
        df["days_open"] = (df["expiredOn"] - df["approvedOn"]).dt.days

    # Áp dụng hàm phân loại Level trực tiếp
    if "jobTitle" in df.columns:
        print("⚙️ Đang phân loại Level...")
        df["jobLevel_processed"] = df["jobTitle"].apply(categorize_level)
    # -----------------------------

    # Xuất file
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    df.to_excel(OUTPUT_XLSX, index=False)

    print(f"✅ Đã làm sạch dữ liệu. Xuất ra: {OUTPUT_CSV}")
    # In thử vài dòng để kiểm tra
    if "jobLevel_processed" in df.columns:
        print(df[["jobTitle", "jobLevel_processed"]].head())

if __name__ == "__main__":
    clean_data()