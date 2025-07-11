# F학점 지뢰찾기 (F-Grade Minesweeper)

## 1. 프로젝트 개요

### 1.1. 개발 목적
표준 지뢰찾기 게임의 규칙을 기반으로, 대학교 생활과 성적(F학점)이라는 재미있는 테마를 적용하여 재해석한 파이썬 GUI 게임입니다. `tkinter`와 `Pillow` 라이브러리를 활용하여 동적으로 그래픽을 생성하고, `pygame`을 통해 사운드 제어, `json`을 이용한 데이터 관리 등 다양한 파이썬 라이브러리 활용 능력을 종합적으로 보여주는 것을 목표로 개발되었습니다.

### 1.2. 사용 기술
- **언어:** Python 3
- **GUI:** `tkinter`
- **그래픽 생성:** `Pillow (PIL)`
- **사운드:** `pygame`
- **데이터 저장:** `json`
- **화면 녹화:** `pyautogui`, `imageio`

## 2. 상세 기능 설명

![스크린샷 2025-06-09 041408](https://github.com/user-attachments/assets/41595c47-82e6-460c-9b58-7fb649210429)



### 2.1. 기본 게임 기능
- **지뢰찾기 핵심 로직:** F학점(지뢰)을 피해서 모든 안전한 칸을 여는 기본적인 게임 방식을 따릅니다.
- **동적 그래픽:** `Pillow`를 사용하여 게임 타일, 숫자, 아이콘 등 모든 그래픽 요소를 코드를 통해 직접 그려서 사용합니다.
- **타이머 및 F학점 카운터:** 게임 시작과 동시에 시간이 기록되며, 남은 F학점 개수가 실시간으로 표시됩니다.

### 2.2. 편의 기능
- **난이도 조절:** '쉬움', '보통', '어려움' 세 가지 기본 난이도를 제공하며, 메뉴에서 선택하여 게임을 재시작할 수 있습니다.
- **사용자 설정 난이도:** 플레이어가 직접 게임 보드의 가로, 세로 크기와 F학점 개수를 설정하여 원하는 난이도를 만들 수 있습니다.
- **'물음표' 기능:** 클래식 지뢰찾기처럼, 마우스 우클릭을 통해 `깃발` -> `물음표` -> `기본` 상태로 타일을 순환시킬 수 있습니다.
- **첫 클릭 안전 보장:** 게임 시작 후 첫 번째 클릭으로는 절대 F학점이 나오지 않으며, 주변 8칸까지 안전한 영역으로 보장됩니다.

### 2.3. 멀티미디어 및 데이터 관리 기능
- **배경음악 및 볼륨 조절:** `pygame`을 통해 배경음악이 재생되며, UI의 슬라이더를 이용해 0%~100%까지 볼륨을 조절할 수 있습니다.
- **게임 플레이 GIF 저장:** 게임 플레이 중 매 클릭 순간이 캡처되며, 'GIF 저장' 버튼을 누르면 `fgrade_finder_play.gif` 파일로 전체 과정이 저장됩니다.
- **상세 최고 기록:** 난이도별 클리어 최고 기록이 시간(초)과 달성 날짜(`YYYY-MM-DD`) 형식으로 `highscore.json` 파일에 영구적으로 저장되고, 게임 화면에 표시됩니다.

## 3. 입출력 형태

- **입력:**
    - 마우스 좌클릭: 타일 열기
    - 마우스 우클릭: 깃발/물음표 표시
    - UI 버튼 및 메뉴 클릭: 난이도 변경, 재시작, GIF 저장, 볼륨 조절 등
    - 키보드 입력: '사용자 설정' 시 가로, 세로, F학점 개수 입력
- **출력:**
    - GUI 게임 화면
    - 게임 승리/패배/최고기록 경신 시 나타나는 메시지 박스
    - `highscore.json`: 게임 기록이 저장되는 파일
    - `fgrade_finder_play.gif`: 게임 플레이 과정이 저장되는 GIF 파일

## 4. 실행 환경 및 설치 방법

### 4.1. 실행 환경
- **Python:** 3.8 이상 권장

### 4.2. 설치 과정
1. **GitHub 저장소 다운로드 (또는 Clone)**
   ```bash
   git clone [본인의 GitHub 저장소 주소]
   cd [저장소 폴더명]
   ```

2. **필요 라이브러리 설치**
   프로젝트 폴더 내의 `requirements.txt` 파일을 이용하여 아래 명령어로 한 번에 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
   *(`requirements.txt`의 내용: pygame, Pillow, pyautogui, imageio)*

3. **필수 파일 확인**
   실행 파일(`f_grade_finder.py`)과 **같은 위치**에 배경음악 파일인 `background.mp3`가 있는지 확인합니다.
   
4. **프로그램 실행**
   터미널에서 아래 명령어를 입력하여 게임을 실행합니다.
   ```bash
   python f_grade_finder.py
   ```

## 5. 파일 구성

- **`f_grade_finder.py`**: 게임의 모든 로직이 포함된 메인 실행 코드.
- **`requirements.txt`**: 실행에 필요한 파이썬 라이브러리 목록.
- **`background.mp3`**: 배경음악 오디오 파일.
- **`highscore.json`**: (자동 생성) 최고 기록이 저장되는 데이터 파일.
- **`fgrade_finder_play.gif`**: (기능 사용 시 생성) 게임 플레이가 녹화된 GIF 이미지 파일.
