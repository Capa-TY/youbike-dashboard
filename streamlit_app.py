import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import platform
import matplotlib.pyplot as plt
from matplotlib import font_manager
import requests
#from sklearn.linear_model import LinearRegression
import math
import plotly.graph_objects as go

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

# 初始化字型
setup_font()


# --------------------------
# 讀取 CSV
# --------------------------
#df = pd.read_csv("data/youbike_data.csv")

url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
response = requests.get(url)
data = response.json()  # 轉成 Python list/dict

df = pd.DataFrame(data)  # 轉成 DataFrame
# --------------------------
# 行政區選單
# --------------------------

df["mday"] = pd.to_datetime(df["mday"])
st.title("🚴Youbike站點分析系統")
st.write("資料更新時間：", df["mday"].max())

st.set_page_config(page_title="YouBike Dashboard", layout="wide")
col1, col2, col3 = st.columns([5,0.002,5])  # 左右欄 + 小空隙
# --------------------------
# 行政區選單
# --------------------------
with col1:
    areas = df['sarea'].unique()
    selected_area = st.selectbox("選擇行政區", areas)
    df_area = df[df['sarea'] == selected_area]


    st.subheader("🔍 站點搜尋")
    keyword = st.text_input("輸入站點關鍵字（例如：台大、公館、中正紀念堂）")

    if keyword:
        keyword_norm = keyword.replace("臺", "台")
        df['sna_normalized'] = df['sna'].str.replace("臺", "台")

        df_display = df[df['sna_normalized'].str.contains(keyword_norm, case=False, na=False)]

        # 去掉前面的 "YouBike2.0_" 或 "YouBike2.0 " 文字
        df_display['sna_display'] = df_display['sna'].str.replace(r'YouBike2\.0[_ ]?', '', regex=True)

        if df_display.empty:
            st.warning("查無相關站點，請換個關鍵字試試！")
        else:
            st.success(f"找到 {len(df_display)} 個相關站點")
            st.dataframe(df_display[['sna_display', 'sarea', 'available_rent_bikes', 'available_return_bikes']])
    else:
        df_display = df_area


    # --------------------------
    # 🏅 排序功能
    # --------------------------


    st.subheader("🏅 排序選項")
    sort_option = st.radio("選擇排序方式", ["可借車數（多→少）", "可還車位（多→少）"])
    if sort_option == "可借車數（多→少）":
        df_display = df_display.sort_values(by='available_rent_bikes', ascending=False)
    else:
        df_display = df_display.sort_values(by='available_return_bikes', ascending=False)

    top_n = 10
    df_top = df_display.head(top_n)
    st.dataframe(df_top[['sarea', 'sna', 'available_rent_bikes', 'available_return_bikes', 'ar']])

    # --------------------------
    # 🗺️ Folium 地圖
    # --------------------------
    st.subheader("🗺️ 地圖視覺化")

    if not df_top.empty:
        center_lat = df_top['latitude'].astype(float).mean()
        center_lng = df_top['longitude'].astype(float).mean()
    else:
        center_lat = df_area['latitude'].astype(float).mean()
        center_lng = df_area['longitude'].astype(float).mean()

    m = folium.Map(location=[center_lat, center_lng], zoom_start=14)

    for _, row in df_top.iterrows():
        folium.CircleMarker(
            location=[float(row['latitude']), float(row['longitude'])],
            radius=row['available_rent_bikes'] * 0.5 + 3,
            popup=(
                f"📍{row['sna']}<br>"
                f"🚲 可借車數：{row['available_rent_bikes']}<br>"
                f"🅿️ 可還車位：{row['available_return_bikes']}<br>"
                f"📫 地址：{row['ar']}"
            ),
            color='blue',
            fill=True,
            fill_color='cyan',
            fill_opacity=0.6
        ).add_to(m)

    st_folium(m, width=700, height=500)

with col2:
    pass  # 空白欄

# --------------------------
# ⚠️ 特殊站點提醒
# --------------------------
with col3:
    st.subheader("⚠️ 站點提醒")

    no_bikes = df[df['available_rent_bikes'] == 0]
    no_space = df[df['available_return_bikes'] == 0]

    col1, col2 = st.columns(2)
    with col1:
        st.error(f"🚫 無可借車站點：{len(no_bikes)} 個")
        st.dataframe(no_bikes[['sarea', 'sna', 'ar']])

    with col2:
        st.warning(f"🈵 無可還車位站點：{len(no_space)} 個")
        st.dataframe(no_space[['sarea', 'sna', 'ar']])


    st.subheader("⭐ 收藏常用站點")

    # 建立 session state 來儲存收藏站點
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    # 顯示可收藏站點列表
    areas = df['sarea'].unique().tolist()  # 取唯一行政區
    selected_area_fav = st.selectbox("先選擇行政區", areas)

    # 過濾該區的站點
    df_area = df[df['sarea'] == selected_area_fav]
    stations = df_area['sna'].tolist()  # 顯示整理過的站點名稱
    selected_station = st.selectbox("選擇站點加入收藏", stations)


    if st.button("加入收藏"):
        if selected_station not in st.session_state.favorites:
            st.session_state.favorites.append(selected_station)
            st.success(f"{selected_station} 已加入收藏！")
        else:
            st.info(f"{selected_station} 已經在收藏清單中")

    # 顯示收藏清單
    if st.session_state.favorites:
        st.write("你的收藏站點：")
        for s in st.session_state.favorites:
            st.write("•", s)
            

    # --------------------------
    # 📊 各行政區平均可借車數長條圖
    # --------------------------
    # 

    st.subheader("📊 各行政區平均可借/可還車數")

    # 計算各行政區平均可借與可還
    avg_stats = df.groupby('sarea')[['available_rent_bikes', 'available_return_bikes']].mean()
    avg_stats = avg_stats.sort_values(by='available_rent_bikes', ascending=False)

    # 建立雙柱狀圖
    fig = go.Figure(data=[
        go.Bar(name='可借車數', x=avg_stats.index, y=avg_stats['available_rent_bikes'], marker_color='skyblue'),
        go.Bar(name='可還車位', x=avg_stats.index, y=avg_stats['available_return_bikes'], marker_color='lightgreen')
    ])

    # 設定圖表布局
    fig.update_layout(
        title='各行政區平均可借/可還車數',
        xaxis_title='行政區',
        yaxis_title='平均數量',
        barmode='group',  # 並排柱狀
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True,width=500)







# df['hour'] = pd.to_datetime(df['mday']).dt.hour
# df['weekday'] = pd.to_datetime(df['mday']).dt.weekday

# # 選站點
# station = st.selectbox("選擇站點", df['sna'].unique())
# df_station = df[df['sna'] == station]

# # 建立簡單模型
# X = df_station[['hour', 'weekday', 'available_rent_bikes', 'available_return_bikes']]
# y = df_station['available_rent_bikes'].shift(-1).fillna(method='ffill').fillna(0)  # 預測下一小時

# model = LinearRegression()
# model.fit(X, y)

# # 預測
# latest = X.iloc[-1:]
# pred = model.predict(latest)[0]
# st.write(f"目前可借車數: {latest['available_rent_bikes'].values[0]}")
# st.write(f"預測下一小時可借車數: {int(pred)}")
