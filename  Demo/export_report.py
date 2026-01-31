import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import ast
import os
import platform

# --- THƯ VIỆN REPORTLAB (TẠO PDF) ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

# --- CẤU HÌNH ---
INPUT_FILE = "vnworks_it_jobs_clean.csv"
OUTPUT_PDF = "report_it_full.pdf"
TEMP_IMG_FOLDER = "temp_images"

# Tạo thư mục chứa ảnh tạm
if not os.path.exists(TEMP_IMG_FOLDER):
    os.makedirs(TEMP_IMG_FOLDER)


# --- 1. CẤU HÌNH FONT TIẾNG VIỆT ---
def configure_fonts():
    """Đăng ký font Arial để hiển thị tiếng Việt trong PDF và Matplotlib"""
    # 1.1 Cho ReportLab (PDF)
    font_name = "Helvetica"  # Mặc định
    try:
        # Đường dẫn font Windows chuẩn
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Arial', font_path))
            font_name = "Arial"
        else:
            print("⚠️ Không tìm thấy font Arial hệ thống. PDF có thể lỗi font tiếng Việt.")
    except:
        pass

    # 1.2 Cho Matplotlib (Biểu đồ)
    system_name = platform.system()
    if system_name == "Windows":
        plt.rcParams['font.family'] = 'Segoe UI'
    else:
        plt.rcParams['font.family'] = 'Sans-serif'

    return font_name


FONT_NAME = configure_fonts()


# --- 2. HÀM VẼ BIỂU ĐỒ ---
def generate_charts(df):
    print("🎨 Vẽ biểu đồ phân tích...")

    # Chuyển đổi dữ liệu cần thiết
    if "approvedOn" in df.columns:
        df["approvedOn"] = pd.to_datetime(df["approvedOn"], errors='coerce')

    # Parse skills_list an toàn
    skills_data = []
    if "skills_list" in df.columns:
        for item in df["skills_list"]:
            try:
                val = ast.literal_eval(item) if isinstance(item, str) else item
                if isinstance(val, list): skills_data.append(val)
            except:
                pass

    # CHART 1: TOP CÔNG TY
    plt.figure(figsize=(10, 5))
    df['companyName'].value_counts().head(10).sort_values().plot(kind='barh', color='#4CAF50')
    plt.title("Top 10 Công ty tuyển dụng nhiều nhất")
    plt.xlabel("Số lượng Job")
    plt.tight_layout()
    plt.savefig(f"{TEMP_IMG_FOLDER}/1_companies.png");
    plt.close()

    # CHART 2: TOP KỸ NĂNG
    flat_skills = [s for sublist in skills_data for s in sublist]
    if flat_skills:
        counts = Counter(flat_skills).most_common(10)
        labels, values = zip(*counts)
        plt.figure(figsize=(10, 5))
        plt.barh(labels[::-1], values[::-1], color='#2196F3')
        plt.title("Top 10 Kỹ năng lập trình phổ biến")
        plt.xlabel("Số lần xuất hiện")
        plt.tight_layout()
        plt.savefig(f"{TEMP_IMG_FOLDER}/2_skills.png");
        plt.close()

    # CHART 3: XU HƯỚNG ĐĂNG TIN
    if "approvedOn" in df.columns:
        trend = df.groupby(df["approvedOn"].dt.date).size()
        plt.figure(figsize=(10, 4))
        trend.plot(kind='line', marker='o', color='orange')
        plt.title("Xu hướng đăng tin tuyển dụng theo ngày")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{TEMP_IMG_FOLDER}/3_trend.png");
        plt.close()

    # CHART 4: WORDCLOUD
    if flat_skills:
        wc = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate(
            " ".join(flat_skills))
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.title("WordCloud Từ khóa Công nghệ")
        plt.tight_layout()
        plt.savefig(f"{TEMP_IMG_FOLDER}/4_wordcloud.png");
        plt.close()

    # CHART 5: PHÂN BỐ CẤP BẬC (LEVEL)
    if "jobLevel_processed" in df.columns:
        plt.figure(figsize=(7, 7))
        counts = df['jobLevel_processed'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90,
                colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        plt.title("Cơ cấu Cấp bậc (Level)")
        plt.tight_layout()
        plt.savefig(f"{TEMP_IMG_FOLDER}/5_level.png");
        plt.close()

    # CHART 6: COMBO KỸ NĂNG
    pairs = []
    for s_list in skills_data:
        if len(s_list) < 2: continue
        unique = sorted(list(set(s_list)))  # Loại trùng lặp trong 1 job
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                pairs.append(f"{unique[i]} + {unique[j]}")

    if pairs:
        common_pairs = Counter(pairs).most_common(10)
        plabels, pvalues = zip(*common_pairs)
        plt.figure(figsize=(10, 6))
        plt.barh(plabels[::-1], pvalues[::-1], color='purple')
        plt.title("Top 10 Combo Kỹ năng thường đi cùng nhau")
        plt.xlabel("Số lần xuất hiện")
        plt.tight_layout()
        plt.savefig(f"{TEMP_IMG_FOLDER}/6_combo.png");
        plt.close()


# --- 3. HÀM TẠO PDF ---
def create_pdf():
    print("📄 Đang khởi tạo file PDF...")

    # Đọc dữ liệu
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file clean csv.")
        return

    # Vẽ biểu đồ
    generate_charts(df)

    # Thiết lập PDF
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    # Tạo style riêng
    title_style = ParagraphStyle('TitleVN', parent=styles['Title'], fontName=FONT_NAME, fontSize=20, spaceAfter=20,
                                 alignment=TA_CENTER, textColor='navy')
    h2_style = ParagraphStyle('H2VN', parent=styles['Heading2'], fontName=FONT_NAME, fontSize=14, spaceAfter=10,
                              spaceBefore=15, textColor='#333333')
    body_style = ParagraphStyle('BodyVN', parent=styles['BodyText'], fontName=FONT_NAME, fontSize=11, spaceAfter=12,
                                alignment=TA_JUSTIFY, leading=14)

    story = []

    # --- TRANG 1: TỔNG QUAN ---
    story.append(Paragraph("BÁO CÁO THỊ TRƯỜNG TUYỂN DỤNG IT", title_style))
    story.append(Paragraph(f"<b>Nguồn dữ liệu:</b> VietnamWorks", body_style))
    story.append(Paragraph(f"<b>Tổng số tin tuyển dụng:</b> {len(df)} job", body_style))
    story.append(Paragraph(f"<b>Số lượng công ty tham gia:</b> {df['companyName'].nunique()} công ty", body_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("1. Top Doanh Nghiệp Tuyển Dụng", h2_style))
    story.append(Paragraph(
        "Biểu đồ dưới đây thể hiện các công ty có nhu cầu tuyển dụng nhân sự IT lớn nhất trong tập dữ liệu thu thập được.",
        body_style))
    if os.path.exists(f"{TEMP_IMG_FOLDER}/1_companies.png"):
        story.append(RLImage(f"{TEMP_IMG_FOLDER}/1_companies.png", width=6.5 * inch, height=3.2 * inch))

    story.append(Paragraph("2. Xu Hướng Theo Thời Gian", h2_style))
    story.append(
        Paragraph("Diễn biến số lượng tin đăng theo ngày, phản ánh nhu cầu thị trường trong khoảng thời gian khảo sát.",
                  body_style))
    if os.path.exists(f"{TEMP_IMG_FOLDER}/3_trend.png"):
        story.append(RLImage(f"{TEMP_IMG_FOLDER}/3_trend.png", width=6.5 * inch, height=2.8 * inch))

    story.append(PageBreak())  # Sang trang mới

    # --- TRANG 2: KỸ NĂNG ---
    story.append(Paragraph("3. Phân Tích Kỹ Năng (Skills)", h2_style))
    story.append(Paragraph("Các công nghệ và ngôn ngữ lập trình được yêu cầu nhiều nhất.", body_style))
    if os.path.exists(f"{TEMP_IMG_FOLDER}/2_skills.png"):
        story.append(RLImage(f"{TEMP_IMG_FOLDER}/2_skills.png", width=6.5 * inch, height=3.2 * inch))

    story.append(Paragraph("4. Hệ Sinh Thái Kỹ Năng (Combo)", h2_style))
    story.append(Paragraph(
        "Phân tích này cho thấy các kỹ năng thường xuất hiện cùng nhau (Co-occurrence). Ví dụ: Python thường đi kèm với Django hoặc AWS.",
        body_style))
    if os.path.exists(f"{TEMP_IMG_FOLDER}/6_combo.png"):
        story.append(RLImage(f"{TEMP_IMG_FOLDER}/6_combo.png", width=6.5 * inch, height=3.5 * inch))

    story.append(PageBreak())  # Sang trang mới

    # --- TRANG 3: CẤP BẬC & WORDCLOUD ---
    story.append(Paragraph("5. Phân Bố Cấp Bậc (Level)", h2_style))
    story.append(Paragraph(
        "Tỷ lệ tuyển dụng dựa trên cấp bậc (Intern, Junior, Senior, Manager) được trích xuất từ tiêu đề công việc.",
        body_style))
    if os.path.exists(f"{TEMP_IMG_FOLDER}/5_level.png"):
        story.append(RLImage(f"{TEMP_IMG_FOLDER}/5_level.png", width=5 * inch, height=5 * inch))

    story.append(Paragraph("6. Từ Khóa Nổi Bật (WordCloud)", h2_style))
    if os.path.exists(f"{TEMP_IMG_FOLDER}/4_wordcloud.png"):
        story.append(RLImage(f"{TEMP_IMG_FOLDER}/4_wordcloud.png", width=6.5 * inch, height=3.2 * inch))

    # XUẤT FILE
    doc.build(story)
    print(f"\n✅ XUẤT BÁO CÁO THÀNH CÔNG: {OUTPUT_PDF}")
    print(f"👉 Mở file {OUTPUT_PDF} để kiểm tra!")


if __name__ == "__main__":
    create_pdf()