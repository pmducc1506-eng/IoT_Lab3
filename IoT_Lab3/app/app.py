import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.set_page_config(page_title="IoT Dashboard & ML Forecast", layout="wide")

st.title("📊 IoT Real-Time Sensor Dashboard & ML Forecast")
st.caption("Hệ thống giám sát chuỗi thời gian & Dự báo nhiệt độ phút tiếp theo (Bài 3)")

# 1. Đường dẫn các tệp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "du_lieu_mau_B2.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model6.pkl")

# 2. Đọc dữ liệu từ du_lieu_mau_B2.csv
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Lấy 12 mẫu gần nhất (tương đương cửa sổ 60s)
    window_12 = df.tail(12).reset_index(drop=True)
    latest_sample = window_12.iloc[-1]

    # Hiển thị 3 chỉ số cảm biến hiện tại (KPI Metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Nhiệt độ hiện tại", f"{latest_sample['temperature']:.2f} °C")
    col2.metric("💧 Độ ẩm hiện tại", f"{latest_sample['humidity']:.2f} %")
    col3.metric("📏 Khoảng cách", f"{latest_sample['distance_cm']:.2f} cm")

    st.markdown("---")

    # 3. Trích xuất 21 đặc trưng cho cửa sổ 12 mẫu gần nhất
    t_s = np.arange(12) * 5
    feats = []
    for col in ['temperature', 'humidity', 'distance_cm']:
        x = window_12[col].values
        feats.extend([
            np.mean(x), np.std(x, ddof=0), np.min(x), np.max(x),
            np.ptp(x), x[-1] - x[0], np.polyfit(t_s, x, 1)[0]
        ])

    # 4. Tải mô hình ML và Dự báo nhiệt độ phút tiếp theo
    if os.path.exists(MODEL_PATH):
        model6 = joblib.load(MODEL_PATH)
        temp_forecast = model6.predict([feats])[0]
        temp_diff = temp_forecast - latest_sample['temperature']

        st.subheader("🔮 Kết quả Dự báo Học máy (Ridge Regression - 6 Đặc trưng)")
        st.metric(
            label="Nhiệt độ trung bình dự báo cho 60 giây tiếp theo (temperature_forecast_next60s)",
            value=f"{temp_forecast:.2f} °C",
            delta=f"{temp_diff:+.2f} °C so với hiện tại"
        )
    else:
        st.warning("⚠️ Không tìm thấy tệp mô hình `model6.pkl` tại thư mục gốc!")

    st.markdown("---")
    st.subheader("📈 Biểu đồ dữ liệu cảm biến thời gian thực (12 mẫu gần nhất)")
    st.line_chart(window_12.set_index('timestamp')[['temperature', 'humidity', 'distance_cm']])

else:
    st.error("❌ Không tìm thấy tệp `du_lieu_mau_B2.csv`!")