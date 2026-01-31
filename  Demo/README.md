# 🎓 BÁO CÁO ĐỀ ÁN: PHÂN TÍCH THỊ TRƯỜNG TUYỂN DỤNG IT

> **Mô tả:** Đề án nghiên cứu, thu thập và phân tích dữ liệu việc làm ngành Công nghệ thông tin từ nền tảng VietnamWorks. Hệ thống bao gồm Crawler dữ liệu, quy trình làm sạch, Dashboard trực quan hóa và tính năng xuất báo cáo PDF tự động.

---

## 👨‍💻 Thông tin sinh viên

| Thông tin | Chi tiết |
| :--- | :--- |
| **Họ và tên** | **Nguyễn Ngô Duy Bảo** |
| **Mã sinh viên** | 11220800 |
| **Lớp học phần** | Đề án Công nghệ Thông tin |
| **Giảng viên hướng dẫn** | **TS. Phạm Minh Hoàn** |

---
## 📂 Cấu trúc thư mục dự án

Dưới đây là danh sách các tập tin chính trong mã nguồn và chức năng của chúng:

| Tên Tập tin / Thư mục | 📝 Mô tả chức năng |
| :--- | :--- |
| **`crawler.py`** | Script thực hiện thu thập dữ liệu từ API VietnamWorks. |
| **`clean_data.py`** | Script tiền xử lý: làm sạch dữ liệu, chuẩn hóa kỹ năng, phân loại Level. |
| **`dashboard.py`** | Giao diện Web (Streamlit App) hiển thị biểu đồ tương tác và nút tải báo cáo. |
| **`export_report.py`** | Module backend xử lý logic vẽ biểu đồ và đóng gói thành file PDF. |
| **`requirements.txt`** | Danh sách các thư viện Python cần thiết để chạy dự án. |
| **`vnworks_it_jobs...csv`** | Các file dữ liệu (.csv) được sinh ra sau khi chạy chương trình. |
| **`report_it_full.pdf`** | File báo cáo kết quả cuối cùng (được sinh ra tự động). |
| **`temp_images/`** | Thư mục chứa các ảnh biểu đồ tạm thời (tự động tạo khi xuất PDF). |

---
## 🛠️ Yêu cầu cài đặt (Prerequisites)

Trước khi chạy chương trình, vui lòng đảm bảo máy tính đã cài đặt **Python 3.x** và các thư viện cần thiết.

1. **Mở Terminal** (hoặc CMD/PowerShell) tại thư mục chứa mã nguồn.
2. **Cài đặt thư viện** bằng lệnh sau:

```bash
    pip install -r requirements.txt 
```
## 🚀 Hướng dẫn sử dụng (Pipeline)
Hệ thống được thiết kế chạy theo luồng tuần tự. Vui lòng thực hiện theo các bước sau để đảm bảo dữ liệu được xử lý chính xác:

### 1️⃣ Bước 1: Thu thập dữ liệu (Crawling)
Chạy file crawler để lấy dữ liệu việc làm mới nhất từ API của VietnamWorks.

```bash
  python crawler.py
```
✅ Kết quả: Tạo ra file dữ liệu thô vnworks_it_jobs.csv.

### 2️⃣ Bước 2: Làm sạch dữ liệu (Cleaning)
Chạy script làm sạch để xử lý dữ liệu thô, tách danh sách kỹ năng và phân loại cấp bậc (Junior/Senior/Manager...).

```bash
  python clean_data.py
```
✅ Kết quả: Dữ liệu sạch được xuất ra file vnworks_it_jobs_clean.csv.

### 3️⃣ Bước 3: Khởi chạy Dashboard
Mở giao diện Web App để xem các biểu đồ phân tích tương tác.

```bash
  streamlit run dashboard.py
```
✅ Kết quả: Trình duyệt sẽ tự động mở tại địa chỉ http://localhost:8501.

### 4️⃣ Bước 4: Xuất báo cáo PDF (Tùy chọn)
Có thể tải báo cáo trực tiếp trên Dashboard, hoặc chạy lệnh sau để tạo thủ công:

```bash
  python export_report.py
```
✅ Kết quả: Tạo ra file báo cáo hoàn chỉnh report_it_full.pdf.
# Hoàn thành. 🎉🎉🎉