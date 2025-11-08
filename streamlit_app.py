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
import plotly.express as px

# def setup_font():
#     system = platform.system()
#     if system == "Darwin":  # macOS
#         plt.rcParams['font.sans-serif'] = ['PingFang TC', 'Heiti TC', 'Arial Unicode MS']
#     elif system == "Windows":
#         plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
#     else:  # Linux / Colab
#         font_path = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
#         try:
#             font_manager.fontManager.addfont(font_path)
#             plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC']
#         except FileNotFoundError:
#             plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
#             print("⚠️ 找不到 Noto CJK 字型，中文可能無法顯示。")

#     plt.rcParams['axes.unicode_minus'] = False
#     print(f"✅ 已設定字型：{plt.rcParams['font.sans-serif'][0]}")

# # 初始化字型
# setup_font()

def setup_font():
    try:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Streamlit Cloud 內建
        plt.rcParams['axes.unicode_minus'] = False
        print(f"✅ 已設定字型：{plt.rcParams['font.sans-serif'][0]}")
    except Exception as e:
        print("⚠️ 字型設定失敗:", e)

setup_font()


#天氣預報
url_weather = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-897885FD-7D6F-4343-B7C8-5436A51D02B8&format=JSON&locationName=%E8%87%BA%E5%8C%97%E5%B8%82&sort=time'
# data = requests.get(url_weather)   # 取得 JSON 檔案的內容為文字
# data_json = data.json()    # 轉換成 JSON 格式
# location = data_json['records']['location']   # 取出 location 的內容
# for i in location:
#     city = i['locationName']    # 縣市名稱
#     #time[0]取第 1 筆時間段的預報（也就是「現在這一個時段」）。
#     wx8 = i['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
#     pop8 = i['weatherElement'][1]['time'][0]['parameter']['parameterName']   # 降雨機率
#     mint8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最低溫
#     ci8 = i['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
#     maxt8 = i['weatherElement'][4]['time'][0]['parameter']['parameterName']  # 最高溫

# res=(f'{city}未來 8 小時{wx8}，最高溫 {maxt8} 度，最低溫 {mint8} 度，降雨機率 {pop8} %，體感{ci8}')



# 1. 使用 st.cache_data 快取6小時
# @st.cache_data(ttl=21600)
# def get_weather():
#     data = requests.get(url_weather).json()
#     taipei = data['records']['location'][0]
#     wx8 = taipei['weatherElement'][0]['time'][0]['parameter']['parameterName']
#     pop8 = taipei['weatherElement'][1]['time'][0]['parameter']['parameterName']
#     mint8 = taipei['weatherElement'][2]['time'][0]['parameter']['parameterName']
#     ci8 = taipei['weatherElement'][3]['time'][0]['parameter']['parameterName']
#     maxt8 = taipei['weatherElement'][4]['time'][0]['parameter']['parameterName']
#     return f'台北市未來 6 小時{wx8}，最高溫 {maxt8} 度，最低溫 {mint8} 度，降雨機率 {pop8} %，體感 {ci8}'


# res=get_weather()

# # 4. 手動刷新按鈕（按下後會清除快取並重新抓 API）
# if st.button("刷新天氣 "):
#     get_weather.clear()  # 清除快取
#     st.experimental_rerun()  # 重新執行頁面




def get_weather():
    try:
        data = requests.get(url_weather, timeout=10).json()
        taipei = data['records']['location'][0]
        wx8 = taipei['weatherElement'][0]['time'][0]['parameter']['parameterName']
        return f'台北市天氣：{wx8}'
    except Exception as e:
        return f"抓取天氣失敗: {e}"

st.write(get_weather())


# --------------------------
# 讀取 CSV
# --------------------------
#df = pd.read_csv("data/youbike_data.csv")

url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
response = requests.get(url, timeout=10)
data = response.json()  # 轉成 Python list/dict

df = pd.DataFrame(data)  # 轉成 DataFrame
# --------------------------
# 行政區選單
# --------------------------
st.set_page_config(page_title="YouBike Dashboard", layout="wide")
df["mday"] = pd.to_datetime(df["mday"])
st.title("🚴即時Youbike站點分析系統")
st.write("資料更新時間：", df["mday"].max())
#unsafe_allow_html=True 允許顯示 HTML 標籤。你可以用 HTML 控制：font-size: 調整字體大小。font-weight: 設定粗細（例如 bold 或 600）。
st.markdown(f"<h3 style='color:#97CBFF; font-size:20px;'>📢天氣預報:{res}</h3>", unsafe_allow_html=True)
#st.write("📢天氣預報:"+res)


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
        #df_display['sna_display'] = df_display['sna'].str.replace(r'YouBike2\.0[_ ]?', '', regex=True)

        if df_display.empty:
            st.warning("查無相關站點，請換個關鍵字試試！")
        else:
            st.success(f"找到 {len(df_display)} 個相關站點")
            st.dataframe(df_display[['sna', 'sarea', 'available_rent_bikes', 'available_return_bikes']])
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
    #st.map(df_top)
    # --------------------------
    # 🗺️ Folium 地圖
    # --------------------------
    st.subheader("🗺️ 地圖視覺化")
    st.write("圓圈大小代表可借車輛多寡(可點擊查看)")

    # if not df_top.empty:
    #      center_lat = df_top['latitude'].astype(float).mean()
    #      center_lng = df_top['longitude'].astype(float).mean()
    # else:
    #      center_lat = df_area['latitude'].astype(float).mean()
    #      center_lng = df_area['longitude'].astype(float).mean()

    # m = folium.Map(location=[center_lat, center_lng], zoom_start=14)

    # for _, row in df_top.iterrows():
    #      folium.CircleMarker(
    #          location=[float(row['latitude']), float(row['longitude'])],
    #          radius=row['available_rent_bikes'] * 0.5 + 3,
    #          popup=folium.Popup(
    #              f'<div style="font-size: 16px; font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 10px; border-radius: 10px;">'# 加上這一行來設定字體大小
    #              f"📍{row['sna']}<br>"
    #              f"🚲 可借車數：{row['available_rent_bikes']}<br>"
    #              f"🅿️ 可還車位：{row['available_return_bikes']}<br>"
    #              f"📫 地址：{row['ar']}"
    #              f'</div>',
    #              max_width=600,  # 最大寬度
    #              min_width=300,  # 最小寬度
    #              max_height=400   # 最大高度
    #          ),
    #          color='blue',
    #          fill=True,
    #          fill_color='cyan',
    #          fill_opacity=0.6
    #      ).add_to(m)

    # st_folium(m, width=800, height=500)
    if not df_top.empty:
    # 建立 Plotly 地圖

        fig = px.scatter_mapbox(
            df_top,
            lat="latitude",
            lon="longitude",
            hover_name="sna",  # 站名
            hover_data={
                "available_rent_bikes": True,  # 顯示可借
                "available_return_bikes": True,  # 顯示可還
                "ar": True,  # 顯示地址
                "latitude": False,  # 不顯示經緯度
                "longitude": False  # 不顯示經緯度
            },
            size="available_rent_bikes",  # 圓圈大小
            size_max=50,
            color="available_rent_bikes",
            color_continuous_scale="Purples",
            title=f"{selected_area} YouBike 站點地圖",
            height=600,   # ✅ 放大地圖高度
            width=1000    # ✅ 放大地圖寬度
        )
        #自訂hover顯示文字
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br><br>" +
                        "🚴可借車數：%{customdata[0]} 台<br>" +
                        "🅿️可還車數：%{customdata[1]} 台<br>" +
                        "📍地址：%{customdata[2]}<extra></extra>"
        )

    # 更新地圖設置
        fig.update_layout(
            mapbox_style="open-street-map",  # 使用開放街圖樣式
            mapbox_zoom=13,  # 初始縮放級別
            mapbox_center_lat = df_top['latitude'].mean(),
            mapbox_center_lon = df_top['longitude'].mean(),
            showlegend=False,
            # 🎨 顏色比例尺放到下方
            coloraxis_colorbar=dict(
                title="可借車數",
                orientation='h',  # 橫向排列
                y=-0.2,          # 向下移動（可依需求微調 -0.3 ~ -0.15）
                x=0.5,            # 水平置中
                xanchor='center',
                len=0.6,          # 比例尺長度
                thickness=15      # 比例尺厚度
                )
        )

    # 顯示 Plotly 地圖
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("無可顯示的站點，請檢查過濾條件！")


with col2:
    pass  # 空白欄

# --------------------------
# ⚠️ 特殊站點提醒
# --------------------------
with col3:
    st.subheader("⚠️ 站點提醒")

    no_bikes = df[df['available_rent_bikes'] == 0]
    no_space = df[df['available_return_bikes'] == 0]
    # 計算前三名無可借車的行政區
    top3_no_bikes = no_bikes['sarea'].value_counts().head(3)
    # 計算前三名無可還車位的行政區
    top3_no_space = no_space['sarea'].value_counts().head(3)

    col1, col2 = st.columns(2)
    with col1:
        st.error(f"🚫 無可借車站點：{len(no_bikes)} 個")
        if not top3_no_bikes.empty:
            st.write("前三名行政區：")
            for area, count in top3_no_bikes.items():
                st.write(f"{area}：{count} 個站點")
        st.dataframe(no_bikes[['sarea', 'sna', 'ar']])

    with col2:
        st.warning(f"🈵 無可還車位站點：{len(no_space)} 個")
        if not top3_no_space.empty:
            st.write("前三名行政區：")
            for area, count in top3_no_space.items():
                st.write(f"{area}：{count} 個站點")
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
        st.write("你的收藏站點：(可自行複製前往站點搜尋)")
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
        title='各行政區平均可借/可還車數(可點擊查看)',
        xaxis_title='行政區',
        yaxis_title='平均數量',
        barmode='group',  # 並排柱狀
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True,width=700)

