import pandas as pd
import numpy as np
import os

# 1. Tạo 720 mốc thời gian (60 phút, chu kỳ 5 giây/mẫu)
timestamps = pd.date_range(start="2026-10-25 08:00:00", periods=720, freq="5s")
t = np.linspace(0, 4 * np.pi, 720)

# 2. Sinh dữ liệu giả lập có biến thiên thực tế (chuẩn dải nhiệt độ, độ ẩm, khoảng cách)
temperature = 25.0 + 4.0 * np.sin(t) + np.random.normal(0, 0.1, 720)       # 21 - 29 °C
humidity = 60.0 - 10.0 * np.cos(t) + np.random.normal(0, 0.2, 720)         # 50 - 70 %RH
distance_cm = 100.0 + 50.0 * np.sin(2 * t) + np.random.normal(0, 0.3, 720)  # 50 - 150 cm

# 3. Đóng gói chuẩn Cột theo yêu cầu Bài thực hành 3
df_sample = pd.DataFrame({
    'timestamp': timestamps.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'temperature': np.round(temperature, 2),
    'humidity': np.round(humidity, 2),
    'distance_cm': np.round(distance_cm, 2),
    'device_id': 'ESP32_WOKWI_01',
    'session_id': 'SESSION_LAB3_01',
    'sequence': np.arange(1, 721),
    'uptime_s': np.arange(1, 721) * 5,
    'data_source': 'Python_Generated_Sample'
})

# 4. Xuất file du_lieu_mau_B2.csv ra thư mục gốc IoT_Lab2
output_path = os.path.join(os.path.dirname(__file__), '..', 'du_lieu_mau_B2.csv')
df_sample.to_csv(output_path, index=False)

print(f"[THÀNH CÔNG] Đã tạo file du_lieu_mau_B2.csv ({len(df_sample)} dòng) tại thư mục gốc IoT_Lab2!")