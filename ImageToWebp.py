import os
import platform
import shutil
import subprocess
import sys
import traceback
import json

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon, QPixmap, QLinearGradient, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QRect, QPoint

# 설정 파일 경로 (실행 파일과 같은 디렉토리에 저장)
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

# 이미지파일 경로 설정
icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')


def is_macos():
    system_info = platform.system()
    return system_info == "Darwin"


# OS에 따라 폴더 열기 명령 실행
def open_folder(folder_path):
    if folder_path:
        try:
            # 경로가 존재하는지 확인
            if not os.path.exists(folder_path):
                # 상대 경로인 경우 처리 (예: "원본 폴더/변환된 이미지")
                if folder_path.startswith("원본 폴더"):
                    # 기본 다운로드 폴더로 대체
                    folder_path = os.path.expanduser("~/Downloads")
                else:
                    return

            # OS에 따라 폴더 열기 명령 다르게 실행
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", folder_path])
            else:  # Linux 등
                subprocess.call(["xdg-open", folder_path])
        except Exception as e:
            print(f"폴더 열기 오류: {str(e)}")


# exe 파일에서 실행될 경우의 상대경로로 설정
if (is_macos()):
    print('이 운영체제는 맥입니다.')
    cwebp_path = os.path.join(os.path.dirname(__file__), 'cwebp')
else:
    print('이 운영체제는 윈도우입니다.')
    cwebp_path = os.path.join(os.path.dirname(__file__), 'cwebp.exe')

# 색상 상수 - 제공된 디자인 팔레트 기반
ROYAL_BLUE = "#4136C3"  # 액센트 컬러 - 01
DEEP_INDIGO = "#3E31B3"  # 보조 컬러 - 01
CORNFLOWER_BLUE = "#74A3FF"  # 보조 컬러 - 03
LAVENDER_MIST = "#E8D7F8"  # 보조 컬러 - 02

# 무채색 배경색 추가
DARK_GRAY = "#222222"  # 진한 배경색
MEDIUM_GRAY = "#333333"  # 중간 배경색
LIGHT_GRAY = "#F0F0F0"  # 밝은 회색 (텍스트용)
WHITE = "#FFFFFF"  # 흰색
BLACK = "#000000"  # 검정색


# 설정 파일 로드 함수
def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 기본 설정 반환
            return {
                "quality": 75,
                "save_location_type": "subfolder",
                "save_location_path": "변환된 이미지"
            }
    except Exception as e:
        print(f"설정 로드 오류: {str(e)}")
        # 오류 발생 시 기본 설정 반환
        return {
            "quality": 75,
            "save_location_type": "subfolder",
            "save_location_path": "변환된 이미지"
        }


# 설정 파일 저장 함수
def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"설정 저장 오류: {str(e)}")
        return False


# 클릭 가능한 레이블 클래스
class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, current_quality=75, current_location_type="subfolder",
                 current_location_path="변환된 이미지"):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.resize(400, 0)

        # 부모 윈도우 위에 모달로 표시
        self.setWindowModality(Qt.ApplicationModal)

        # Set window style to match main application
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(DARK_GRAY))
        palette.setColor(QPalette.WindowText, QColor(WHITE))
        self.setPalette(palette)

        # Remove default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        titleBar = QtWidgets.QWidget()
        titleBar.setFixedHeight(36)
        titleBar.setStyleSheet(f"background-color: {ROYAL_BLUE};")

        titleBarLayout = QtWidgets.QHBoxLayout(titleBar)
        titleBarLayout.setContentsMargins(10, 0, 10, 0)
        titleBarLayout.setSpacing(10)

        # Title icon and label
        titleIcon = QtWidgets.QLabel()
        titleIcon.setFixedSize(16, 16)
        titleIcon.setText("⚙️")
        titleBarLayout.addWidget(titleIcon)

        titleLabel = QtWidgets.QLabel("설정")
        titleLabel.setStyleSheet("""
            color: #FFFFFF;
            font-family: 'Arial';
            font-size: 12px;
            font-weight: bold;
        """)
        titleBarLayout.addWidget(titleLabel)

        titleBarLayout.addStretch()

        # Close button
        closeButton = QtWidgets.QPushButton("×")
        closeButton.setFixedSize(20, 20)
        closeButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        closeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FF0000;
            }
        """)
        closeButton.clicked.connect(self.reject)
        titleBarLayout.addWidget(closeButton)

        layout.addWidget(titleBar)

        # Content area
        contentWidget = QtWidgets.QWidget()
        contentWidget.setStyleSheet(f"background-color: {DARK_GRAY};")
        contentLayout = QtWidgets.QVBoxLayout(contentWidget)
        contentLayout.setContentsMargins(20, 20, 20, 20)
        contentLayout.setSpacing(20)

        # Quality settings
        qualityGroup = QtWidgets.QGroupBox("변환 품질")
        qualityGroup.setStyleSheet(f"""
            QGroupBox {{
                color: {WHITE};
                font-family: 'Arial';
                font-weight: bold;
                border: 1px solid {CORNFLOWER_BLUE};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                padding-bottom: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        qualityLayout = QtWidgets.QVBoxLayout(qualityGroup)

        # Quality slider
        self.qualitySlider = QtWidgets.QSlider(Qt.Horizontal)
        self.qualitySlider.setMinimum(0)
        self.qualitySlider.setMaximum(100)
        self.qualitySlider.setValue(current_quality)
        self.qualitySlider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {CORNFLOWER_BLUE};
                height: 8px;
                background: {MEDIUM_GRAY};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {ROYAL_BLUE};
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {CORNFLOWER_BLUE};
                border-radius: 4px;
            }}
        """)
        qualityLayout.addWidget(self.qualitySlider)

        # Quality value label
        self.qualityLabel = QtWidgets.QLabel(f"품질: {current_quality}%")
        self.qualityLabel.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 12px;
            color: {WHITE};
            padding-top: 5px;
        """)
        self.qualityLabel.setAlignment(Qt.AlignCenter)
        qualityLayout.addWidget(self.qualityLabel)

        # Connect slider to update label
        self.qualitySlider.valueChanged.connect(self.updateQualityLabel)

        contentLayout.addWidget(qualityGroup)

        # Save location settings
        locationGroup = QtWidgets.QGroupBox("저장 위치")
        locationGroup.setStyleSheet(f"""
            QGroupBox {{
                color: {WHITE};
                font-family: 'Arial';
                font-weight: bold;
                border: 1px solid {CORNFLOWER_BLUE};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                padding-bottom: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        locationLayout = QtWidgets.QVBoxLayout(locationGroup)

        # Radio buttons for save location options
        self.originalFolderRadio = QtWidgets.QRadioButton("원본 폴더에 저장")
        self.originalFolderRadio.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.originalFolderRadio.setStyleSheet(f"""
            QRadioButton {{
                color: {WHITE};
                font-family: 'Arial';
                font-size: 12px;
                padding: 3px 0;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 7px;
                border: 2px solid {CORNFLOWER_BLUE};
            }}
            QRadioButton::indicator:checked {{
                background-color: {ROYAL_BLUE};
                border: 2px solid {CORNFLOWER_BLUE};
            }}
        """)
        locationLayout.addWidget(self.originalFolderRadio)

        self.subfoldRadio = QtWidgets.QRadioButton("원본 폴더의 하위 폴더에 저장")
        self.subfoldRadio.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.subfoldRadio.setStyleSheet(f"""
            QRadioButton {{
                color: {WHITE};
                font-family: 'Arial';
                font-size: 12px;
                padding: 3px 0;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 7px;
                border: 2px solid {CORNFLOWER_BLUE};
            }}
            QRadioButton::indicator:checked {{
                background-color: {ROYAL_BLUE};
                border: 2px solid {CORNFLOWER_BLUE};
            }}
        """)
        locationLayout.addWidget(self.subfoldRadio)

        # Subfolder name input
        subfolderLayout = QtWidgets.QHBoxLayout()
        self.subfolderLabel = QtWidgets.QLabel("하위 폴더 이름:")
        self.subfolderLabel.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 12px;
            color: {WHITE};
            margin-left: 20px;
        """)
        subfolderLayout.addWidget(self.subfolderLabel)

        self.subfolderInput = QtWidgets.QLineEdit(
            current_location_path if current_location_type == "subfolder" else "변환된 이미지")
        self.subfolderInput.setStyleSheet(f"""
            QLineEdit {{
                background-color: {MEDIUM_GRAY};
                color: {WHITE};
                border: 1px solid {CORNFLOWER_BLUE};
                border-radius: 4px;
                padding: 5px;
                font-family: 'Arial';
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ROYAL_BLUE};
            }}
        """)
        subfolderLayout.addWidget(self.subfolderInput)
        locationLayout.addLayout(subfolderLayout)

        self.customFolderRadio = QtWidgets.QRadioButton("사용자 지정 폴더에 저장")
        self.customFolderRadio.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.customFolderRadio.setStyleSheet(f"""
            QRadioButton {{
                color: {WHITE};
                font-family: 'Arial';
                font-size: 12px;
                padding: 3px 0;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 7px;
                border: 2px solid {CORNFLOWER_BLUE};
            }}
            QRadioButton::indicator:checked {{
                background-color: {ROYAL_BLUE};
                border: 2px solid {CORNFLOWER_BLUE};
            }}
        """)
        locationLayout.addWidget(self.customFolderRadio)

        # Custom folder selection
        customFolderLayout = QtWidgets.QHBoxLayout()

        self.customFolderPath = QtWidgets.QLineEdit(current_location_path if current_location_type == "custom" else "")
        self.customFolderPath.setStyleSheet(f"""
            QLineEdit {{
                background-color: {MEDIUM_GRAY};
                color: {WHITE};
                border: 1px solid {CORNFLOWER_BLUE};
                border-radius: 4px;
                padding: 5px;
                font-family: 'Arial';
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ROYAL_BLUE};
            }}
        """)
        customFolderLayout.addWidget(self.customFolderPath)

        self.browseFolderButton = QtWidgets.QPushButton("찾아보기")
        self.browseFolderButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browseFolderButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {ROYAL_BLUE};
                color: {WHITE};
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-family: 'Arial';
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {CORNFLOWER_BLUE};
            }}
        """)
        self.browseFolderButton.clicked.connect(self.browseSaveFolder)
        customFolderLayout.addWidget(self.browseFolderButton)

        locationLayout.addLayout(customFolderLayout)

        # Set default save option
        if current_location_type == "original":
            self.originalFolderRadio.setChecked(True)
        elif current_location_type == "subfolder":
            self.subfoldRadio.setChecked(True)
        elif current_location_type == "custom":
            self.customFolderRadio.setChecked(True)
        else:
            self.subfoldRadio.setChecked(True)

        contentLayout.addWidget(locationGroup)

        # Save button
        self.saveButton = QtWidgets.QPushButton("설정 저장")
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.saveButton.setMinimumHeight(36)
        self.saveButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {ROYAL_BLUE};
                color: {WHITE};
                font-family: 'Arial';
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: {CORNFLOWER_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {DEEP_INDIGO};
                color: {WHITE};
            }}
        """)
        # 저장 버튼에 명시적으로 accept() 메서드 연결
        self.saveButton.clicked.connect(self.accept)
        contentLayout.addWidget(self.saveButton)

        layout.addWidget(contentWidget)

        # Enable dragging of titlebar
        self.dragPos = None
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        titleBar.mouseReleaseEvent = self.titleBarMouseReleaseEvent

    def titleBarMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def titleBarMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def titleBarMouseReleaseEvent(self, event):
        self.dragPos = None

    def updateQualityLabel(self, value):
        self.qualityLabel.setText(f"품질: {value}%")

    def browseSaveFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "저장 폴더 선택")
        if folder:
            self.customFolderPath.setText(folder)
            self.customFolderRadio.setChecked(True)

    def getSettings(self):
        # Return the settings as a dictionary
        quality = self.qualitySlider.value()

        save_location_type = ""
        save_location_path = ""

        if self.originalFolderRadio.isChecked():
            save_location_type = "original"
        elif self.subfoldRadio.isChecked():
            save_location_type = "subfolder"
            save_location_path = self.subfolderInput.text()
        elif self.customFolderRadio.isChecked():
            save_location_type = "custom"
            save_location_path = self.customFolderPath.text()

        return {
            "quality": quality,
            "save_location_type": save_location_type,
            "save_location_path": save_location_path
        }


class DragDropFrame(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_dialog = parent
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        # 클릭 시 파일 선택 다이얼로그 호출
        self.parent_dialog.ui.select_files()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            files.append(file_path)

        if files:
            # 부모 다이얼로그의 ui 객체에 접근
            self.parent_dialog.ui.convert_files(files)


class GradientProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {MEDIUM_GRAY};
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                border-radius: 6px;
                background-color: qlineargradient(x1:0, y1:0.5, x2:1, y2:0.5, stop:0 {DEEP_INDIGO}, stop:1 {ROYAL_BLUE});
            }}
        """)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog  # 다이얼로그 객체 저장

        # 설정 불러오기
        settings = load_settings()

        # 기본 설정값 초기화 (저장된 설정이 있으면 사용)
        self.conversion_quality = settings.get("quality", 75)
        self.save_location_type = settings.get("save_location_type", "subfolder")
        self.save_location_path = settings.get("save_location_path", "변환된 이미지")

        # 저장 위치 경로 (클릭 시 열 폴더)
        self.current_save_folder = ""

        # 앱 전체 스타일 설정
        Dialog.setObjectName("Dialog")

        # 앱 배경색 설정 (Dark Gray)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(DARK_GRAY))
        palette.setColor(QPalette.WindowText, QColor(WHITE))
        Dialog.setPalette(palette)

        # 기본 제목 표시줄 제거
        Dialog.setWindowFlags(Qt.FramelessWindowHint)

        # 아이콘 설정
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setWindowTitle("이미지 변환기")

        # 메인 레이아웃
        self.mainLayout = QtWidgets.QVBoxLayout(Dialog)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # 전체 마진 제거
        self.mainLayout.setSpacing(0)

        # 제목 표시줄
        self.titleBar = QtWidgets.QWidget()
        self.titleBar.setFixedHeight(36)
        self.titleBar.setStyleSheet(f"background-color: {ROYAL_BLUE};")

        self.titleBarLayout = QtWidgets.QHBoxLayout(self.titleBar)
        self.titleBarLayout.setContentsMargins(10, 0, 10, 0)
        self.titleBarLayout.setSpacing(10)

        # 앱 아이콘
        self.titleIcon = QtWidgets.QLabel()
        self.titleIcon.setFixedSize(16, 16)
        self.titleIcon.setText("🔄")
        self.titleBarLayout.addWidget(self.titleIcon)

        # 앱 이름
        self.titleLabel = QtWidgets.QLabel("이미지 변환기")
        self.titleLabel.setStyleSheet("""
            color: #FFFFFF;
            font-family: 'Arial';
            font-size: 12px;
            font-weight: bold;
        """)
        self.titleBarLayout.addWidget(self.titleLabel)

        self.titleBarLayout.addStretch()

        # 도움말 버튼
        self.helpButton = QtWidgets.QPushButton("?")
        self.helpButton.setFixedSize(20, 20)
        self.helpButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.helpButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #E8D7F8;
            }
        """)
        self.titleBarLayout.addWidget(self.helpButton)

        # 닫기 버튼
        self.closeButton = QtWidgets.QPushButton("×")
        self.closeButton.setFixedSize(20, 20)
        self.closeButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FF0000;
            }
        """)
        self.closeButton.clicked.connect(self.on_close)
        self.titleBarLayout.addWidget(self.closeButton)

        self.mainLayout.addWidget(self.titleBar)

        # 컨텐츠 영역
        self.content = QtWidgets.QWidget()
        self.content.setStyleSheet(f"background-color: {DARK_GRAY};")

        self.contentLayout = QtWidgets.QVBoxLayout(self.content)
        self.contentLayout.setContentsMargins(20, 20, 20, 20)
        self.contentLayout.setSpacing(15)

        # 헤더 영역
        self.headerWidget = QtWidgets.QWidget()
        self.headerLayout = QtWidgets.QHBoxLayout(self.headerWidget)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(10)

        # 앱 로고
        self.logoLabel = QtWidgets.QLabel()
        self.logoLabel.setFixedSize(48, 48)
        self.logoLabel.setStyleSheet(f"""
            background-color: {ROYAL_BLUE};
            color: {WHITE};
            font-family: 'Arial';
            font-weight: bold;
            font-size: 24px;
            border-radius: 8px;
            text-align: center;
        """)
        self.logoLabel.setAlignment(Qt.AlignCenter)
        self.logoLabel.setText("W")
        self.headerLayout.addWidget(self.logoLabel)

        # 앱 제목 및 설명
        self.titleContainer = QtWidgets.QWidget()
        self.titleContainerLayout = QtWidgets.QVBoxLayout(self.titleContainer)
        self.titleContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.titleContainerLayout.setSpacing(3)

        self.appTitle = QtWidgets.QLabel("이미지 변환기")
        self.appTitle.setStyleSheet("""
            font-family: 'Arial';
            font-weight: bold;
            font-size: 22px;
            color: white;
        """)
        self.titleContainerLayout.addWidget(self.appTitle)

        self.appDesc = QtWidgets.QLabel("이미지를 WEBP 형식으로 변환하세요")
        self.appDesc.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 12px;
            color: {CORNFLOWER_BLUE};
        """)
        self.titleContainerLayout.addWidget(self.appDesc)

        self.headerLayout.addWidget(self.titleContainer)
        self.headerLayout.addStretch()

        # 설정 버튼 - 배경색 없고 호버시에만 배경색 나타나게 수정
        self.settingsButton = QtWidgets.QPushButton()
        self.settingsButton.setFixedSize(32, 32)
        self.settingsButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.settingsButton.setToolTip("설정")
        self.settingsButton.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {LAVENDER_MIST};
                border: none;
                font-size: 18px;
                border-radius: 16px;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: rgba(75, 75, 75, 0.3);
                color: {WHITE};
            }}
        """)
        self.settingsButton.setText("⚙️")

        # 설정 버튼 클릭 이벤트를 직접 정의
        self.settingsButton.clicked.connect(self.showSettingsDialog)
        self.headerLayout.addWidget(self.settingsButton)

        # 설정 레이블
        self.settingsLabel = QtWidgets.QLabel(f"변환 품질: {self.conversion_quality}%")
        self.settingsLabel.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 12px;
            color: {LAVENDER_MIST};
        """)
        self.headerLayout.addWidget(self.settingsLabel)

        self.contentLayout.addWidget(self.headerWidget)

        # 드래그 앤 드롭 영역
        self.frame = DragDropFrame(Dialog)
        self.frame.setStyleSheet(f"""
            text-align: center;
            border-radius: 12px;
            border: 2px dashed {DEEP_INDIGO};
            background-color: {MEDIUM_GRAY};
        """)

        self.frameLayout = QtWidgets.QVBoxLayout(self.frame)
        self.frameLayout.setContentsMargins(20, 54, 20, 54)  # 내부 여백 추가
        self.frameLayout.setAlignment(Qt.AlignCenter)

        # 안내 텍스트
        self.dropLabel = QtWidgets.QLabel("파일을 여기에 드래그하세요")
        self.dropLabel.setStyleSheet("""
            font-family: 'Arial';
            font-weight: bold;
            font-size: 15px;
            color: white;
            background: transparent;
            border: none;
        """)
        self.dropLabel.setAlignment(Qt.AlignCenter)
        self.frameLayout.addWidget(self.dropLabel)

        # 부가 안내
        self.orLabel = QtWidgets.QLabel("또는 이 영역을 클릭하세요")
        self.orLabel.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 13px;
            color: {CORNFLOWER_BLUE};
            background: transparent;
            border: none;
        """)
        self.orLabel.setAlignment(Qt.AlignCenter)
        self.frameLayout.addWidget(self.orLabel)

        self.contentLayout.addWidget(self.frame)

        # 하단 영역
        self.bottomWidget = QtWidgets.QWidget()
        self.bottomLayout = QtWidgets.QHBoxLayout(self.bottomWidget)
        self.bottomLayout.setContentsMargins(0, 5, 0, 5)
        self.bottomLayout.setSpacing(10)

        # 상태 메시지
        self.statusContainer = QtWidgets.QWidget()
        self.statusLayout = QtWidgets.QHBoxLayout(self.statusContainer)
        self.statusLayout.setContentsMargins(5, 0, 0, 0)
        self.statusLayout.setSpacing(5)

        self.statusIcon = QtWidgets.QLabel("🔄")
        self.statusIcon.setStyleSheet(f"color: {CORNFLOWER_BLUE}; font-size: 15px;")
        self.statusLayout.addWidget(self.statusIcon)

        self.statusLabel = QtWidgets.QLabel("변환할 파일을 추가해 주세요")
        self.statusLabel.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 12px;
            color: {CORNFLOWER_BLUE};
        """)
        self.statusLayout.addWidget(self.statusLabel)
        self.statusLayout.addStretch()

        self.bottomLayout.addWidget(self.statusContainer, 3)  # 3:1 비율

        # 변환 버튼
        self.convertButton = QtWidgets.QPushButton("변환 시작")
        self.convertButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.convertButton.setMinimumHeight(36)
        self.convertButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {ROYAL_BLUE};
                color: {WHITE};
                font-family: 'Arial';
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {CORNFLOWER_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {DEEP_INDIGO};
                color: white;
            }}
        """)
        self.convertButton.clicked.connect(self.select_files)
        self.bottomLayout.addWidget(self.convertButton, 1)  # 비율 1

        self.contentLayout.addWidget(self.bottomWidget)

        # 프로그레스바
        self.progressBar = GradientProgressBar()
        self.progressBar.setFixedHeight(6)
        self.progressBar.setValue(0)
        self.progressBar.hide()  # 초기에는 숨김
        self.contentLayout.addWidget(self.progressBar)

        # 저장 경로 표시 (하단에 작게)
        self.saveInfoWidget = QtWidgets.QWidget()
        self.saveInfoLayout = QtWidgets.QHBoxLayout(self.saveInfoWidget)
        self.saveInfoLayout.setContentsMargins(5, 0, 5, 0)
        self.saveInfoLayout.setSpacing(5)

        self.saveIcon = QtWidgets.QLabel("📁")
        self.saveIcon.setStyleSheet(f"color: {LAVENDER_MIST}; font-size: 11px;")
        self.saveInfoLayout.addWidget(self.saveIcon)

        # 클릭 가능한 저장 위치 레이블로 변경
        self.saveLabel = ClickableLabel()
        self.updateSaveLocationLabel()  # 저장 위치 레이블 업데이트
        self.saveLabel.setStyleSheet(f"""
            font-family: 'Arial';
            font-size: 11px;
            color: {LAVENDER_MIST};
            text-decoration: underline;
        """)
        # 클릭 이벤트 연결
        self.saveLabel.clicked.connect(self.open_save_folder)
        self.saveInfoLayout.addWidget(self.saveLabel)
        self.saveInfoLayout.addStretch()

        self.contentLayout.addWidget(self.saveInfoWidget)

        # 컨텐츠 영역을 메인 레이아웃에 추가
        self.mainLayout.addWidget(self.content)

        # 제목 표시줄 드래그를 위한 이벤트 설정
        self.titleBar.mousePressEvent = self.titleBarMousePressEvent
        self.titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        self.titleBar.mouseReleaseEvent = self.titleBarMouseReleaseEvent
        self.dragPos = None

    def titleBarMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.Dialog.frameGeometry().topLeft()
            event.accept()

    def titleBarMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.Dialog.move(event.globalPos() - self.dragPos)
            event.accept()

    def titleBarMouseReleaseEvent(self, event):
        self.dragPos = None

    # 앱 종료 시 설정 저장
    def on_close(self):
        self.save_current_settings()
        self.Dialog.close()

    # 현재 설정 저장
    def save_current_settings(self):
        settings = {
            "quality": self.conversion_quality,
            "save_location_type": self.save_location_type,
            "save_location_path": self.save_location_path
        }
        save_settings(settings)

    # 저장 위치 표시 레이블 업데이트
    def updateSaveLocationLabel(self):
        if self.save_location_type == "original":
            self.saveLabel.setText("저장 위치: 원본 폴더")
            self.current_save_folder = ""  # 원본 폴더는 선택 전까지 알 수 없음
        elif self.save_location_type == "subfolder":
            self.saveLabel.setText(f"저장 위치: 원본 폴더/{self.save_location_path}")
            self.current_save_folder = self.save_location_path  # 하위 폴더 이름
        elif self.save_location_type == "custom":
            self.saveLabel.setText(f"저장 위치: {self.save_location_path}")
            self.current_save_folder = self.save_location_path  # 사용자 지정 폴더 경로

    # 저장 폴더 열기
    def open_save_folder(self):
        # 폴더 열기
        if self.current_save_folder:
            open_folder(self.current_save_folder)
        else:
            # 원본 폴더인 경우 마지막으로 처리한 파일의 폴더 열기 (없으면 다운로드 폴더)
            default_folder = os.path.expanduser("~/Downloads")
            open_folder(default_folder)

    # 설정 창 열기 함수 - 완전히 새롭게 구현
    def showSettingsDialog(self):
        try:
            # 모든 부모/자식 관계를 끊고 완전히 독립적인 설정 다이얼로그 생성
            settings_dialog = SettingsDialog(None)

            # 설정 값 초기화
            settings_dialog.qualitySlider.setValue(self.conversion_quality)

            if self.save_location_type == "original":
                settings_dialog.originalFolderRadio.setChecked(True)
            elif self.save_location_type == "subfolder":
                settings_dialog.subfoldRadio.setChecked(True)
                settings_dialog.subfolderInput.setText(self.save_location_path)
            elif self.save_location_type == "custom":
                settings_dialog.customFolderRadio.setChecked(True)
                settings_dialog.customFolderPath.setText(self.save_location_path)

            # 화면 중앙에 표시
            screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
            x = (screen_geometry.width() - settings_dialog.width()) // 2
            y = (screen_geometry.height() - settings_dialog.height()) // 2
            settings_dialog.move(x, y)

            # 결과를 기다린 후 처리 (블로킹 호출)
            if settings_dialog.exec_() == QtWidgets.QDialog.Accepted:
                # 설정 가져오기
                settings = settings_dialog.getSettings()
                self.conversion_quality = settings["quality"]
                self.save_location_type = settings["save_location_type"]
                self.save_location_path = settings["save_location_path"]

                # UI 업데이트
                self.settingsLabel.setText(f"변환 품질: {self.conversion_quality}%")
                self.updateSaveLocationLabel()  # 저장 위치 레이블 업데이트

                # 설정 저장
                self.save_current_settings()
        except Exception as e:
            # 자세한 오류 정보 출력
            print(f"설정 대화상자 오류: {str(e)}")
            traceback.print_exc()

    # 파일 선택 다이얼로그를 열어 이미지 선택
    def select_files(self):
        file_dialog = QFileDialog(self.Dialog, "이미지 파일 선택", os.path.expanduser("~/Downloads"))
        file_dialog.setNameFilters(["이미지 파일 (*.jpg *.jpeg *.png *.gif)", "All Files (*)"])
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_() == QFileDialog.Accepted:
            filenames = file_dialog.selectedFiles()
            if filenames:
                # 첫 번째 파일의 디렉토리를 현재 작업 디렉토리로 설정
                self.last_working_dir = os.path.dirname(filenames[0])
            self.convert_files(filenames)

    # 이미지 파일을 WEBP로 변환하는 함수
    def convert_files(self, filenames):
        # 변환 옵션 선택 - 설정값 사용
        option = f" -q {self.conversion_quality}"
        image_files = []
        unsupported_files = []
        progressNum = 0  # 프로그레스 바의 진행도

        # 이미지 확장자 확인
        for filename in filenames:
            # 이미지 파일인 경우 이미지 파일 리스트에 추가
            if os.path.splitext(filename)[1].lower() in ('.jpg', '.jpeg', '.png', '.gif'):
                image_files.append(filename)
            else:
                # 이미지 파일이 아닌 경우 지원하지 않는 파일 리스트에 추가
                unsupported_files.append(filename)

        # 프로그레스바 초기화 및 표시
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(len(image_files))
        self.progressBar.show()

        # 이미지 파일이 없을 경우 경고 메시지 출력
        if not image_files:
            self.statusIcon.setText("⚠️")
            self.statusLabel.setText("선택된 파일에 이미지 파일이 없습니다.")
            self.statusLabel.setStyleSheet("""
                font-family: 'Arial';
                font-size: 12px;
                color: #FF5252;
            """)
            self.frame.setStyleSheet(f"""
                border: 2px dashed #FF5252;
                border-radius: 12px;
                background-color: {MEDIUM_GRAY};
            """)

            # 3초 후 원래 스타일로 복원
            QtCore.QTimer.singleShot(3000, lambda: self.frame.setStyleSheet(f"""
                border: 2px dashed {DEEP_INDIGO};
                border-radius: 12px;
                background-color: {MEDIUM_GRAY};
            """))
            QtCore.QTimer.singleShot(3000, lambda: self.statusIcon.setText("🔄"))
            QtCore.QTimer.singleShot(3000, lambda: self.statusLabel.setText("변환할 파일을 추가해 주세요"))
            QtCore.QTimer.singleShot(3000, lambda: self.statusLabel.setStyleSheet(f"""
                font-family: 'Arial';
                font-size: 12px;
                color: {CORNFLOWER_BLUE};
            """))
            QtCore.QTimer.singleShot(3000, lambda: self.progressBar.hide())
        else:  # 이미지 파일이 존재할 경우 변환을 시작함
            # UI 업데이트
            self.statusIcon.setText("⏳")
            self.statusLabel.setText("변환 중...")
            self.statusLabel.setStyleSheet(f"""
                font-family: 'Arial';
                font-size: 12px;
                color: {ROYAL_BLUE};
            """)
            self.dropLabel.setText("변환 중...")
            self.frame.setStyleSheet(f"""
                border: 2px dashed {ROYAL_BLUE};
                border-radius: 12px;
                background-color: {MEDIUM_GRAY};
            """)

            # 마지막으로 처리한 파일 (결과 경로를 저장)
            last_output_folder = None

            # 변환 시작
            for filename in image_files:
                output_folder, output_filename = self.makeFolder(filename)
                if os.path.splitext(filename)[1].lower() == '.gif':
                    command = f'"{cwebp_path}" "{filename}" {option} -o {output_filename}'
                else:
                    command = f'"{cwebp_path}" "{filename}" {option} -o {output_filename}'

                # 변환 실행
                subprocess.call(command, shell=True)

                # 마지막 출력 폴더 저장
                last_output_folder = output_folder

                # 변환 완료 후 프로그레스바 수치 + 1
                progressNum += 1
                self.progressBar.setValue(progressNum)

            # 저장 폴더 업데이트 (결과를 볼 수 있게)
            if last_output_folder:
                self.current_save_folder = last_output_folder

            # 변환 결과 출력
            self.statusIcon.setText("✅")
            if len(image_files) == 1:
                self.statusLabel.setText(f"{os.path.basename(output_filename)[:-1]}으로 변환되었습니다.")
                self.dropLabel.setText("변환 완료!")
            else:
                self.statusLabel.setText(f"총 {len(image_files)}개의 파일이 변환되었습니다.")
                self.dropLabel.setText(f"{len(image_files)}개 변환 완료!")

            # 성공 스타일
            self.statusLabel.setStyleSheet(f"""
                font-family: 'Arial';
                font-size: 12px;
                color: {CORNFLOWER_BLUE};
            """)

            self.frame.setStyleSheet(f"""
                border: 2px solid {CORNFLOWER_BLUE};
                border-radius: 12px;
                background-color: {MEDIUM_GRAY}; 
            """)

            # 3초 후 원래 스타일과 메시지로 복원
            QtCore.QTimer.singleShot(3000, lambda: self.frame.setStyleSheet(f"""
                border: 2px dashed {DEEP_INDIGO};
                border-radius: 12px;
                background-color: {MEDIUM_GRAY};
            """))
            QtCore.QTimer.singleShot(3000, lambda: self.dropLabel.setText("파일을 여기에 드래그하세요"))
            QtCore.QTimer.singleShot(3000, lambda: self.statusIcon.setText("🔄"))
            QtCore.QTimer.singleShot(3000, lambda: self.statusLabel.setText("변환할 파일을 추가해 주세요"))
            QtCore.QTimer.singleShot(3000, lambda: self.statusLabel.setStyleSheet(f"""
                font-family: 'Arial';
                font-size: 12px;
                color: {CORNFLOWER_BLUE};
            """))
            QtCore.QTimer.singleShot(3000, lambda: self.progressBar.hide())

    def makeFolder(self, filename):
        # 설정에 따라 저장 위치 결정
        base_name = '변환된_' + os.path.basename(filename)

        if self.save_location_type == "original":
            # 원본 폴더에 저장
            output_directory = os.path.dirname(filename)
        elif self.save_location_type == "subfolder":
            # 원본 폴더의 하위 폴더에 저장
            output_directory = os.path.join(os.path.dirname(filename), self.save_location_path)
            try:
                os.makedirs(output_directory, exist_ok=True)
            except Exception as e:
                print(f"하위 폴더 생성 오류: {e}")
                # 실패 시 원본 폴더에 저장
                output_directory = os.path.dirname(filename)
        elif self.save_location_type == "custom":
            # 사용자 지정 폴더에 저장
            output_directory = self.save_location_path
            try:
                os.makedirs(output_directory, exist_ok=True)
            except Exception as e:
                print(f"폴더 생성 오류: {e}")
                # 실패 시 원본 폴더에 저장
                output_directory = os.path.dirname(filename)
        else:
            # 기본값: 하위 폴더에 저장
            output_directory = os.path.join(os.path.dirname(filename), "변환된 이미지")
            try:
                os.makedirs(output_directory, exist_ok=True)
            except Exception as e:
                print(f"기본 폴더 생성 오류: {e}")
                # 실패 시 원본 폴더에 저장
                output_directory = os.path.dirname(filename)

        output_filename = os.path.join(output_directory, base_name)
        output_filename = '"' + os.path.splitext(output_filename)[0] + '.webp' + '"'
        return output_directory, output_filename


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # 앱 글꼴 설정
    font = QFont("Arial", 10)
    app.setFont(font)

    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)

    # DragDropFrame이 ui 객체에 접근할 수 있도록 설정
    Dialog.ui = ui

    Dialog.show()
    sys.exit(app.exec_())