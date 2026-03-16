import math
import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

st.set_page_config(
    page_title="教授拜託給我一百100分",
    page_icon="🌍",
    layout="wide"
)

# Session state initialization

if "mode" not in st.session_state:
    st.session_state.mode = None

if "result" not in st.session_state:
    st.session_state.result = None


# Functions
def get_coordinates(place_name):
    try:
        geolocator = Nominatim(user_agent="great_circle_distance_homework")
        location = geolocator.geocode(place_name, timeout=10)
        if location is None:
            return None, None, None
        return location.latitude, location.longitude, location.address
    except Exception:
        return None, None, None


def great_circle_distance(lat1, lon1, lat2, lon2):
    r = 6371  # Earth radius in km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    value = (
        math.sin(lat1_rad) * math.sin(lat2_rad)
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(lon1_rad - lon2_rad)
    )
    value = min(1.0, max(-1.0, value))

    distance = r * math.acos(value)
    return distance


def create_map(lat1, lon1, name1, lat2, lon2, name2):
    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=3)

    folium.Marker(
        [lat1, lon1],
        popup=name1,
        tooltip=name1,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    folium.Marker(
        [lat2, lon2],
        popup=name2,
        tooltip=name2,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    folium.PolyLine(
        locations=[[lat1, lon1], [lat2, lon2]],
        weight=4
    ).add_to(m)

    m.fit_bounds([[lat1, lon1], [lat2, lon2]])
    return m


def calculate_result(place1, place2):
    lat1, lon1, address1 = get_coordinates(place1)
    lat2, lon2, address2 = get_coordinates(place2)

    if lat1 is None or lat2 is None:
        return {
            "success": False,
            "message": "找不到其中一個或兩個地點，請嘗試輸入其他名稱。"
        }

    distance = great_circle_distance(lat1, lon1, lat2, lon2)

    return {
        "success": True,
        "place1": place1,
        "place2": place2,
        "lat1": lat1,
        "lon1": lon1,
        "lat2": lat2,
        "lon2": lon2,
        "address1": address1,
        "address2": address2,
        "distance": distance
    }


def show_result(result):
    if not result["success"]:
        st.error(result["message"])
        return

    st.success("距離計算完成！")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("地點一")
        st.write(f"**輸入地點:** {result['place1']}")
        st.write(f"**查詢結果：** {result['address1']}")
        st.write(f"**緯度：** {result['lat1']}")
        st.write(f"**經度：** {result['lon1']}")

    with col2:
        st.subheader("地點二")
        st.write(f"**輸入地點:** {result['place2']}")
        st.write(f"**查詢結果：** {result['address2']}")
        st.write(f"**緯度：** {result['lat2']}")
        st.write(f"**經度：** {result['lon2']}")

    st.subheader("大圓距離")
    st.metric(label="距離（公里）", value=f"{result['distance']:.2f}")

    st.subheader("地圖")
    fmap = create_map(
        result["lat1"], result["lon1"], result["place1"],
        result["lat2"], result["lon2"], result["place2"]
    )
    st_folium(fmap, width=1100, height=500)

    st.subheader("使用公式")
    st.code(
        "distance = r * acos(sin(x1)*sin(x2) + cos(x1)*cos(x2)*cos(y1-y2))",
        language="python"
    )

    st.write("Where:")
    st.write("- r = 6371 km (Earth radius)")
    st.write("- x1, x2 are latitudes in radians")
    st.write("- y1, y2 are longitudes in radians")

# Title
st.title("🌍 地球大圓距離計算")
st.write("這個城市可以計算地球上兩點間的大圓距離.")
st.write("本程式使用 geopy 取得經緯度，並利用大圓距離公式計算兩地距離。")

st.divider()

#Teacher example
st.subheader("老師指定範例")

if st.button("執行範例：帝國大廈 → 台北101"):
    st.session_state.mode = "teacher"
    st.session_state.result = calculate_result("Empire State Building", "Taipei 101")

st.divider()

# Custom input
st.subheader("自訂地點輸入")

place1 = st.text_input("請輸入第一個地點", value="Empire State Building")
place2 = st.text_input("請輸入第二個地點", value="Taipei 101")

if st.button("計算自訂距離"):
    st.session_state.mode = "custom"
    st.session_state.result = calculate_result(place1, place2)

st.divider()

# ---------------------------
# Show result persistently
# ---------------------------
if st.session_state.result is not None:
    show_result(st.session_state.result)

st.divider()
