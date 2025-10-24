
import requests
import streamlit as st
import os

CITY_MAP = {
    '서울': 'Seoul,KR',
    '인천': 'Incheon,KR',
    '대전': 'Daejeon,KR',
    '대구': 'Daegu,KR',
    '광주': 'Gwangju,KR',
    '부산': 'Busan,KR',
    '울산': 'Ulsan,KR',
    '세종': 'Sejong,KR',
    '수원': 'Suwon-si,KR',
    '고양': 'Goyang-si,KR',
    '성남': 'Seongnam-si,KR',
    '부천': 'Bucheon-si,KR',
    '의정부': 'Uijeongbu-si,KR',
    '남양주': 'Namyangju-si,KR',
    '안산': 'Ansan-si,KR',
    '기장군': 'Gijang-gun,KR',
    # 부산 주요 시군구
    '수영구': 'Suyeong-gu,KR',
    '동구': 'Dong-gu,KR',
    # 서울 주요 시군구
    '종로구': 'Jongno-gu,KR',
    '영등포구': 'Yeongdeungpo-gu,KR',
    '강남구': 'Gangnam-gu,KR',
    '송파구': 'Songpa-gu,KR',
    '마포구': 'Mapo-gu,KR',
    '서초구': 'Seocho-gu,KR',
    '중구': 'Jung-gu,KR',
    '동대문구': 'Dongdaemun-gu,KR',
    '성동구': 'Seongdong-gu,KR',
    '성북구': 'Seongbuk-gu,KR',
    '은평구': 'Eunpyeong-gu,KR',
    '강서구': 'Gangseo-gu,KR',
    '노원구': 'Nowon-gu,KR',
    '관악구': 'Gwanak-gu,KR',
    '동작구': 'Dongjak-gu,KR',
    '서대문구': 'Seodaemun-gu,KR',
    '강동구': 'Gangdong-gu,KR',
    '중랑구': 'Jungnang-gu,KR',
    '광진구': 'Gwangjin-gu,KR',
    '양천구': 'Yangcheon-gu,KR',
    '도봉구': 'Dobong-gu,KR',
    '강북구': 'Gangbuk-gu,KR',
    '구로구': 'Guro-gu,KR',
    '금천구': 'Geumcheon-gu,KR',
    '용산구': 'Yongsan-gu,KR'
    ,'동래구': 'Dongnae-gu,KR'
    ,'남구': 'Nam-gu,KR'
    ,'북구': 'Buk-gu,KR'
    ,'강서구': 'Gangseo-gu,KR'
    ,'사하구': 'Saha-gu,KR'
    ,'금정구': 'Geumjeong-gu,KR'
    ,'연제구': 'Yeonje-gu,KR'
    ,'수영구': 'Suyeong-gu,KR'
    ,'사상구': 'Sasang-gu,KR'
    ,'기장군': 'Gijang-gun,KR'
}


    # (중복 및 잘못된 들여쓰기 구역 삭제)
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'

def get_forecast(city_kr):
    import datetime
    city_en = CITY_MAP.get(city_kr)
    if not city_en:
        return None, f"지원하지 않는 도시입니다: {city_kr}"
    params = {
        'q': city_en,
        'appid': API_KEY,
        'lang': 'kr',
        'units': 'metric'
    }
    try:
        response = requests.get(FORECAST_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            # Group forecast by date (one per day, noon)
            daily = {}
            for entry in data['list']:
                dt = datetime.datetime.fromtimestamp(entry['dt'])
                date_str = dt.strftime('%Y-%m-%d')
                hour = dt.hour
                # Pick the forecast closest to 12:00 (noon) for each day
                if date_str not in daily or abs(hour - 12) < abs(daily[date_str]['hour'] - 12):
                    daily[date_str] = {
                        'date': date_str,
                        'weather': entry['weather'][0]['description'],
                        'temp': entry['main']['temp'],
                        'icon': entry['weather'][0]['icon'],
                        'hour': hour
                    }
            # Remove 'hour' from result
            result = [{k: v for k, v in day.items() if k != 'hour'} for day in daily.values()]
            return result, None
        else:
            return None, f"5일 예보 정보를 가져올 수 없습니다: {city_kr}"
    except Exception as e:
        return None, f"API 요청 중 오류 발생: {e}"

def get_weather(city_kr):
    city_en = CITY_MAP.get(city_kr)
    if not city_en:
        return None, f"지원하지 않는 도시입니다: {city_kr}"
    params = {
        'q': city_en,
        'appid': API_KEY,
        'lang': 'kr',
        'units': 'metric'
    }
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            icon = data['weather'][0]['icon']
            return {
                'city_kr': city_kr,
                'city_en': city_en,
                'weather': weather,
                'temp': temp,
                'icon': icon
            }, None
        else:
            return None, f"날씨 정보를 가져올 수 없습니다: {city_kr}"
    except Exception as e:
        return None, f"API 요청 중 오류 발생: {e}"

def main():
    st.set_page_config(page_title='한국 날씨', layout='centered')
    st.title("한국 도시별 날씨 및 5일 예보")
    # 광역시별 시군구/동 분류
    # 각 광역시별 시군구만 분류
    def get_districts(metro):
        if metro == '서울':
            return [c for c in CITY_MAP if c.endswith('구') and c != '수영구' and c != '동구']
        elif metro == '부산':
            busan_districts = [
                '중구', '서구', '동구', '영도구', '부산진구', '동래구', '남구', '북구', '해운대구', '사하구', '금정구', '강서구', '연제구', '수영구', '사상구', '기장군'
            ]
            return [c for c in CITY_MAP if c in busan_districts]
        elif metro == '인천':
            incheon_districts = [
                '중구', '동구', '미추홀구', '연수구', '남동구', '부평구', '계양구', '서구', '강화군', '옹진군'
            ]
            return [c for c in CITY_MAP if c in incheon_districts]
        elif metro == '대전':
            return [c for c in CITY_MAP if c.endswith('구') and 'Daejeon' in CITY_MAP[c] or c == '대전']
        elif metro == '대구':
            return [c for c in CITY_MAP if c.endswith('구') and 'Daegu' in CITY_MAP[c] or c == '대구']
        elif metro == '광주':
            return [c for c in CITY_MAP if c.endswith('구') and 'Gwangju' in CITY_MAP[c] or c == '광주']
        elif metro == '울산':
            return [c for c in CITY_MAP if c.endswith('구') and 'Ulsan' in CITY_MAP[c] or c == '울산']
        elif metro == '경기도':
            return [c for c in CITY_MAP if c not in ['서울', '인천', '대전', '대구', '광주', '부산', '울산', '세종', '강원도', '경기도']]
        else:
            return [metro]
    metros = ['서울', '부산', '인천', '대전', '대구', '광주', '울산', '경기도']
    metro_choice = st.selectbox(
        "선택_광역시/도(행정구역)",
        options=metros,
        index=0
    )
    district_options = get_districts(metro_choice)
    district_list = st.multiselect(
        f"선택_{metro_choice}_시군구 (복수 선택 가능)",
        options=district_options,
        default=[]
    )
    if not district_list:
        st.info("시군구를 선택하면 날씨와 5일 예보가 표시됩니다.")
        return
    # 선택된 시군구/동에 대해 날씨/예보 표시
    for city_kr in district_list:
        if city_kr not in CITY_MAP:
            st.warning(f"도시명 '{city_kr}'은 지원하지 않습니다. CITY_MAP에 추가해 주세요.")
            continue
        with st.spinner(f'{city_kr} 날씨 정보를 불러오는 중입니다...'):
            weather, error = get_weather(city_kr)
            forecast, f_error = get_forecast(city_kr)
        st.markdown(f'---')
        st.subheader(f'[{city_kr}] 오늘의 날씨')
        if weather:
            st.success(f"{weather['city_kr']}({weather['city_en']})의 현재 날씨: {weather['weather']}, 온도: {weather['temp']}°C")
            icon_url = f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
            st.image(icon_url, width=100)
            if forecast:
                st.subheader(f'[{city_kr}] 5일치 주간 날씨')
                # 한 줄에 모든 날씨 정보와 아이콘을 깔끔하게 표시
                cols = st.columns(len(forecast))
                import datetime
                weekday_names = ['월', '화', '수', '목', '금', '토', '일']
                for idx, day in enumerate(forecast):
                    with cols[idx]:
                        st.image(f"http://openweathermap.org/img/wn/{day['icon']}@2x.png", width=48)
                        date_obj = datetime.datetime.strptime(day['date'], "%Y-%m-%d")
                        # Python의 weekday()는 월=0, 일=6이므로, 한국식 요일로 변환
                        weekday = weekday_names[date_obj.weekday()]
                        st.write(f"{day['date']} ({weekday}요일)\n{day['weather']}\n{day['temp']}°C")
            else:
                st.error(f_error)
        else:
            st.error(error or f'{city_kr}의 날씨 정보를 불러올 수 없습니다.')

if __name__ == '__main__':
    main()

