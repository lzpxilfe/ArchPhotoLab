from __future__ import annotations

from typing import Final

APP_NAME: Final[str] = "ArchPhotoLab"
APP_VERSION: Final[str] = "0.1.0"
APP_ICON_FILE: Final[str] = "icon.png"
DEFAULT_TIMESTAMP_FORMAT: Final[str] = "%Y%m%d_%H%M%S"
PYTHON_LOG_FORMAT: Final[str] = "%(asctime)s [%(levelname)s] %(message)s"
PROJECT_MIN_COMPATIBLE_VERSION: Final[str] = "0.1.0"

# Alignment modes
ALIGNMENT_MODE_HOMOGRAPHY: Final[str] = "homography"
ALIGNMENT_MODE_AFFINE: Final[str] = "affine"
ALIGNMENT_MODE_SIMILARITY: Final[str] = "similarity"
TRANSFORM_MODE_OPTIONS: Final[tuple[str, ...]] = (
    ALIGNMENT_MODE_HOMOGRAPHY,
    ALIGNMENT_MODE_AFFINE,
    ALIGNMENT_MODE_SIMILARITY,
)
ALIGNMENT_MODE_LABELS: Final[dict[str, str]] = {
    ALIGNMENT_MODE_HOMOGRAPHY: "프로젝트 정합",
    ALIGNMENT_MODE_AFFINE: "선형 정합",
    ALIGNMENT_MODE_SIMILARITY: "유사 변환 정합",
}
DEFAULT_ALIGNMENT_MODE: Final[str] = ALIGNMENT_MODE_HOMOGRAPHY

# Layout
DEFAULT_WINDOW_SIZE: Final[tuple[int, int]] = (1660, 1020)
MIN_PANEL_SIZE: Final[tuple[int, int]] = (260, 260)
ROOT_LAYOUT_MARGIN: Final[int] = 10
ROOT_LAYOUT_SPACING: Final[int] = 8
WORKFLOW_SECTION_SPACING: Final[int] = 8
WORKFLOW_ROW_SPACING: Final[int] = 8
WORKFLOW_ROW3_SPACING: Final[int] = 10
PANELS_STRETCH: Final[int] = 9

# UI / typography
UI_FONT_FAMILY: Final[str] = (
    '"Pretendard", "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif'
)
UI_FONT_SIZE: Final[float] = 10.5
UI_TITLE_FONT_SIZE: Final[int] = 11
UI_TITLE_OFFSET_Y: Final[int] = 9

# File handling
SUPPORTED_IMAGE_EXTENSIONS: Final[set[str]] = {".png", ".jpg", ".jpeg"}
IMAGE_FILE_FILTER: Final[str] = "PNG/JPG 이미지 (*.png *.jpg *.jpeg)"
PROJECT_FILE_FILTER: Final[str] = "ArchPhotoLab 프로젝트 (*.json)"
SUPPORTED_PROJECT_EXTENSION: Final[str] = ".json"
JSON_CHARSET_ENCODING: Final[str] = "utf-8"

# Alignment / geometry
MIN_ALIGNMENT_POINTS: Final[int] = 4
HOMOGRAPHY_METHOD: Final[int] = 0
OVERLAY_ALPHA_DEFAULT: Final[float] = 0.45
OVERLAY_ALPHA_MIN: Final[int] = 0
OVERLAY_ALPHA_MAX: Final[int] = 100
ALPHA_PERCENT_SCALE: Final[int] = 100
ERROR_WARNING_THRESHOLD_PX: Final[float] = 12.0
ERROR_WARNING_PERCENTILE: Final[float] = 95.0
ERROR_GRADE_GOOD: Final[float] = 3.0
ERROR_GRADE_WARNING: Final[float] = 8.0
QUALITY_GRADE_GOOD: Final[str] = "좋음"
QUALITY_GRADE_NORMAL: Final[str] = "보통"
QUALITY_GRADE_POOR: Final[str] = "불안정"
QUALITY_GRADE_UNKNOWN: Final[str] = "판단 불가"
WORKFLOW_STAGE_UNKNOWN: Final[str] = "단계 미지정"
WORKFLOW_STAGE_LOAD: Final[str] = "1) 사진/도면 로드"
WORKFLOW_STAGE_POINTS: Final[str] = "2) 대응점 등록"
WORKFLOW_STAGE_ALIGNMENT: Final[str] = "3) 정합 계산"
WORKFLOW_STAGE_EXPORT: Final[str] = "4) 내보내기"

# View mode keys
VIEW_MODE_PHOTO: Final[str] = "photo"
VIEW_MODE_PLAN: Final[str] = "plan"
VIEW_MODE_OVERLAY: Final[str] = "overlay"

# UI strings
WINDOW_TITLE: Final[str] = APP_NAME
SPLASH_TITLE: Final[str] = APP_NAME
SPLASH_MESSAGE_LINES: Final[tuple[str, str, str]] = (
    "GNU General Public License 2.0 기반",
    "공공에게 공개된 오픈 소스 도구입니다.",
    "사진-도면 정합·점 기반 작업 워크플로를 시작합니다.",
)

INTRO_TITLE: Final[str] = "첫 사용 가이드"
GUIDE_HIDE_TEXT: Final[str] = "안내 숨기기"
GUIDE_SHOW_TEXT: Final[str] = "안내 보기"

INFO_NO_FILE: Final[str] = "없음"
TEMP_FILE_NAME: Final[str] = "임시"
IMAGE_PANEL_EMPTY_TEXT: Final[str] = "이미지 없음"

VIEW_BUTTON_OPEN_PHOTO: Final[str] = "사진 불러오기"
VIEW_BUTTON_OPEN_PLAN: Final[str] = "도면 불러오기"
VIEW_BUTTON_LOAD_PROJECT: Final[str] = "프로젝트 불러오기"
VIEW_BUTTON_SAVE_PROJECT: Final[str] = "결과 저장"
VIEW_BUTTON_START_POINTS: Final[str] = "대응점 찍기 시작"
VIEW_BUTTON_ALIGN: Final[str] = "자동 정합"
VIEW_BUTTON_FLATTEN: Final[str] = "플랫 보정 적용"
VIEW_BUTTON_REMOVE_POINT: Final[str] = "점 다시 맞추기"
VIEW_BUTTON_ALIGN_WITH_SELECTED_EXCLUDED: Final[str] = "선택점 제외 후 정합"
VIEW_BUTTON_UNDO: Final[str] = "되돌리기"
VIEW_BUTTON_REDO: Final[str] = "다시 실행"
VIEW_BUTTON_REORDER_UP: Final[str] = "선택점 앞으로"
VIEW_BUTTON_REORDER_DOWN: Final[str] = "선택점 뒤로"
VIEW_BUTTON_EXPORT: Final[str] = "PNG 내보내기"
VIEW_TOGGLE_COMPARE_FLAT: Final[str] = "원본/평탄화 보기"
VIEW_TOGGLE_COMPARE_SPLIT: Final[str] = "분할 비교 모드"
WORKFLOW_MODE_PLAN_SPLIT: Final[str] = "도면 분할 보기"

WORKFLOW_MODE_PHOTO: Final[str] = "사진만"
WORKFLOW_MODE_PLAN: Final[str] = "도면만"
WORKFLOW_MODE_OVERLAY: Final[str] = "정합 overlay"
LABEL_FLATTEN_PRESET: Final[str] = "평탄화 방식"
LABEL_FLATTEN_INTENSITY: Final[str] = "평탄화 정도"
LABEL_FLATTEN_SPLIT: Final[str] = "원본/평탄화 비교"
VIEW_LABEL_PHOTO: Final[str] = "사진"
VIEW_LABEL_PLAN: Final[str] = "도면"

STATUS_STEP_PREFIX: Final[str] = "현재 단계: "
STATUS_GUIDE_PREFIX: Final[str] = "워크플로: "
STATUS_FILES_PREFIX: Final[str] = "사진: "
STATUS_FILES_SEPARATOR: Final[str] = " / 도면: "
STATUS_POINTS_PREFIX: Final[str] = "대응점: 사진 "
STATUS_POINTS_SEPARATOR: Final[str] = "개 / 도면 "
STATUS_POINTS_SUFFIX: Final[str] = "개"
STATUS_QUALITY_PREFIX: Final[str] = "정합 품질: "
STATUS_QUALITY_NOT_CALCULATED: Final[str] = "정합 품질: 계산 전"
STATUS_QUALITY_BAD_POINTS: Final[str] = "오차 큰 포인트: "
STATUS_QUALITY_RECOMMENDATION: Final[str] = "추천 조치: "
STATUS_MISMATCH_WARNING: Final[str] = "경고: 대응점 개수 불일치"
STATUS_STEP_POINTS: Final[str] = "대응점 찍기"
STATUS_STEP_ALIGNMENT: Final[str] = "자동 정합"
STATUS_STEP_ALIGNMENT_DONE: Final[str] = f"{WORKFLOW_MODE_OVERLAY} 확인"

WORKFLOW_INTRO_TEXT: Final[str] = (
    "실행 순서: "
    "1) 드론 사진 불러오기 → 2) 도면 불러오기 → "
    f"3) 양쪽에 대응점 찍기(양쪽 각 {MIN_ALIGNMENT_POINTS}개 이상) → 4) 자동 정합 → "
    "5) 정합 overlay 확인 및 투명도 조절 → 6) 플랫 보정 적용 비교 → "
    "7) PNG 저장(overlay / 평탄화 / 정합 도면)"
)

WORKFLOW_STEP_1_LOAD_PHOTO: Final[str] = "1) 사진을 불러오고, 2) 도면을 불러오세요."
WORKFLOW_STEP_1_LOAD_PLAN: Final[str] = "1) 도면을 불러온 뒤, 2) 사진·도면에 대응점을 찍으세요."
WORKFLOW_STEP_POINTS: Final[str] = "양쪽 이미지에 대응점을 각각 최소 {min_points}개씩 찍어야 정합을 계산할 수 있습니다."
WORKFLOW_STEP_ALIGNMENT_MISMATCH_WARN: Final[str] = (
    "경고: 대응점 개수가 달라 자동 정합 버튼이 비활성입니다. 양쪽 개수를 맞춰주세요."
)
WORKFLOW_STEP_ALIGNMENT_READY: Final[str] = "정합 준비 완료. 정합 버튼을 눌러 overlay 미리보기를 확인하세요."
WORKFLOW_STEP_ALIGNMENT_DONE: Final[str] = (
    "정합 완료. 도면 투명도를 조절하고, 필요하면 점을 수정해 다시 정합한 뒤 PNG 내보내기를 진행하세요."
)
WORKFLOW_STEP_FLATTEN_READY: Final[str] = "플랫 보정 단계: 방식/강도 조정과 분할 비교로 판독성이 좋아진지 확인하세요."
WORKFLOW_STEP_EXPORT_READY: Final[str] = "PNG 내보내기에서 overlay / 평탄화 / 정합 도면을 각각 저장하세요."

# Common UI object names and labels
QOBJECT_INTRO_CARD: Final[str] = "IntroCard"
QOBJECT_STATUS_PANEL: Final[str] = "StatusPanel"
QOBJECT_WORK_PANEL: Final[str] = "WorkPanel"

LABEL_PHOTO_PANEL: Final[str] = "드론 사진"
LABEL_PLAN_PANEL: Final[str] = "도면"
LABEL_RESULT_PANEL: Final[str] = "결과 표시"

LABEL_VIEW_MODE: Final[str] = "보기 모드"
LABEL_OVERLAY_ALPHA: Final[str] = "도면 투명도"

LABEL_RESULT_VIEW_PREFIX: Final[str] = "결과 표시: "
LABEL_RESULT_VIEW_NO_PHOTO: Final[str] = "(사진 없음)"
LABEL_STATUS_PANEL: Final[str] = "상태"
LABEL_RESULT_VIEW_NO_ALIGNMENT: Final[str] = "(정합 미실행)"

RESULT_LAST_SAVED_PREFIX: Final[str] = "마지막 저장: "
RESULT_LAST_SAVED_NONE: Final[str] = "마지막 저장: 없음"

# Dialog / menu titles
DIALOG_TITLE_ERROR: Final[str] = "오류"
DIALOG_TITLE_INFO: Final[str] = "저장"
DIALOG_TITLE_SAVE_OK: Final[str] = "저장 완료"

MSG_POINT_MODE_ON: Final[str] = "점 편집 모드: 사용"
MSG_POINT_MODE_OFF: Final[str] = "점 편집 모드: 잠금"
MSG_REQUIRES_PHOTO_FOR_FLAT_COMPARE: Final[str] = "원본/평탄화 보기를 하려면 먼저 사진을 불러와야 합니다."
MSG_FLATTEN_CALC_FAIL_FMT: Final[str] = "평탄화 계산 실패: {error}"
MSG_FILE_LOADED_FMT: Final[str] = "{label} 로드: {name}"
MSG_POINT_ADDED_FMT: Final[str] = "{side} 대응점 {count}개 추가"
MSG_SELECTED_PHOTO_POINT_DELETED: Final[str] = "선택한 사진 대응점을 삭제했습니다."
MSG_SELECTED_PLAN_POINT_DELETED: Final[str] = "선택한 도면 대응점을 삭제했습니다."
MSG_SELECT_POINT_TO_DELETE: Final[str] = "삭제할 점을 선택하세요."
MSG_ALIGNMENT_REQUIRE_IMAGES: Final[str] = "정합은 사진과 도면을 모두 불러온 뒤에 가능합니다."
MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT: Final[str] = "대응점을 {min_points}개 이상 찍어주세요."
MSG_HOMOGRAPHY_BAD_POINT_SHAPE: Final[str] = "점 좌표 형식이 잘못되었습니다."
MSG_HOMOGRAPHY_DEGENERATE: Final[str] = "정합을 계산할 수 없습니다. 점이 거의 일직선이거나 특이한 배치인지 확인하세요."
MSG_HOMOGRAPHY_BAD_RESULT: Final[str] = "정합 결과 형식이 비정상입니다."
MSG_ALIGNMENT_REQUIRE_POINTS_FMT: Final[str] = (
    "자동 정합은 양쪽 모두에서 {min_points}개 이상의 대응점이 필요합니다."
)
MSG_ALIGNMENT_POINT_MISMATCH_WARN: Final[str] = "경고: 대응점 개수가 다릅니다. 앞쪽의 공통 개수만 사용해 정렬합니다."
MSG_ALIGNMENT_COMPLETE_FMT: Final[str] = "자동 정합 완료: 평균 {avg:.2f}px, 최대 {max:.2f}px"
MSG_ALIGNMENT_COMPLETE_WITH_MODE_FMT: Final[str] = (
    "정합 완료({mode}): 평균 {avg:.2f}px, 중앙값 {median:.2f}px, 최대 {max:.2f}px"
)
MSG_ALIGNMENT_MODE_CHANGED: Final[str] = "정합 모드가 바뀌어 이전 정합 결과가 초기화됩니다."
MSG_ALIGNMENT_MODE_UNSUPPORTED: Final[str] = "지원하지 않는 정합 모드입니다."
MSG_ALIGNMENT_ERROR_FMT: Final[str] = "정합 실패: {error}"
MSG_ALIGNMENT_POSTPROC_ERROR_FMT: Final[str] = "정합 후 결과 계산 실패: {error}"
MSG_ALIGNMENT_TOOLTIP_FMT: Final[str] = (
    "양쪽 이미지에서 대응점을 동일 개수로 {min_points}개 이상 찍어야 자동 정합이 가능합니다."
)
MSG_ALIGNMENT_READY_TO_ALIGN_FMT: Final[str] = "현재 점으로 정합을 계산합니다."
MSG_ALIGNMENT_CONSTRAINT_FAILED: Final[str] = "정합 조건이 충족되지 않았습니다."
MSG_ALIGNMENT_RESULT_INVALID: Final[str] = "정합 계산 결과가 비정상입니다."
MSG_ALIGNMENT_NO_OVERLAP: Final[str] = "오차가 커 정합 신뢰도가 낮습니다. 점을 조정해 다시 계산해보세요."

MSG_FLATTEN_REQUIRED: Final[str] = "평탄화할 사진이 없습니다."
MSG_FLATTEN_APPLIED: Final[str] = "플랫 보정 적용됨"
MSG_FLATTEN_ERROR_FMT: Final[str] = "평탄화 실패: {error}"
MSG_FLATTEN_PRESET_APPLIED_FMT: Final[str] = "평탄화 방식 적용: {preset} ({intensity:.0f}%)"
MSG_FLATTEN_PRESET_INVALID: Final[str] = "지원되지 않는 평탄화 방식입니다."
MSG_FLATTEN_INTENSITY_RANGE_FMT: Final[str] = "평탄화 강도: {value}%"
MSG_OVERLAY_BASE_MISSING: Final[str] = "기준 사진이 없습니다."
MSG_OVERLAY_PLAN_MISSING: Final[str] = "정합 결과가 없습니다."
MSG_OVERLAY_IMAGE_SIZE_MISMATCH: Final[str] = "overlay 이미지 크기가 다릅니다."
MSG_OVERLAY_IMAGE_MISSING: Final[str] = "overlay를 만들기 위한 이미지가 없습니다."
MSG_IMAGE_UNSUPPORTED_EXTENSION: Final[str] = "PNG/JPG 파일만 지원됩니다."
MSG_IMAGE_LOAD_FAIL_FMT: Final[str] = "이미지를 불러올 수 없습니다: {path}"
MSG_IMAGE_NOT_FOUND: Final[str] = "이미지를 불러올 수 없습니다."

MSG_EXPORT_REQUIRE_PHOTO: Final[str] = "출력할 사진이 없어 내보내기할 수 없습니다."
MSG_EXPORT_SAVED_FLAT_FMT: Final[str] = "flat: {filename}"
MSG_EXPORT_SAVED_WARPED_FMT: Final[str] = "warped plan: {filename}"
MSG_EXPORT_SAVED_OVERLAY_FMT: Final[str] = "overlay: {filename}"
MSG_EXPORT_MISSING_OVERLAY: Final[str] = "정합 overlay"
MSG_EXPORT_MISSING_PLAN: Final[str] = "도면 정합 결과"
MSG_EXPORT_MISSING_PREFIX: Final[str] = "누락: "
MSG_EXPORT_SUCCESS_FMT: Final[str] = "PNG 내보내기 완료: {path}"
MSG_EXPORT_ERROR_FMT: Final[str] = "PNG 내보내기 실패: {error}"
MSG_EXPORT_RESULT_MESSAGE: Final[str] = "저장된 파일:\\n{message}\\n\\n폴더: {path}"
MSG_EXPORT_NO_IMAGE: Final[str] = "저장할 이미지가 없습니다."
MSG_EXPORT_IMAGE_NOT_RGB: Final[str] = "RGB 이미지만 저장 가능합니다."

MSG_PHOTO_FILE_LOADED_FMT: Final[str] = "사진 로드: {name}"
MSG_PLAN_FILE_LOADED_FMT: Final[str] = "도면 로드: {name}"
MSG_PHOTO_LOAD_FAIL_FMT: Final[str] = "사진 로드 실패: {error}"
MSG_PLAN_LOAD_FAIL_FMT: Final[str] = "도면 로드 실패: {error}"
MSG_LOAD_PHOTO_ERROR_FMT: Final[str] = "사진을 열지 못했습니다.\\n{error}"
MSG_LOAD_PLAN_ERROR_FMT: Final[str] = "도면을 열지 못했습니다.\\n{error}"
MSG_LOAD_PROJECT_ERROR_FMT: Final[str] = "프로젝트를 열지 못했습니다.\\n{error}"
MSG_PROJECT_SAVED_FMT: Final[str] = "프로젝트 저장 완료: {path}"
MSG_PROJECT_SAVED_DIALOG_FMT: Final[str] = "프로젝트를 저장했습니다.\\n{path}"
MSG_PROJECT_LOADED_FMT: Final[str] = "프로젝트를 불러왔습니다: {name}"
MSG_PROJECT_MISSING_PATH_FMT: Final[str] = "경고: {paths} 경로를 찾지 못했습니다."
MSG_PROJECT_VERSION_UPGRADE_FMT: Final[str] = "프로젝트 포맷 업그레이드: {from_version} → {to_version}"
MSG_PROJECT_VERSION_MISMATCH: Final[str] = "호환되지 않는 프로젝트 버전입니다. 최근 버전 기준으로 복원 시도 후 누락값을 보강합니다."
MSG_LOAD_MISSING_PHOTO: Final[str] = "드론 사진"
MSG_LOAD_MISSING_PLAN: Final[str] = "도면"
MSG_PROJECT_LOAD_FAIL_FMT: Final[str] = "프로젝트 불러오기 실패: {error}"
MSG_PROJECT_FORMAT_INVALID: Final[str] = "프로젝트 파일 형식이 올바르지 않습니다."
MSG_RESULT_VIEW_FMT: Final[str] = "결과 표시: {mode}"
MSG_RESULT_VIEW_NO_PHOTO_FMT: Final[str] = "결과 표시: {mode} (사진 없음)"
MSG_RESULT_VIEW_NO_ALIGNMENT_FMT: Final[str] = "결과 표시: {mode} (정합 미실행)"
MSG_FATAL_LOG_PREFIX: Final[str] = "Fatal error during startup"

MSG_PNG_SAVE_FAIL_FMT: Final[str] = "PNG 저장 실패: {error}"
MSG_IMAGE_RGB_ONLY: Final[str] = "이미지는 RGB 형식이어야 합니다."

MSG_QUALITY_SUMMARY_FMT: Final[str] = (
    "평균 오차 {avg:.2f}px / 중앙값 {median:.2f}px / 최대 오차 {max:.2f}px (오차 큰 점: {warn_count}개)"
)
MSG_QUALITY_GRADE_FMT: Final[str] = "품질: {grade} (이상치 {bad_count}개)"
MSG_QUALITY_OUTLIER_HINT_FMT: Final[str] = "문제 포인트: {count}개"
MSG_QUALITY_RECOMMEND_OUTLIER: Final[str] = "오차가 큰 점을 제외하고 정합을 다시 실행해보세요."
MSG_QUALITY_NO_ALIGNMENT: Final[str] = "정합 미실행: 품질 계산 대기"
WORKFLOW_POINT_EXCLUDE_HELP: Final[str] = "선택 점을 임시 제외 후 정합을 재실행해 오차 개선 효과를 확인하세요."
MSG_POINT_ORDER_CHANGED: Final[str] = "선택점 순서를 변경했습니다."
MSG_POINT_HISTORY_EMPTY: Final[str] = "더 이상 되돌릴 작업이 없다."
MSG_POINT_HISTORY_REDO_EMPTY: Final[str] = "더 이상 되살릴 작업이 없다."
MSG_POINT_UNDO_DONE: Final[str] = "점 작업을 되돌렸습니다."
MSG_POINT_REDO_DONE: Final[str] = "취소했던 점 작업을 되살렸습니다."

ERROR_MESSAGE_PREFIX: Final[str] = "⚠️ "

FILE_SELECT_PHOTO_TITLE: Final[str] = "드론 사진 불러오기"
FILE_SELECT_PLAN_TITLE: Final[str] = "도면 불러오기"
FILE_SELECT_PROJECT_SAVE_TITLE: Final[str] = "프로젝트 저장"
FILE_SELECT_PROJECT_LOAD_TITLE: Final[str] = "프로젝트 불러오기"
FILE_SELECT_EXPORT_FOLDER_TITLE: Final[str] = "내보낼 폴더 선택"
FILE_COMPARE_SPLIT_TITLE: Final[str] = "이미지 비교"

# Export
PNG_NAME_TEMPLATES: Final[dict[str, str]] = {
    "overlay": "overlay_result_{timestamp}.png",
    "flat": "flat_photo_{timestamp}.png",
    "warped": "warped_plan_{timestamp}.png",
}
PNG_FORMAT: Final[str] = "PNG"

# Flatten presets
FLATTEN_PRESET_RECORD: Final[str] = "기록용"
FLATTEN_PRESET_SHADOW: Final[str] = "강한음영완화"
FLATTEN_PRESET_SOFT: Final[str] = "부드러운정리"
FLATTEN_PRESET_KEYS: Final[tuple[str, ...]] = (
    FLATTEN_PRESET_RECORD,
    FLATTEN_PRESET_SHADOW,
    FLATTEN_PRESET_SOFT,
)
FLATTEN_PRESET_DEFAULT: Final[str] = FLATTEN_PRESET_RECORD
FLATTEN_PRESET_INTENSITY_MIN: Final[int] = 0
FLATTEN_PRESET_INTENSITY_MAX: Final[int] = 100
FLATTEN_PRESET_INTENSITY_DEFAULT: Final[int] = 85
FLATTEN_PRESETS: Final[dict[str, dict[str, float]]] = {
    FLATTEN_PRESET_RECORD: {"kernel_scale": 0.10, "clahe_clip": 2.0, "gamma": 1.0},
    FLATTEN_PRESET_SHADOW: {"kernel_scale": 0.18, "clahe_clip": 2.8, "gamma": 0.95},
    FLATTEN_PRESET_SOFT: {"kernel_scale": 0.08, "clahe_clip": 1.4, "gamma": 1.05},
}

SPLIT_VIEW_DEFAULT_RATIO: Final[float] = 0.5
SPLIT_VIEW_MIN_RATIO: Final[float] = 0.05
SPLIT_VIEW_MAX_RATIO: Final[float] = 0.95

# Color theme
PALETTE: Final[dict[str, str]] = {
    "primary": "#151d2b",
    "secondary": "#23304a",
    "accent": "#6a8cff",
    "text": "#e6edf7",
    "muted": "#96a9c1",
    "panel": "#2b3d58",
    "danger": "#ff8f8f",
}

IMAGE_PANEL_BACKGROUND_RGB: Final[tuple[int, int, int]] = (43, 61, 88)
IMAGE_PANEL_BORDER_RGB: Final[tuple[int, int, int]] = (107, 140, 177)
IMAGE_PANEL_TITLE_BAR_RGB: Final[tuple[int, int, int]] = (31, 43, 64)
IMAGE_PANEL_TEXT_RGB: Final[tuple[int, int, int]] = (224, 233, 248)
IMAGE_PANEL_HINT_TEXT: Final[str] = "이미지를 불러와 주세요"
IMAGE_PANEL_HINT_TEXT_RGB: Final[tuple[int, int, int]] = (180, 188, 205)

POINT_WARNING_RGB: Final[tuple[int, int, int]] = (255, 99, 99)
POINT_SELECTED_RGB: Final[tuple[int, int, int]] = (255, 196, 0)
POINT_NORMAL_RGB: Final[tuple[int, int, int]] = (106, 140, 255)
POINT_ERROR_LOW_RGB: Final[tuple[int, int, int]] = (76, 170, 255)
POINT_ERROR_MID_RGB: Final[tuple[int, int, int]] = (255, 196, 0)
POINT_ERROR_HIGH_RGB: Final[tuple[int, int, int]] = (255, 56, 56)
POINT_OUTLINE_RGB: Final[tuple[int, int, int]] = (20, 20, 24)
POINT_LABEL_TEXT_RGB: Final[tuple[int, int, int]] = (24, 24, 24)

PANEL_TOP_BANNER_HEIGHT: Final[int] = 28
IMAGE_PANEL_TITLE_X: Final[int] = 8
IMAGE_PANEL_TITLE_Y_OFFSET: Final[int] = 9
IMAGE_PANEL_HINT_X: Final[int] = 16
PANEL_RENDER_PADDING_BOTTOM: Final[int] = 40
POINT_HOVER_RADIUS_MIN: Final[float] = 8.0
POINT_HOVER_RADIUS_SCALE: Final[float] = 10.0
POINT_HOVER_RADIUS_MAX: Final[float] = 12.0
POINT_HOVER_RADIUS_FALLBACK_SCALE: Final[float] = 1e-6
POINT_MARK_SIZE: Final[int] = 9
POINT_LABEL_OFFSET_X: Final[int] = 2
POINT_LABEL_OFFSET_Y: Final[int] = 4
POINT_LABEL_FONT_SIZE: Final[int] = UI_TITLE_FONT_SIZE - 2

CONTROL_MIN_HEIGHT: Final[int] = 34
CONTROL_MIN_WIDTH: Final[int] = 130
SLIDER_MIN_WIDTH: Final[int] = 160
COMBO_MIN_WIDTH: Final[int] = 140
COMBO_MIN_HEIGHT: Final[int] = 24

# Widget style literals
GROUPBOX_MARGIN_TOP: Final[int] = 10
GROUPBOX_PADDING_TOP: Final[int] = 8
GROUPBOX_PADDING_RIGHT: Final[int] = 10
GROUPBOX_PADDING_BOTTOM: Final[int] = 10
GROUPBOX_PADDING_LEFT: Final[int] = 10
GROUPBOX_TITLE_LEFT: Final[int] = 12
GROUPBOX_TITLE_PADDING_X: Final[int] = 6
GROUPBOX_BORDER_ALPHA_SUFFIX: Final[str] = "44"
GROUPBOX_TITLE_BORDER_ALPHA_SUFFIX: Final[str] = "66"
GROUPBOX_BORDER_RADIUS: Final[int] = 12
BUTTON_FONT_WEIGHT: Final[int] = 700
BUTTON_BORDER_RADIUS: Final[int] = 9
BUTTON_PADDING_X: Final[int] = 12
BUTTON_PADDING_Y: Final[int] = 7
COMBO_BORDER_WIDTH: Final[int] = 1
COMBO_PADDING_X: Final[int] = 10
COMBO_PADDING_Y: Final[int] = 4
COMBO_BORDER_RADIUS: Final[int] = 8
CHECKBOX_SPACING: Final[int] = 6
SLIDER_GROOVE_HEIGHT: Final[int] = 8
SLIDER_GROOVE_RADIUS: Final[int] = 4
SLIDER_HANDLE_SIZE: Final[int] = 18
SLIDER_HANDLE_MARGIN_Y: Final[int] = -6
PANEL_HEADER_PADDING: Final[str] = "4px 2px"
PANEL_INFO_PADDING: Final[str] = "2px 4px"
IMAGE_PANEL_HEADER_PADDING: Final[str] = PANEL_HEADER_PADDING
IMAGE_PANEL_INFO_PADDING: Final[str] = PANEL_INFO_PADDING
PANEL_IMAGE_STYLE_COLOR_TRANSPARENT: Final[str] = "transparent"

# Splash
SPLASH_WIDTH: Final[int] = 520
SPLASH_HEIGHT: Final[int] = 260
SPLASH_BG_COLOR: Final[tuple[int, int, int]] = (24, 28, 38)
SPLASH_TEXT_COLOR: Final[tuple[int, int, int]] = (228, 236, 255)
SPLASH_TITLE_FONT_SIZE: Final[int] = 15
SPLASH_BODY_FONT_SIZE: Final[int] = 10
SPLASH_ICON_MAX_SIZE: Final[int] = 150
SPLASH_ICON_TOP_MARGIN: Final[int] = 16
SPLASH_DURATION_MS: Final[int] = 1400
SPLASH_TEXT_Y_WITH_ICON_OFFSET: Final[int] = 30
SPLASH_TEXT_Y_NO_ICON: Final[int] = 30
SPLASH_TEXT_Y_ICON_FAILED: Final[int] = 26
SPLASH_TITLE_BAR_HEIGHT: Final[int] = 34
SPLASH_TEXT_LEFT: Final[int] = 20
SPLASH_TEXT_TOP_OFFSET: Final[int] = 38
SPLASH_TEXT_WIDTH_MARGIN: Final[int] = 40
SPLASH_TEXT_HEIGHT: Final[int] = 70

# Image processing
IMAGE_EXT_MIN: Final[float] = 0.0
IMAGE_EXT_MAX: Final[float] = 255.0
RGB_CHANNELS_EXPECTED: Final[int] = 3
KERNEL_MIN_SIZE: Final[int] = 11
BACKGROUND_ESTIMATION_SCALE: Final[float] = 0.10
BACKGROUND_EPSILON: Final[float] = 1e-6
CLAHE_CLIP_LIMIT: Final[float] = 2.0
CLAHE_TILE: Final[tuple[int, int]] = (8, 8)


class ProjectKeys:
    FORMAT_VERSION: Final[str] = "format_version"
    PHOTO_PATH: Final[str] = "photo_path"
    PLAN_PATH: Final[str] = "plan_path"
    PHOTO_POINTS: Final[str] = "photo_points"
    PLAN_POINTS: Final[str] = "plan_points"
    OVERLAY_ALPHA: Final[str] = "overlay_alpha"
    HOMOGRAPHY: Final[str] = "homography"
    SHOW_FLAT_PHOTO: Final[str] = "show_flat_photo"
    RESULT_VIEW_MODE: Final[str] = "result_view_mode"
    REPROJECTION_AVG: Final[str] = "reprojection_avg"
    REPROJECTION_MEDIAN: Final[str] = "reprojection_median"
    REPROJECTION_MAX: Final[str] = "reprojection_max"
    REPROJECTION_ERRORS: Final[str] = "reprojection_errors"
    FLATTEN_ENABLED: Final[str] = "flatten_enabled"
    ALIGNMENT_MODE: Final[str] = "alignment_mode"
    QUALITY_PROFILE: Final[str] = "quality_profile"
    QUALITY_GRADE: Final[str] = "quality_grade"
    FLATTEN_PRESET: Final[str] = "flatten_preset"
    FLATTEN_INTENSITY: Final[str] = "flatten_intensity"
    SHOW_SPLIT_VIEW: Final[str] = "show_split_view"
    SPLIT_VIEW_RATIO: Final[str] = "split_view_ratio"
    WORKFLOW_STAGE: Final[str] = "workflow_stage"
    POINT_EDITOR_STATE: Final[str] = "point_editor_state"
    PHOTO_VIEW_ZOOM: Final[str] = "photo_view_zoom"
    PHOTO_VIEW_PAN_X: Final[str] = "photo_view_pan_x"
    PHOTO_VIEW_PAN_Y: Final[str] = "photo_view_pan_y"
    PLAN_VIEW_ZOOM: Final[str] = "plan_view_zoom"
    PLAN_VIEW_PAN_X: Final[str] = "plan_view_pan_x"
    PLAN_VIEW_PAN_Y: Final[str] = "plan_view_pan_y"
