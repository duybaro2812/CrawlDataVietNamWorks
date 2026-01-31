import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import ast
import platform
from export_report import create_pdf
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="VietnamWorks IT Job Dashboard", layout="wide")

# --- CẤU HÌNH FONT TIẾNG VIỆT ---
system_name = platform.system()
if system_name == "Windows":
    plt.rcParams['font.family'] = 'Segoe UI'
elif system_name == "Darwin":
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Sans-serif'


# --- LOAD DỮ LIỆU ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("vnworks_it_jobs_clean.csv")
        # Chuyển đổi ngày tháng
        df["approvedOn"] = pd.to_datetime(df["approvedOn"], errors='coerce')

        # Parse skills_list từ chuỗi thành list thật
        if "skills_list" in df.columns:
            df["skills_list"] = df["skills_list"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        return df
    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Không tìm thấy file dữ liệu. Hãy chạy clean_data.py trước!")
    st.stop()

# --- SIDEBAR (THANH BÊN TRÁI) ---
st.sidebar.header("🔍 Bộ lọc")

# 1. Bộ lọc Công ty
all_companies = sorted(df["companyName"].unique().tolist())
selected_companies = st.sidebar.multiselect("Chọn công ty", all_companies)

# 2. Bộ lọc Thời gian
min_date = df["approvedOn"].min().date()
max_date = df["approvedOn"].max().date()

if pd.isnull(min_date) or pd.isnull(max_date):
    st.sidebar.warning("Dữ liệu ngày tháng bị lỗi.")
    start_date, end_date = None, None
else:
    date_range = st.sidebar.date_input(
        "Chọn khoảng thời gian",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

# --- ÁP DỤNG BỘ LỌC ---
filtered_df = df.copy()

if selected_companies:
    filtered_df = filtered_df[filtered_df["companyName"].isin(selected_companies)]

if start_date and end_date:
    filtered_df = filtered_df[
        (filtered_df["approvedOn"].dt.date >= start_date) &
        (filtered_df["approvedOn"].dt.date <= end_date)
        ]

# --- GIAO DIỆN CHÍNH ---
st.title("📊 Dashboard Phân Tích Tuyển Dụng IT")
col1, col2, col3 = st.columns(3)
col1.metric("Tổng số Job", len(filtered_df))
col2.metric("Số công ty", filtered_df['companyName'].nunique())

all_skills_temp = [s for skills in filtered_df["skills_list"] for s in skills]
top_skill = Counter(all_skills_temp).most_common(1)[0][0] if all_skills_temp else "N/A"
col3.metric("Kỹ năng Hot nhất", top_skill)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏢 Top Công Ty", "🧠 Top Kỹ Năng", "📈 Xu Hướng",
    "☁ WordCloud", "Bg Cấp Bậc", "🔗 Combo Kỹ Năng"
])

with tab1:  # Top Công Ty
    st.subheader("Top 10 Công ty tuyển dụng nhiều nhất")
    if not filtered_df.empty:
        top_companies = filtered_df['companyName'].value_counts().head(10).sort_values()
        fig, ax = plt.subplots(figsize=(10, 6))
        top_companies.plot(kind='barh', color='#4CAF50', ax=ax)
        ax.set_xlabel("Số lượng Job")
        st.pyplot(fig)

with tab2:  # Top Kỹ Năng
    st.subheader("Top 10 Kỹ năng Hot nhất")
    if all_skills_temp:
        counts = Counter(all_skills_temp).most_common(10)
        skills, nums = zip(*counts)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(skills[::-1], nums[::-1], color="#2196F3")
        ax.set_xlabel("Số lượng")
        st.pyplot(fig)

with tab3:  # Xu Hướng
    st.subheader("Xu hướng đăng tin theo ngày")
    if not filtered_df.empty:
        daily = filtered_df.groupby(filtered_df["approvedOn"].dt.date).size()
        st.line_chart(daily)

with tab4:  # WordCloud
    st.subheader("WordCloud")
    if all_skills_temp:
        wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(all_skills_temp))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

with tab5:  # Cấp Bậc
    st.subheader("Phân bố Cấp bậc (Level)")
    if "jobLevel_processed" in filtered_df.columns:
        counts = filtered_df['jobLevel_processed'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90,
               colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        st.pyplot(fig)
    else:
        st.warning("Chưa có dữ liệu Cấp bậc.")

with tab6:  # Combo Kỹ Năng
    st.subheader("Các cặp kỹ năng thường đi cùng nhau")
    pairs_list = []
    for skills in filtered_df["skills_list"]:
        unique_skills = sorted(list(set(skills)))
        if len(unique_skills) < 2: continue
        for i in range(len(unique_skills)):
            for j in range(i + 1, len(unique_skills)):
                pairs_list.append(f"{unique_skills[i]} + {unique_skills[j]}")

    if pairs_list:
        common_pairs = Counter(pairs_list).most_common(10)
        labels, values = zip(*common_pairs)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(labels[::-1], values[::-1], color='purple')
        ax.set_xlabel("Số lần xuất hiện cùng nhau")
        st.pyplot(fig)
    else:
        st.info("Không đủ dữ liệu để phân tích combo.")

# Xem dữ liệu chi tiết
st.markdown("---")
st.subheader("📋 Dữ liệu chi tiết")

with st.expander("Xem danh sách Job (Table) chi tiết"):
    # Chọn các cột hiển thị cho đẹp (Tránh hiển thị hết nếu file quá nhiều cột rác)
    cols_to_show = [
        "jobTitle", "companyName", "salary", "jobLevel_processed",
        "city", "approvedOn", "skills", "jobUrl"
    ]
    # Chỉ hiển thị những cột thực sự tồn tại trong file của bạn
    final_cols = [c for c in cols_to_show if c in filtered_df.columns]

    # Hiển thị bảng
    st.dataframe(
        filtered_df[final_cols],
        use_container_width=True,
        height=500  # Chiều cao bảng (có thanh cuộn)
    )
    st.caption(f"Đang hiển thị {len(filtered_df)} job theo bộ lọc.")

# Tải PDF
st.sidebar.markdown("---")
st.sidebar.header("🖨️ Xuất báo cáo")

if st.sidebar.button("Tạo & Tải Báo Cáo PDF"):
    with st.spinner("Đang tạo file PDF... Vui lòng đợi..."):
        # Gọi hàm tạo PDF từ file export_report.py
        create_pdf()
        time.sleep(1)

    # Đọc file PDF dạng binary để cho phép tải về
    try:
        with open("report_it_full.pdf", "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.sidebar.download_button(
            label="📥 Nhấn để tải file PDF",
            data=PDFbyte,
            file_name="VietnamWorks_IT_Report.pdf",
            mime='application/octet-stream'
        )
        st.sidebar.success("Đã tạo xong! Hãy bấm nút trên để tải.")
    except FileNotFoundError:
        st.sidebar.error("Có lỗi khi tạo file PDF.")