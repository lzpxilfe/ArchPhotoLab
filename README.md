# ArchPhotoLab v0.1.0

ArchPhotoLab is a desktop application designed for archaeological recording and heritage photo processing. It aligns drone photography and site/plan drawings using manual control points, offering advanced blending, shadow flattening, and real-time alignment diagnostics.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-Desktop%20GUI-41B883?logo=qt)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10+-brightgreen?logo=opencv)
![License](https://img.shields.io/badge/License-GPL--2.0-lightgrey)

This project is released under the `GNU GPL v2.0` license for public-interest archaeological recording and site preservation work.

---

## ⚡ Key Features

### 1. 📐 7 Geometric Alignment Modes
Supports various camera angles and terrain conditions to achieve precise registration:
* **Similarity (유사 변환)**: Rotation, uniform scaling, and translation (2+ points).
* **Affine (선형 정합)**: Rotation, non-uniform scaling, shearing, and translation (3+ points).
* **Homography (원근 정합)**: Corrects 3D perspective distortion (4+ points).
* **Polynomial 2nd Order (2차 다항식)**: Best for lens curvature and mild terrain relief (6+ points). Recommended for oblique drone shots.
* **Polynomial 3rd Order (3차 다항식)**: Handles high-order optical distortion and complex terrain (10+ points).
* **Thin Plate Spline (TPS)**: Local warp based on radial basis function for maximum local fit (5+ points).
* **RBF Multiquadric (MQ)**: Smooth local warping with natural extrapolation at the boundaries (4+ points).

### 2. 🎨 Advanced Blending & Image Processing
* **Multiply Blending (곱하기 합성)**: Removes the white background of the drawing automatically, overlaying only the clean black contours and lines onto the drone terrain.
* **Normal Opacity**: Real-time slider to control transparency from 0% to 100%.
* **Color Keying (크로마키 배경 제거)**: Instantly keys out a target color from the drawing background with adjustable tolerance.
* **Illumination Flattening (조명 평탄화)**: Removes shadows and uneven lighting from drone footage. Features three presets (`Record (기록용)`, `Shadow removal (그림자 제거)`, `Soft (부드럽게)`) and intensity control.
* **Split View Compare**: Interactive split-screen view to swipe and compare before/after results side-by-side.

### 3. 📋 Real-Time Diagnostics & UX
* **Asynchronous Computation**: Point registration runs in a background thread to prevent UI freezing. The interface locks during calculations and displays an active spinner (`계산 중...`).
* **Diagnostic Log Panel**: An expandable, clear text log that shows computation duration, average/median/max reprojection errors, quality grade, and suggestions for removing outliers.
* **Synchronized Point List**: Adding, moving, deleting, or reordering points instantly updates both the photo and the map view in sync, preventing point order mismatches.

### 4. 📁 Project Management & Export
* **JSON State Saving**: Saves image paths, point lists, transforms, blending mode, opacity, and UI parameters into a single portable `.json` file.
* **High-Res Export**: Generates original-resolution PNG outputs for overlays, flattened photos, and warped drawings.

---

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
pyinstaller --clean ArchPhotoLab.spec
```

빌드가 완료되면 프로젝트 루트에 `dist/` 폴더가 생성되며, 그 안에 `ArchPhotoLab.exe` 파일이 생성됩니다. 이 파일만 복사해서 바로 실행할 수 있습니다.

---

## 💻 Installation & Quick Start

### Requirements
* Python `3.10` or newer
* Qt GUI desktop environment (macOS, Windows, or Linux)

### Run from Source

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows PowerShell:**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

---

## 📂 Project Layout

```txt
ArchPhotoLab/
├── main.py
├── ArchPhotoLab.spec
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

## License

This repository is licensed under `GNU General Public License v2.0`. See [LICENSE](LICENSE).

## Citation

이 저장소가 연구, 수업, 현장 업무에 도움이 되었다면 GitHub의 **Cite this repository** 버튼으로 인용해 주세요.

[![Cite this repository](https://img.shields.io/badge/Cite_this-repository-2ea44f?logo=github)](https://github.com/lzpxilfe/ArchPhotoLab)
[![Star this repository](https://img.shields.io/github/stars/lzpxilfe/ArchPhotoLab?style=social)](https://github.com/lzpxilfe/ArchPhotoLab)

인용 메타데이터는 [CITATION.cff](CITATION.cff)에 보관합니다.

