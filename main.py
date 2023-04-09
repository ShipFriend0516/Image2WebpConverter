import tkinter as tk
from tkinter import filedialog
import tkinter.dnd
import subprocess
import os

# exe 파일에서 실행될 경우의 상대경로로 설정
cwebp_path = os.path.join(os.path.dirname(__file__), 'cwebp.exe')
webpmux_path = os.path.join(os.path.dirname(__file__), 'webpmux.exe')

def convert_image():
    # 파일 대화상자 열기
    filenames = filedialog.askopenfilenames()

    # 변환 옵션 선택
    option = " -q 75"
    image_files = []
    unsupported_files = []

    for filename in filenames:
        # 이미지 파일인 경우 이미지 파일 리스트에 추가
        if os.path.splitext(filename)[1].lower() in ('.jpg', '.jpeg', '.png', '.gif'):
            image_files.append(filename)
        else:
            # 이미지 파일이 아닌 경우 지원하지 않는 파일 리스트에 추가
            unsupported_files.append(filename)

    # 이미지 파일이 없을 경우 경고 메시지 출력
    if not image_files:
        result_label.config(text=f"이미지 파일을 선택해주세요.", bg="#D90429", fg="#FFFFFF",
                            padx="3", pady="3")
    else:
        option = " -q 75"
        for filename in image_files:
            output_filename = '"' + os.path.splitext(filename)[0] + '.webp' + '"'
            if os.path.splitext(filename)[1].lower() == '.gif':
                command = f'"{webpmux_path}" -get frame {filename} -o frame-#.webp'
                subprocess.call(command, shell=True)
                command = f'"{cwebp_path}" frame_*.webp -o {output_filename}'
            else:
                command = f'"{cwebp_path}" "{filename}" {option} -o {output_filename}'
            subprocess.call(command, shell=True)

        # 변환 결과 출력
        if len(image_files) == 1:
            result_label.config(text=f"{os.path.basename(output_filename)}으로 변환되었습니다.", bg="#0B2447", fg="#FFFFFF",
                                padx="3", pady="3")
        else:
            result_label.config(text=f"선택한 파일들이 모두 변환되었습니다.", bg="#0B2447", fg="#FFFFFF", padx="3", pady="3")

    if len(unsupported_files) == 0:
        result_label2.config(text=f"변환 성공: {len(image_files)}개, 실패: {len(unsupported_files)}개", bg="#539165", fg="#FFFFFF", padx="3", pady="3")
    elif len(image_files) == 0:
        result_label2.config(text=f"변환 성공: {len(image_files)}개, 실패: {len(unsupported_files)}개", bg="#D90429", fg="#FFFFFF", padx="3", pady="3")
    else:
        result_label2.config(text=f"변환 성공: {len(image_files)}개, 실패: {len(unsupported_files)}개", bg="#F7C04A", fg="#FFFFFF", padx="3", pady="3")

if __name__ == "__main__":
    # GUI 디자인
    root = tk.Tk()
    root.title("WebP 변환 프로그램")
    root.geometry("500x300")
    root.config(bg="#DAF5FF")

    filenames = []

    file_label = tk.Label(root, text="이미지 파일 선택", font=("Arial", 30), pady="20", bg="#DAF5FF", fg="#19376D")
    file_label.pack()

    file_button = tk.Button(root, text="파일 선택", command=convert_image,width="20", height="1", pady="3",bg="#576CBC",fg="#FFFFFF", font=("Arial", 15))
    file_button.place(relx=0.5, rely=0.5, anchor="center")


    result_label = tk.Label(root, text="", bg="#DAF5FF")
    result_label.place(relx=0.5, rely=0.8, anchor="center")

    result_label2 = tk.Label(root, bg="#DAF5FF")
    result_label2.place(relx=0.5, rely=0.9, anchor="center")

    iconpath = os.path.join(os.path.dirname(__file__), 'icon.ico')
    if os.path.isfile(iconpath):
        root.iconbitmap(iconpath)

    root.mainloop()