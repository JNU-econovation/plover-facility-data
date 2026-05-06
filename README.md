## 1
data 폴더에 있는 전국휴지통표준데이터.csv와 공중화장실정보.csv을 분석해줘.

목표는 쓰레기통/화장실 위치 조회 API용 DB 데이터를 만드는 거야.

먼저 구현하지 말고 아래만 정리해줘.

1. 각 CSV의 전체 컬럼명
2. API에서 실제로 쓸 만한 컬럼
3. DB 컬럼명으로 바꿀 매핑표
4. 위도/경도 컬럼명
5. null이 많거나 사용하지 않아도 될 컬럼
6. boolean으로 변환해야 할 컬럼
7. 숫자로 변환해야 할 컬럼
8. 최종 DB 테이블 설계 추천

## 2
방금 분석한 CSV 결과를 바탕으로 scripts/clean_facility_data.py를 작성해줘.

목표:
공공데이터 원본 CSV를 정제해서 DB import용 cleaned CSV를 생성한다.
이번 1차 버전에서는 지도 마커 표시와 근처 위치 조회에 필요한 최소 컬럼만 사용한다.

입력 파일:
- data/전국휴지통표준데이터.csv
- data/공중화장실정보.csv 또는 data/공중화장실정보.csv

출력 파일:
- data/cleaned/cleaned_trash_bins.csv
- data/cleaned/cleaned_toilets.csv

요구사항:
1. pandas를 사용한다.
2. 원본 CSV는 cp949 인코딩으로 읽는다.
3. 화장실 파일이 zip이면 zip 안의 csv를 자동으로 찾아 읽고, 일반 csv이면 그대로 읽는다.
4. DB import에 필요한 최소 컬럼만 선택한다.
5. DB 테이블 컬럼명에 맞게 영어 컬럼명으로 변경한다.
6. 위도/경도 컬럼은 숫자로 변환한다.
7. 위도/경도 값이 없는 행은 제거한다.
8. 위도는 -90~90, 경도는 -180~180 범위를 벗어나면 제거한다.
9. name + latitude + longitude 기준으로 중복 제거한다.
10. 정제 전 행 개수, 정제 후 행 개수, 제거된 행 개수를 출력한다.
11. 결과 CSV는 utf-8-sig 인코딩으로 저장한다.
12. 기존 프로젝트 코드는 건드리지 말고 scripts/clean_facility_data.py만 작성한다.

DB 컬럼명은 아래 기준을 따른다.

trash_bins:
name, road_address, latitude, longitude, trash_type, data_reference_date

toilets:
name, road_address, latitude, longitude, toilet_type, data_reference_date

원본 컬럼 매핑은 아래 기준을 따른다.

trash_bins:
설치장소명 -> name
소재지도로명주소 -> road_address
위도 -> latitude
경도 -> longitude
휴지통종류 -> trash_type
데이터기준일자 -> data_reference_date

toilets:
화장실명 -> name
소재지도로명주소 -> road_address
WGS84위도 -> latitude
WGS84경도 -> longitude
구분명 -> toilet_type
데이터기준일자 -> data_reference_date

주의사항:
- 소재지도로명주소가 비어 있어도 제거하지 말고 null/빈 값으로 유지한다.
- 위도/경도가 없는 행만 제거한다.
- data/cleaned 폴더가 없으면 자동 생성한다.
- 스크립트 실행 예시는 주석 또는 출력 메시지에 간단히 남긴다.