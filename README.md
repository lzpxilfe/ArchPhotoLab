# ArchPhotoLab v0.1.0

ArchPhotoLab is a desktop tool for archaeology-focused photo processing. It aligns one drone photo and one plan image with manually picked control points, previews the result as an overlay, applies a record-friendly flatten correction, and exports PNG outputs from a single workflow.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-Desktop%20GUI-41B883?logo=qt)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10+-brightgreen?logo=opencv)
![License](https://img.shields.io/badge/License-GPL--2.0-lightgrey)

This project is released under `GNU GPL v2.0` and is intended to be openly shared for public-interest archaeological recording and preservation work.

## 🚀 Standalone Executable 빌드 방법 (Windows)

ArchPhotoLab을 단일 실행 파일(`.exe`)로 패키징하여 Python 설치가 없는 환경에서도 편리하게 배포 및 실행할 수 있도록 하는 방법입니다.

### 1. PyInstaller 설치
터미널(PowerShell 또는 CMD)에서 다음 명령어로 PyInstaller를 설치합니다:
```bash
pip install pyinstaller
```

### 2. 단일 실행 파일 (.exe) 빌드
프로젝트 루트 폴더에서 아래 명령어를 실행하여 단일 실행 파일로 빌드합니다:

**Windows PowerShell:**
```powershell
pyinstaller --noconsole --onefile --icon=icon.png --add-data "icon.png;." --name=ArchPhotoLab main.py
```

**Windows CMD:**
```cmd
pyinstaller --noconsole --onefile --icon=icon.png --add-data "icon.png;." --name=ArchPhotoLab main.py
```

- `--noconsole` (또는 `-w`): 프로그램 실행 시 백그라운드 콘솔(CMD) 창이 뜨지 않도록 합니다.
- `--onefile` (또는 `-F`): 종속 라이브러리와 이미지 파일을 하나의 `.exe` 파일로 병합합니다.
- `--add-data "icon.png;."`: 애플리케이션의 아이콘 파일(`icon.png`)을 빌드된 실행 파일의 리소스 디렉토리에 포함시킵니다.

### 3. 빌드 결과 확인
빌드가 완료되면 프로젝트 루트에 `dist/` 폴더가 생성되며, 그 안에 `ArchPhotoLab.exe` 파일이 생성됩니다. 이 파일만 복사해서 바로 실행할 수 있습니다.

---

## What It Does

- Load one photo and one plan image in `PNG`, `JPG`, or `JPEG`.
- Add, move, delete, reorder, undo, and redo paired control points.
- Estimate alignment in photo coordinates and preview the warped plan as an overlay.
- Show alignment quality metrics including average, median, maximum error, grade, and outlier count.
- Apply illumination flattening presets for record-oriented readability.
- Save and reopen project state as JSON.
- Export three PNG outputs:
  - overlay result
  - flattened photo
  - warped plan

## Workflow

1. Click `사진 불러오기`.
2. Click `도면 불러오기`.
3. Add matching points on both images.
4. Run `자동 정합`.
5. Review `정합 overlay` and adjust `도면 투명도`.
6. Apply `플랫 보정 적용` if needed.
7. Save project JSON or export PNG outputs.

## Current Feature Set

### Image Loading

- Separate photo and plan slots.
- Current filename and resolution shown in the UI.
- Unsupported formats are rejected with a user-facing error.

### Point Editing

- Click to add points.
- Drag to move points.
- Double-click or use the delete action to remove points.
- Point numbering is shown directly on both panels.
- Point history supports undo and redo.
- Point mismatch warnings appear when counts differ.

### Alignment

- Homography alignment is supported.
- The current codebase also includes `affine` and `similarity` transform modes internally.
- Alignment fails clearly when point count is too low or geometry is degenerate.
- Warped plan preview is shown in the result panel.

### Quality Feedback

- Reprojection errors are computed per point.
- Average, median, and maximum errors are displayed.
- Outlier points are highlighted.
- A simple quality grade is derived from error distribution.

### Flatten Correction

- Illumination flattening uses large-scale background estimation plus local contrast enhancement.
- Preset and intensity values are stored in the project file.
- Before/after compare and split compare modes are supported by the current UI state model.

### Project Save and Restore

- Project files use JSON.
- Saved state includes file paths, points, transform data, overlay opacity, quality state, flatten settings, and some UI state.
- Older project payloads are migrated forward when possible.

### PNG Export

- `overlay_result_YYYYMMDD_HHMMSS.png`
- `flat_photo_YYYYMMDD_HHMMSS.png`
- `warped_plan_YYYYMMDD_HHMMSS.png`

## Installation

### Requirements

- Python `3.10` or newer
- Desktop environment for Qt GUI
- macOS, Windows, or Linux

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

### Windows cmd

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Project Layout

```txt
ArchPhotoLab/
├── main.py
├── requirements.txt
├── LICENSE
├── README.md
├── icon.png
├── archphotolab/
│   ├── constants.py
│   ├── state.py
│   ├── core/
│   │   ├── export.py
│   │   ├── geometry.py
│   │   ├── imagery.py
│   │   └── project_io.py
│   └── ui/
│       ├── main_window.py
│       ├── panels.py
│       ├── point_editor.py
│       ├── status_panel.py
│       └── workflow_controller.py
├── docs/
│   └── qa_checklist.md
└── samples/
    ├── README.md
    └── project_templates/
```

## Documentation

- QA checklist: [docs/qa_checklist.md](docs/qa_checklist.md)
- Sample templates: [samples/README.md](samples/README.md)

## Known Limits

- The primary workflow is still one photo plus one plan.
- Supported raster inputs are limited to `PNG`, `JPG`, and `JPEG`.
- `PDF` and `SVG` are not supported in this version.
- Automatic keypoint detection is not included.

## Troubleshooting

### The image does not load

- Check that the extension is `PNG`, `JPG`, or `JPEG`.
- Check that the file still exists at the saved path.

### Alignment fails

- Use at least four points on both sides.
- Make sure the point order matches between photo and plan.
- Avoid nearly collinear point layouts.

### Quality looks poor

- Review highlighted outlier points.
- Move or delete bad points and run alignment again.
- Flatten correction improves readability, not transform accuracy.

## License

This repository is licensed under `GNU General Public License v2.0`. See [LICENSE](LICENSE).
