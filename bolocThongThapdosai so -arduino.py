import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# ==== Cấu hình ====
PORT = 'COM17'  
BAUD = 9600
GROUND_TRUTH = 10.0  # khoảng cách thực tế (cm)

# ==== Danh sách dữ liệu ====
raw_values = []
filtered_values = []
timestamps = []

# ==== Kết nối Serial ====
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # đợi Arduino khởi động

print("Đang ghi dữ liệu...")

# ==== Đọc mẫu ====
start_time = time.time()
for _ in range(100):
    line = ser.readline().decode(errors='ignore').strip()
    timestamp = time.time() - start_time
    if "Raw" in line and "Filtered" in line:
        try:
            parts = line.split('|')
            raw = float(parts[0].split(':')[1].strip().replace("cm", ""))
            filtered = float(parts[1].split(':')[1].strip())
            raw_values.append(raw)
            filtered_values.append(filtered)
            timestamps.append(timestamp)
            print(f"Raw: {raw:.2f} | Filtered: {filtered:.2f} | Time: {timestamp:.3f}s")
        except:
            continue
ser.close()

# ==== Phân tích dữ liệu ====
raw_np = np.array(raw_values)
filtered_np = np.array(filtered_values)
timestamps_np = np.array(timestamps)

# Sai số trung bình
raw_error = np.abs(raw_np - GROUND_TRUTH) / GROUND_TRUTH * 100
filtered_error = np.abs(filtered_np - GROUND_TRUTH) / GROUND_TRUTH * 100

# Nhiễu (std)
raw_std = np.std(raw_np)
filtered_std = np.std(filtered_np)
noise_reduction = (1 - filtered_std / raw_std) * 100

# Thời gian trung bình giữa các mẫu
time_diffs = np.diff(timestamps_np)
avg_sample_interval = np.mean(time_diffs) * 1000  # ms

# Ước lượng độ trễ do lọc (EMA gây trễ 1–2 mẫu)
estimated_filter_delay = avg_sample_interval  # ~1 mẫu trễ
avg_response_time_raw = avg_sample_interval  # ms
avg_response_time_filtered = avg_sample_interval + estimated_filter_delay  # ms

# ==== Kết quả ====
print("\n=== PHÂN TÍCH ===")
print(f"Số mẫu thu được: {len(raw_values)}")
print(f"Sai số trung bình Raw (chưa lọc): {np.mean(raw_error):.2f}%")
print(f"Sai số trung bình Filtered (đã lọc): {np.mean(filtered_error):.2f}%")
print(f"Nhiễu Raw (std): {raw_std:.2f}")
print(f"Nhiễu Filtered (std): {filtered_std:.2f}")
print(f"Hiệu quả lọc (giảm nhiễu): {noise_reduction:.2f}%")
print(f"Thời gian đáp ứng trung bình (Raw): {avg_response_time_raw:.2f} ms")
print(f"Thời gian đáp ứng trung bình (Filtered ~ trễ hơn): {avg_response_time_filtered:.2f} ms")

# ==== Vẽ biểu đồ ====
plt.figure(figsize=(10, 5))
plt.plot(raw_np, label='Raw', linestyle='--', color='red')
plt.plot(filtered_np, label='Filtered', color='blue')
plt.axhline(GROUND_TRUTH, color='green', linestyle=':', label='Ground Truth')
plt.xlabel('Chỉ số mẫu')
plt.ylabel('Khoảng cách (cm)')
plt.title('So sánh Dữ liệu Raw vs Filtered')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
