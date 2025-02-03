import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm

# 연도 입력 (예: 1973)
yyyy = input("Enter the year (yyyy): ")

# 기본 URL
# yyyy 부분을 필요한 년도(yyyy)로 수정하며 사용
base_url = f'https://www.laoziliao.net/rmrb/{yyyy}-{{}}-{{}}-{{}}'

# 최종 결과를 저장할 리스트
all_dfs = []

# month 변수는 날짜를 나타냄.
# 1~12 범위에서 반복 시행, 날짜가 더 이상 존재 하지 않으면 동작을 마침
# tqdm은 진행상황 표시하는 라이브러리
# 퍼센티지와 남은 시간, 동작 종료 후 총 소요시간 확인 가능
# 보통 1시간 40분에서 2시간 정도 소요
for month in tqdm(range(1, 13), desc="Processing"):

    # day 변수는 날짜를 나타냄.
    # 1~31 범위에서 반복 시행, 날짜가 더 이상 존재 하지 않으면 동작을 마침
    for day in range(1, 32):

        # p 변수는 지면을 나타냄.
        # 초기 인민일보는 2면 정도에 그쳤으나 # 이후 지면이 늘어나 1950년대에는 4~8면을 들쭉날쭉 함.
        # 아래 코드는 지면이 최대 12면 이내일 것으로 가정하고,
        # 12면 이내에서 동작을 반복 시행, 지면이 더 이상 존재하지 않으면 동작을 마침
        # 나중에 인민일보 지면은 최대 20면에 이르는데, 필요한 경우 range(1, x)의 x값을 늘려주면 됨.
        for p in range(1, 20):

            # mm 부분을 두 자리수(01, 02, ..., 12)로 동적 생성
            mm = f"{month:02d}"

            # dd 부분을 두 자리수(01, 02, ..., 31)로 동적 생성
            dd = f"{day:02d}"

            # URL 동적 생성
            url = base_url.format(mm, dd, p)

            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                x = 1
                h2_values = []
                div_values = []

                while True:
                    h2_selector = f'div div:nth-of-type(1) div:nth-of-type({x}) h2'
                    div_selector = f'div div:nth-of-type(1) div:nth-of-type({x}) div'

                    h2_element = soup.select_one(h2_selector)
                    div_element = soup.select_one(div_selector)

                    if h2_element is None:
                        break

                    h2_values.append(h2_element.text.strip())
                    div_values.append(div_element.text.strip())

                    x += 1

                    # 주파수 유지하기 위한 일시정지
                    time.sleep(0.2)
    # 코드의 반복 시행이 지나치게 빠르면 내용을 불러오지 못하고 누락되는 페이지가 발생하거나
    # 웹페이지에서 ip를 차단하는 문제가 발생. 이를 방지하기 위해 기사와 기사 사이에
    # 0.2초의 시간 간격을 두고 동작 시행

                df = pd.DataFrame({'yyyy': yyyy, 'mm': mm, 'dd': dd, 'p': p, 'title': h2_values, 'contents': div_values, 'url': url})

                # 결과를 리스트에 추가
                all_dfs.append(df)

            else:
                print(f"Error for {url}: {response.status_code}")

# 모든 결과를 하나의 데이터프레임으로 결합
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df.sort_values(by=['mm', 'dd', 'p'], ascending=[True, True, True])

# 최종 결과 출력
print(final_df)

# 엑셀, csv 파일로 저장
# yyyy 부분을 필요한 년도(yyyy)로 수정하며 사용
# 엑셀 형식의 경우 한 셀이 포함할 수 있는 글자 수가 최대 32767자로, 이것을 초과하는 분량은 누락됨
final_df.to_excel(f'rmrb{yyyy}.xlsx', index=False)
final_df.to_csv(f'rmrb{yyyy}.csv', index=False)

# 구글 Colab에서 시행할 경우, 파일 저장 후 로컬 기기로 다운로드
# "여러 파일 다운로드 ~" 팝업 뜨지 않도록 10초의 시간차를 두고 다운로드 시행
from google.colab import files
files.download(f'rmrb{yyyy}.csv')
time.sleep(10)
files.download(f'rmrb{yyyy}.xlsx')
