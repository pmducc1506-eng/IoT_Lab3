# IoT Lab 2: Thu thập, Lưu trữ và Tiền xử lý dữ liệu IoT

## 1. Cấu trúc thư mục
- `firmware/`: Mã nguồn ESP32, diagram.json và libraries.txt trên Wokwi.
- `scripts/`: Code Python collector (subscribe MQTT & ghi InfluxDB) và preprocessing (IQR, resampling, chuẩn hóa).
- `app/`: Dashboard giám sát real-time Streamlit.

## 2. Hướng dẫn khởi chạy
1. Khởi chạy InfluxDB v2 trên `http://localhost:8086`.
2. Khởi động mô phỏng ESP32 trên Wokwi.
3. Chạy script thu thập dữ liệu: `python scripts/collector.py`
4. Chạy script tiền xử lý: `python scripts/preprocessing.py`
5. Khởi chạy Dashboard: `python -m streamlit run app/app.py`