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


# ---------------------------
# 別名對照表
# 使用者輸入這些名稱時，先轉成標準名稱
# ---------------------------
ALIASES = {
    # 老師範例 / 國外
    "帝國大廈": "Empire State Building",
    "empire state building": "Empire State Building",
    "empirestatebuilding": "Empire State Building",

    # 台北101
    "台北101": "Taipei 101",
    "台北 101": "Taipei 101",
    "taipei101": "Taipei 101",
    "taipei 101": "Taipei 101",
    "台北101大樓": "Taipei 101",
    "taipei 101 tower": "Taipei 101",

    # 台北車站
    "台北車站": "台北車站",
    "台北火車站": "台北車站",
    "台北車站站": "台北車站",
    "台北火車站站": "台北車站",
    "北車": "台北車站",
    "taipei main station": "台北車站",
    "taipei station": "台北車站",
    "taipei railway station": "台北車站",

    # 板橋車站
    "板橋車站": "板橋車站",
    "板橋火車站": "板橋車站",
    "板橋站": "板橋車站",
    "banqiao station": "板橋車站",
    "banqiao railway station": "板橋車站",

    # 海洋大學
    "海洋大學": "國立台灣海洋大學",
    "台灣海洋大學": "國立台灣海洋大學",
    "國立台灣海洋大學": "國立台灣海洋大學",
    "國立臺灣海洋大學": "國立台灣海洋大學",
    "台海大": "國立台灣海洋大學",
    "海大": "國立台灣海洋大學",
    "ntou": "國立台灣海洋大學",
    "national taiwan ocean university": "國立台灣海洋大學",

    # 其他大學
    "台灣大學": "國立台灣大學",
    "臺灣大學": "國立台灣大學",
    "台大": "國立台灣大學",
    "ntu": "國立台灣大學",
    "國立台灣大學": "國立台灣大學",
    "國立臺灣大學": "國立台灣大學",

    "清華大學": "國立清華大學",
    "清大": "國立清華大學",
    "nthu": "國立清華大學",
    "國立清華大學": "國立清華大學",

    "交通大學": "國立陽明交通大學",
    "陽明交通大學": "國立陽明交通大學",
    "陽交大": "國立陽明交通大學",
    "nycu": "國立陽明交通大學",
    "國立陽明交通大學": "國立陽明交通大學",

    "成功大學": "國立成功大學",
    "成大": "國立成功大學",
    "ncku": "國立成功大學",
    "國立成功大學": "國立成功大學",

    # 車站 / 景點
    "西門町": "西門町",
    "ximending": "西門町",
    "淡水": "淡水站",
    "淡水站": "淡水站",
    "tamsui": "淡水站",
    "tamsui station": "淡水站",

    "台中車站": "台中車站",
    "台中火車站": "台中車站",
    "taichung station": "台中車站",

    "高雄車站": "高雄車站",
    "高雄火車站": "高雄車站",
    "kaohsiung station": "高雄車站",

    "基隆車站": "基隆車站",
    "基隆火車站": "基隆車站",
    "keelung station": "基隆車站",

    # 常見行政 / 地標
    "總統府": "中華民國總統府",
    "presidential office building taipei": "中華民國總統府",
    "中正紀念堂": "國立中正紀念堂",
    "chiang kai-shek memorial hall": "國立中正紀念堂",
}


# ---------------------------
# 內建固定座標
# 這些地點一定穩
# ---------------------------
KNOWN_LOCATIONS = {
    "Empire State Building": (
        40.748817,
        -73.985428,
        "Empire State Building, 20 W 34th St, New York, NY 10001, USA"
    ),
    "Taipei 101": (
        25.033968,
        121.564468,
        "Taipei 101, Xinyi District, Taipei City, Taiwan"
    ),
    "台北車站": (
        25.047924,
        121.517081,
        "台北車站，台北市中正區，臺灣"
    ),
    "板橋車站": (
        25.014231,
        121.463395,
        "板橋車站，新北市板橋區，臺灣"
    ),
    "國立台灣海洋大學": (
        25.1507663,
        121.7812151,
        "國立臺灣海洋大學，基隆市中正區，臺灣"
    ),
    "國立台灣大學": (
        25.0173405,
        121.5397518,
        "國立臺灣大學，台北市大安區，臺灣"
    ),
    "國立清華大學": (
        24.796498,
        120.996764,
        "國立清華大學，新竹市東區，臺灣"
    ),
    "國立陽明交通大學": (
        24.786748,
        120.997463,
        "國立陽明交通大學，新竹市東區，臺灣"
    ),
    "國立成功大學": (
        22.996944,
        120.220474,
        "國立成功大學，台南市東區，臺灣"
    ),
    "西門町": (
        25.042231,
        121.507416,
        "西門町，台北市萬華區，臺灣"
    ),
    "淡水站": (
        25.167817,
        121.445561,
        "淡水站，新北市淡水區，臺灣"
    ),
    "台中車站": (
        24.136675,
        120.684075,
        "台中車站，台中市中區，臺灣"
    ),
    "高雄車站": (
        22.639673,
        120.302007,
        "高雄車站，高雄市三民區，臺灣"
    ),
    "基隆車站": (
        25.134124,
        121.739526,
        "基隆車站，基隆市仁愛區，臺灣"
    ),
    "中華民國總統府": (
        25.040085,
        121.511954,
        "中華民國總統府，台北市中正區，臺灣"
    ),
    "國立中正紀念堂": (
        25.034535,
        121.521680,
        "國立中正紀念堂，台北市中正區，臺灣"
    ),
}


# ---------------------------
# 文字標準化
# ---------------------------
def normalize_place_name(place_name):
    if place_name is None:
        return ""

    name = place_name.strip()
    lower_name = name.lower().strip()

    if name in ALIASES:
        return ALIASES[name]

    if lower_name in ALIASES:
        return ALIASES[lower_name]

    return name


# ---------------------------
# 地點查詢快取
# ---------------------------
@st.cache_data(show_spinner=False)
def cached_geocode(query):
    geolocator = Nominatim(
        user_agent="katrina-distance-app/1.0 (student homework contact via github)",
        timeout=10
    )
    return geolocator.geocode(
        query,
        language="zh-TW",
        exactly_one=True
    )


# ---------------------------
# Functions
# ---------------------------
def get_coordinates(place_name):
    normalized_name = normalize_place_name(place_name)

    # 1. 先查內建固定座標
    if normalized_name in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[normalized_name]

    # 2. 再試 geopy
    try:
        candidates = [
            normalized_name,
            normalized_name + ", Taiwan",
            normalized_name + ", 台灣",
        ]

        simplified_1 = normalized_name.replace("號", "").strip()
        simplified_2 = simplified_1.replace("樓", "").strip()
        simplified_3 = simplified_2.replace("巷", "").replace("弄", "").strip()

        extra_candidates = [
            simplified_1,
            simplified_1 + ", Taiwan",
            simplified_1 + ", 台灣",
            simplified_2,
            simplified_2 + ", Taiwan",
            simplified_2 + ", 台灣",
            simplified_3,
            simplified_3 + ", Taiwan",
            simplified_3 + ", 台灣",
        ]

        if "區" in normalized_name:
            part = normalized_name.split("區")[0] + "區"
            extra_candidates.extend([
                part,
                part + ", Taiwan",
                part + ", 台灣"
            ])

        if "街" in normalized_name:
            part = normalized_name.split("街")[0] + "街"
            extra_candidates.extend([
                part,
                part + ", Taiwan",
                part + ", 台灣"
            ])

        if "路" in normalized_name:
            part = normalized_name.split("路")[0] + "路"
            extra_candidates.extend([
                part,
                part + ", Taiwan",
                part + ", 台灣"
            ])

        candidates.extend(extra_candidates)

        seen = set()
        for query in candidates:
            query = query.strip()
            if not query or query in seen:
                continue
            seen.add(query)

            location = cached_geocode(query)
            if location is not None:
                return location.latitude, location.longitude, location.address

        return None, None, None

    except Exception:
        return None, None, None


def great_circle_distance(lat1, lon1, lat2, lon2):
    r = 6371  # 地球半徑（公里）

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
            "message": "找不到其中一個或兩個地點，請嘗試輸入較簡短的名稱，例如車站、學校、景點或建築物名稱。"
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
        st.write(f"**輸入地點：** {result['place1']}")
        st.write(f"**查詢結果：** {result['address1']}")
        st.write(f"**緯度：** {result['lat1']}")
        st.write(f"**經度：** {result['lon1']}")

    with col2:
        st.subheader("地點二")
        st.write(f"**輸入地點：** {result['place2']}")
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

    st.write("其中：")
    st.write("- r = 6371 公里（地球半徑）")
    st.write("- x1、x2 為緯度（弧度制）")
    st.write("- y1、y2 為經度（弧度制）")


# Title
st.title("🌍 地球大圓距離計算")
st.write("這個程式可以計算地球上兩點之間的大圓距離。")
st.write("本程式先使用內建常用地點座標與別名對照，再使用 geopy 查詢其他地點。")
st.write("若查詢不到完整地址，建議改輸入較簡短的地點名稱，例如車站、學校、景點或建築物名稱。")

st.divider()

# Teacher example
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

# Show result persistently
if st.session_state.result is not None:
    show_result(st.session_state.result)

st.divider()
