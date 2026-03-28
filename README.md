# 🏛️ ArchPhotoLab v0.1.0

ArchPhotoLab은 고고학 현장의 **드론 사진 + 도면** 정합을 빠르게 처리하는 데스크톱 도구입니다.

- 🖼️ 사진과 도면을 각각 불러온 뒤
- 🧩 대응점을 찍어 정합
- 👀 overlay를 비교 확인
- ☀️ 플랫 보정으로 판독성 향상
- 💾 프로젝트 저장/복원
- 📤 PNG 3종 내보내기

를 한 번의 워크플로로 처리할 수 있습니다.

> 📣 **오픈소스 안내**: 현재 버전은 **GNU General Public License 2.0(GPL-2.0)** 기반입니다.
>
> 🌐 공공 연구/기록 보존 목적의 활용을 염두에 둔 공개형 도구로 사용 가능합니다.

---

## ✅ 실행 체크리스트

- [ ] Python 3.10+ 가상환경 준비
- [ ] `python3 -m venv .venv` 또는 `python -m venv .venv`
- [ ] 가상환경 활성화 완료
- [ ] `pip install -r requirements.txt` 실행
- [ ] `python main.py`로 화면이 뜨는지 확인
- [ ] `사진 불러오기`로 드론 사진 1장 선택
- [ ] `도면 불러오기`로 도면 1장 선택
- [ ] 양측 이미지에 대응점 최소 4개씩 찍기
- [ ] `자동 정합` 실행
- [ ] `정합 overlay` 모드에서 위치 확인 및 투명도 조절
- [ ] `플랫 보정 적용` → `원본/평탄화 보기` 확인
- [ ] `PNG 내보내기`로 결과 3종 저장
- [ ] `결과 저장`/`프로젝트 불러오기`로 상태 복원 확인

## 📦 주요 기능

### 1) 기본 워크플로 UI
- 좌측: 드론 사진 판독 패널
- 중앙: 도면 판독 패널
- 우측: 결과 표시 패널
- 상단: 작업 버튼 모음
- 하단: 현재 단계/로드 파일/점 개수/오류/품질 상태 패널

### 2) 이미지 로딩
- 드론 사진 로딩: `사진 불러오기`
- 도면 로딩: `도면 불러오기`
- 지원 형식: **PNG / JPG / JPEG**
- 각 패널에 현재 파일명과 해상도 표시

### 3) 대응점 관리
- 양쪽 이미지 클릭으로 대응점 추가
- 대응점 번호 라벨 표시
- 점 드래그로 위치 수정
- 점 더블클릭 또는 선택 후 `점 다시 맞추기`로 삭제
- 좌우 점 개수 불일치 시 경고

### 4) 정합(Homography)
- 대응점 4개 이상에서 `자동 정합` 실행
- 도면을 사진 좌표로 projective transform(warp)하여 overlay 생성
- 점 개수 부족/배열 실패 시 오류 메시지 표시

### 5) 결과 확인
- 보기 모드: `사진만`, `도면만`, `정합 overlay`
- `도면 투명도` 슬라이더로 실시간 overlay 조절

### 6) 정합 품질 표시
- 대응점 기준 **재투영 오차(reprojection error)** 표시
- 평균/최대 오차 표시
- 오차 임계치 초과 점은 상태 및 포인트 시각 경고로 표시

### 7) 플랫 보정
- 단순 1차 조도 정리 방식(배경 조명 추정 + CLAHE)
- `플랫 보정 적용`으로 보정 결과 생성
- `원본/평탄화 보기`로 비교

### 8) 프로젝트 저장/복원
- JSON 기반 프로젝트 파일 저장
- 저장 항목:
  - 사진 경로
  - 도면 경로
  - 사진 대응점 목록
  - 도면 대응점 목록
  - overlay 투명도
  - 정합 행렬/상태
- `프로젝트 불러오기`로 동일 작업 상태 복구

### 9) PNG Export
- 다음 3종 파일 기본명으로 저장
  - `overlay_result_YYYYMMDD_HHMMSS.png`
  - `flat_photo_YYYYMMDD_HHMMSS.png`
  - `warped_plan_YYYYMMDD_HHMMSS.png`
- 사용자 지정 폴더 선택 가능

### 10) 앱 시작 정보
- `icon.png`를 앱 아이콘으로 사용
- 실행 시 스플래시 화면에서 프로젝트 공개/라이선스 안내

---

## 🧰 요구 환경

- Python: **3.10+** 권장
- OS: Windows / macOS / Linux 데스크톱
- 화면 기반 GUI 환경

---

## 🧪 설치 및 실행 (상세)

### 공통 공통 준비
```bash
cd /Users/your-path/ArchPhotoLab  # 경로는 본인 환경에 맞게 변경
```

---

## 🍎 macOS / Linux

### 1) 가상환경 생성
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) 패키지 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) 실행
```bash
python main.py
```

---

## 🪟 Windows (PowerShell)

### 1) 가상환경 생성
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

### 2) 패키지 설치
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) 실행
```powershell
python main.py
```

---

## 🪟 Windows (cmd)

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

---

## 📂 프로젝트 핵심 파일 구조

- `main.py` : 앱 시작, 스플래시, 윈도우/아이콘 설정
- `requirements.txt` : 의존성 목록
- `icon.png` : 실행 아이콘 및 시작 스플래시에 사용
- `archphotolab/state.py` : 앱 상태 모델
- `archphotolab/core/geometry.py` : 정합/오차 계산
- `archphotolab/core/imagery.py` : 이미지 입출력 및 보정 로직
- `archphotolab/core/project_io.py` : JSON 프로젝트 저장/복원
- `archphotolab/core/export.py` : PNG 내보내기
- `archphotolab/ui/main_window.py` : 전체 UI 및 워크플로 바인딩

---

## ⚠️ 제한/알려진 사항

- 현재는 PNG/JPG만 지원 (PDF/SVG 미지원)
- 정합은 **homography** 기반만 포함
- 자동 대응점 추출은 미구현
- 한 번에 1장의 사진, 1장의 도면 기준

---

## 🧭 추천 작업 순서(기본 플로우)

1. `사진 불러오기` 📷
2. `도면 불러오기` 🗺️
3. 양쪽에 대응점 4개 이상 찍기 🎯
4. `자동 정합` 실행 ✅
5. `정합 overlay` 확인 후 투명도 조절 🎚️
6. `플랫 보정 적용` + `원본/평탄화 보기` 비교 ☀️
7. `PNG 내보내기` 또는 `결과 저장` 💾

---

## 📄 라이선스

- GNU General Public License 2.0 (GPL-2.0)
- 공개 소프트웨어 원칙에 따라 공개된 고고학 기록 작업 도구입니다.
