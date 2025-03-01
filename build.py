import os
import shutil
import subprocess

# 프로젝트 폴더 및 빌드 폴더 설정
project_folder = os.path.dirname(os.path.abspath(__file__))
build_folder = os.path.join(project_folder, 'build')
dist_folder = os.path.join(project_folder, 'dist')
output_folder = os.path.join(project_folder, 'output')

# 기존 빌드 폴더 정리
if os.path.exists(build_folder):
    shutil.rmtree(build_folder)
if os.path.exists(dist_folder):
    shutil.rmtree(dist_folder)
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)

# output 폴더 생성
os.makedirs(output_folder)

# PyInstaller 실행
print("PyInstaller로 exe 빌드 중...")
subprocess.call([
    'pyinstaller',
    '--onefile',
    '--windowed',
    '--icon=icon.ico',
    '--name=이미지변환기',
    '--clean',
    '--add-data', 'cwebp.exe;.',
    '--add-data', 'icon.ico;.',
    'ImageToWebp.py'
])

# 생성된 파일을 output 폴더로 이동
print("최종 파일 복사 중...")
shutil.copy(os.path.join(dist_folder, '이미지변환기.exe'), output_folder)

# 설명서 파일 생성
readme_content = """# 이미지 변환기 사용법

1. 프로그램을 실행합니다.
2. 변환할 이미지 파일을 드래그 앤 드롭하거나 영역을 클릭하여 파일을 선택합니다.
3. 변환 옵션을 설정하려면 오른쪽 상단의 ⚙️ 아이콘을 클릭합니다.
4. 변환 품질과 저장 위치를 설정할 수 있습니다.
5. 변환된 파일을 확인하려면 하단의 저장 위치를 클릭하세요.

문의사항: 깃허브 이슈
"""

with open(os.path.join(output_folder, '사용설명서.txt'), 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("빌드 완료! output 폴더에서 결과물을 확인하세요.")