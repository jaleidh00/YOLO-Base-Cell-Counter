import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import pyautogui
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageTk
import keyboard  # 전역 키 입력 감지

# YOLO 모델 불러오기
model = YOLO("./runs/detect/train/weights/best.pt")

# 전역 변수
selected_window_title = None
selected_hwnd = None
roi_coords = None  # 절대 좌표로 저장

def get_window_titles():
    titles = []
    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            titles.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_callback, None)
    return titles

def refresh_window_list():
    window_combobox['values'] = [title for _, title in get_window_titles()]

def on_window_select(event):
    global selected_hwnd, selected_window_title
    selected_window_title = window_combobox.get()
    for hwnd, title in get_window_titles():
        if title == selected_window_title:
            selected_hwnd = hwnd
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            break

def select_roi():
    global roi_coords

    if selected_hwnd is None:
        print("윈도우를 먼저 선택하세요.")
        return

    win32gui.SetForegroundWindow(selected_hwnd)
    win32gui.BringWindowToTop(selected_hwnd)

    overlay = tk.Toplevel(root)
    overlay.attributes('-fullscreen', True)
    overlay.attributes('-topmost', True)
    overlay.configure(bg='black')
    overlay.attributes('-alpha', 0.3)
    overlay.title("ROI 선택")

    canvas = tk.Canvas(overlay, cursor="cross", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = None
    rect_id = None

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_mouse_drag(event):
        nonlocal rect_id
        canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        global roi_coords
        end_x, end_y = event.x, event.y
        rx1, ry1 = min(start_x, end_x), min(start_y, end_y)
        rx2, ry2 = max(start_x, end_x), max(start_y, end_y)

        roi_coords = (rx1, ry1, rx2, ry2)
        overlay.destroy()
        print(f"ROI 선택 완료: {roi_coords}")

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

def run_yolo():
    global roi_coords, selected_hwnd

    if roi_coords is None or selected_hwnd is None:
        print("ROI와 창을 모두 선택하세요.")
        return

    win_left, win_top, win_right, win_bottom = win32gui.GetWindowRect(selected_hwnd)
    win_w, win_h = win_right - win_left, win_bottom - win_top

    rx1, ry1, rx2, ry2 = roi_coords
    roi_w, roi_h = rx2 - rx1, ry2 - ry1
    roi_in_win_x = rx1 - win_left
    roi_in_win_y = ry1 - win_top

    full_win_img = pyautogui.screenshot(region=(win_left, win_top, win_w, win_h))
    full_win_np = np.array(full_win_img)
    roi_img = full_win_np[roi_in_win_y:roi_in_win_y + roi_h, roi_in_win_x:roi_in_win_x + roi_w]

    results = model(roi_img)[0]

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        label = f"{model.names[cls]} {conf:.2f}"
        cv2.rectangle(roi_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(roi_img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("YOLO Result", roi_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Tkinter UI 설정
root = tk.Tk()
root.title("YOLO ROI 감지기")
root.geometry("400x200")

window_combobox = ttk.Combobox(root, state="readonly")
window_combobox.pack(pady=10)
window_combobox.bind("<<ComboboxSelected>>", on_window_select)

refresh_btn = tk.Button(root, text="창 새로고침", command=refresh_window_list)
refresh_btn.pack(pady=5)

roi_btn = tk.Button(root, text="ROI 선택", command=select_roi)
roi_btn.pack(pady=5)

# 전역 단축키 등록
keyboard.add_hotkey("F6", run_yolo)

refresh_window_list()
root.mainloop()

# app