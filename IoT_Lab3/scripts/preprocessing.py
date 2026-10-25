import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "baMu4IPo-l0Fv2upMh26YsInfOCjXymmQC71_-Buv_yn9qiFyZEvIHzBvXMkW2tbsBJLqG8exAUFJUz5H728Bg=="  # <--- Thay Token của bạn
INFLUX_ORG = "IoT_Org"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def preprocess():
    query_api = client.query_api()
    
    # 1. Đọc dữ liệu thô từ iot_raw_db
    query = f'''
    from(bucket: "iot_raw_db")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_data")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df = query_api.query_data_frame(query)
    if df.empty:
        print("Chưa có đủ dữ liệu thô trong database để xử lý. Hãy chờ Wokwi gửi thêm vài phút...")
        return

    df['_time'] = pd.to_datetime(df['_time'])
    df.set_index('_time', inplace=True)

    # 2. Xử lý giá trị khuyết
    cols = ['temperature', 'humidity', 'distance_cm']
    for c in cols:
        if c in df.columns:
            df[c] = df[c].interpolate(method='time')

    # 3. Lọc Outlier bằng IQR[cite: 1]
    for c in cols:
        if c in df.columns:
            Q1 = df[c].quantile(0.25)
            Q3 = df[c].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df[c] = np.where((df[c] < lower) | (df[c] > upper), np.nan, df[c])
            df[c] = df[c].ffill().bfill()

    # 4. Resampling 1 phút[cite: 1]
    df_resampled = df[cols].resample('1Min').mean()

    # 5. Tạo đặc trưng (Rolling mean & Delta)[cite: 1]
    df_resampled['temp_rolling_mean'] = df_resampled['temperature'].rolling(window=3, min_periods=1).mean()
    df_resampled['dist_delta'] = df_resampled['distance_cm'].diff().fillna(0)

    # 6. Chuẩn hóa dữ liệu bằng StandardScaler[cite: 1]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_resampled[cols].fillna(0))
    df_resampled['temp_scaled'] = scaled[:, 0]
    df_resampled['hum_scaled'] = scaled[:, 1]

    # 7. Lưu vào bucket iot_processed_db[cite: 1]
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for timestamp, row in df_resampled.dropna().iterrows():
        p = Point("processed_sensor_data") \
            .time(timestamp) \
            .field("temperature", float(row['temperature'])) \
            .field("humidity", float(row['humidity'])) \
            .field("distance_cm", float(row['distance_cm'])) \
            .field("temp_rolling_mean", float(row['temp_rolling_mean'])) \
            .field("dist_delta", float(row['dist_delta'])) \
            .field("temp_scaled", float(row['temp_scaled']))
        write_api.write(bucket="iot_processed_db", org=INFLUX_ORG, record=p)

    print("[SUCCESS] Đã hoàn thành tiền xử lý và lưu dữ liệu mới vào iot_processed_db!")

if __name__ == "__main__":
    preprocess()