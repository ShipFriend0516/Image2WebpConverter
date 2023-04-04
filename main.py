import tkinter as tk
from tkinter import filedialog
import subprocess
import os

# exe 파일에서 실행될 경우의 상대경로로 설정
cwebp_path = os.path.join(os.path.dirname(__file__), 'cwebp.exe')

def convert_image():
    # 파일 대화상자 열기
    filenames = filedialog.askopenfilenames()

    # 변환 옵션 선택
    option = " -q 75"

    for filename in filenames:
        # 변환 명령어 실행
        output_filename = '"' + os.path.splitext(filename)[0] + '.webp' + '"'
        command = f'"{cwebp_path}" "{filename}" {option} -o {output_filename}'
        subprocess.call(command, shell=True)

        # 변환 결과 출력
        if len(filenames) == 1:
          result_label.config(text=f"{os.path.basename(output_filename)}으로 변환되었습니다.", bg="#0B2447",fg="#FFFFFF", padx="3", pady="3")
        else: result_label.config(text=f"선택한 파일들이 모두 변환되었습니다.", bg="#0B2447",fg="#FFFFFF", padx="3", pady="3")


if __name__ == "__main__":
    # GUI 디자인
    root = tk.Tk()
    root.title("WebP 변환 프로그램")
    root.geometry("600x200")
    root.config(bg="#DAF5FF")

    file_label = tk.Label(root, text="이미지 파일 선택", font=("Arial", 30), pady="20", bg="#DAF5FF", fg="#19376D")
    file_label.pack()

    file_button = tk.Button(root, text="파일 선택", command=convert_image,width="20", height="1", pady="3",bg="#576CBC",fg="#FFFFFF", font=("Arial", 15))
    file_button.place(relx=0.5, rely=0.5, anchor="center")

    result_label = tk.Label(root, text="", bg="#DAF5FF")
    result_label.place(relx=0.5, rely=0.8, anchor="center")

    iconpath = os.path.join(os.path.dirname(__file__), 'icon.ico')
    if os.path.isfile(iconpath):
        root.iconbitmap(iconpath)

    root.mainloop()
