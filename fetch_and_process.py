import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import platform
import os
os.makedirs("data", exist_ok=True)
os.makedirs("figures", exist_ok=True)
# ==========================
# ✅ 字型設定（自動偵測系統）
# ==========================
def setup_font():
    system = platform.system()
    if system == "Darwin":  # macOS
        plt.rcParams['font.sans-serif'] = ['PingFang TC', 'Heiti TC', 'Arial Unicode MS']
    elif system == "Windows":
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
    else:  # Linux / Colab
        font_path = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
        try:
            font_manager.fontManager.addfont(font_path)
            plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC']
        except FileNotFoundError:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            print("⚠️ 找不到 Noto CJK 字型，中文可能無法顯示。")

    plt.rcParams['axes.unicode_minus'] = False
    print(f"✅ 已設定字型：{plt.rcParams['font.sans-serif'][0]}")

setup_font()

# ==========================
# 🚴‍♂️ 抓取 YouBike 即時資料
# ==========================
url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
data=requests.get(url).json()

# 轉成 DataFrame
df = pd.DataFrame(data)

# 2️⃣ 資料清理
df["mday"] = pd.to_datetime(df["mday"])
df["hour"] = df["mday"].dt.hour
df["weekday"] = df["mday"].dt.day_name()
df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce').fillna(0).astype(int)
df["available_rent_bikes"] = pd.to_numeric(df["available_rent_bikes"], errors='coerce').fillna(0).astype(int)
df["usage_rate"] = df["available_rent_bikes"] / df["Quantity"]

# 3️⃣ 儲存 CSV
df.to_csv("data/youbike_data.csv", index=False, encoding="utf-8-sig")
print("✅ 資料已儲存到 data/youbike_data.csv")
# 4️⃣ 畫圖
# 行政區平均使用率
area_usage = df.groupby("sarea")["usage_rate"].mean().sort_values(ascending=False)
plt.figure(figsize=(10,5))
area_usage.plot(kind="bar", color="skyblue")
plt.title("各行政區 YouBike 平均可借車比例")
plt.ylabel("可借車比例")
plt.xlabel("行政區")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figures/usage_by_area.png")

# 每小時平均使用率
hourly_usage = df.groupby("hour")["usage_rate"].mean()
plt.figure(figsize=(10,5))
hourly_usage.plot(kind="line", marker="o")
plt.title("YouBike 每小時平均使用率變化")
plt.xlabel("小時")
plt.ylabel("平均可借車比例")
plt.grid(True)
plt.tight_layout()
plt.savefig("figures/hourly_usage.png")

print("✅ CSV 與圖表已生成")
