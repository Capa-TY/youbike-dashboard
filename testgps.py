import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components

st.title("YouBike 附近站點查詢📍")

# -----------------------------
# 1️⃣ 載入站點資料
# -----------------------------
url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
data = pd.read_json(url)
df = pd.DataFrame(data)

# -----------------------------
# 2️⃣ 使用者 GPS
# -----------------------------
st.subheader("請允許瀏覽器取得位置")

gps_js = """
<script>
navigator.geolocation.getCurrentPosition(
    function(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const input = window.parent.document.getElementById('gps_input');
        input.value = lat + ',' + lon;
        input.dispatchEvent(new Event('change'));
    },
    function(err) {
        alert('無法取得位置，請手動輸入！');
    }
)
</script>
<input type="text" id="gps_input" style="display:none;">
"""

gps_str = components.html(gps_js, height=0, width=0)

# -----------------------------
# 3️⃣ 手動或自動取得 GPS
# -----------------------------
gps_input = st.text_input("若瀏覽器無法取得位置，請手動輸入經緯度 (lat,lon)", "")
if gps_input:
    user_lat, user_lon = map(float, gps_input.split(","))
else:
    # 先給一個預設值，等瀏覽器取得再更新
    user_lat, user_lon = 25.0330, 121.5654  # 台北市中心

# -----------------------------
# 4️⃣ 計算距離找最近站點
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi, dlambda = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

df['distance'] = df.apply(lambda row: haversine(user_lat, user_lon, row['latitude'], row['longitude']), axis=1)
df_nearby = df.nsmallest(10, 'distance')

st.write(f"📍 以你的位置為中心，最近 {len(df_nearby)} 個站點：")
st.dataframe(df_nearby[['sna','available_rent_bikes','available_return_bikes','ar','distance']])

# -----------------------------
# 5️⃣ 顯示 Plotly 地圖
# -----------------------------
fig = px.scatter_mapbox(
    df_nearby,
    lat="latitude",
    lon="longitude",
    hover_name="sna",
    hover_data={
        "available_rent_bikes": True,
        "available_return_bikes": True,
        "ar": True,
        "distance": True,
        "latitude": False,
        "longitude": False
    },
    size="available_rent_bikes",
    size_max=50,
    color="available_rent_bikes",
    color_continuous_scale="Agsunset",
    height=700,
)

fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br><br>" +
                  "可借車數：%{customdata[0]} 台<br>" +
                  "可還車數：%{customdata[1]} 台<br>" +
                  "地址：%{customdata[2]}<br>" +
                  "距離：%{customdata[3]:.2f} km<extra></extra>"
)

fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_zoom=14,
    mapbox_center_lat=user_lat,
    mapbox_center_lon=user_lon,
    showlegend=False,
    coloraxis_colorbar=dict(
        title="可借車數",
        orientation='h',
        y=-0.25,
        x=0.5,
        xanchor='center',
        len=0.6,
        thickness=15
    ),
    margin=dict(l=0,r=0,t=50,b=0)
)

st.plotly_chart(fig, use_container_width=True)
