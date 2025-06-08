import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, Scale
import random
import time
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import json
import datetime

# 기능 추가에 필요한 라이브러리
import pygame
import pyautogui
import imageio

# --- 이미지 생성 함수 (이전과 동일) ---
def create_game_images():
    images = {}
    size = (36, 36)
    bg_color, outline_color = "#c0c0c0", "#7b7b7b"
    num_colors = { 1: "#0000FF", 2: "#008200", 3: "#FF0000", 4: "#000084", 5: "#840000", 6: "#008284", 7: "#840084", 8: "#757575" }
    try:
        font = ImageFont.truetype("malgun.ttf", 20); f_font = ImageFont.truetype("arialbd.ttf", 24); q_font = ImageFont.truetype("arialbd.ttf", 22)
    except IOError:
        font = ImageFont.load_default(); f_font = ImageFont.load_default(); q_font = ImageFont.load_default()
    img = Image.new("RGB", size, bg_color); draw = ImageDraw.Draw(img)
    draw.line([(0,0), (size[0]-1,0)], fill="#ffffff"); draw.line([(0,0), (0,size[1]-1)], fill="#ffffff")
    draw.line([(size[0]-1,0), (size[0]-1,size[1]-1)], fill=outline_color); draw.line([(0,size[1]-1), (size[0]-1,size[1]-1)], fill=outline_color)
    images["hidden"] = ImageTk.PhotoImage(img)
    img = Image.new("RGB", size, bg_color); draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0), (size[0]-1, size[1]-1)], outline=outline_color); images["revealed"] = ImageTk.PhotoImage(img)
    img_f = images["revealed"]._PhotoImage__photo.copy(); img = ImageTk.getimage(img_f); draw = ImageDraw.Draw(img)
    draw.text((8, 3), "F", font=f_font, fill="red"); images["f_grade"] = ImageTk.PhotoImage(img)
    img_flag = images["hidden"]._PhotoImage__photo.copy(); img = ImageTk.getimage(img_flag); draw = ImageDraw.Draw(img)
    draw.text((8, 3), "F", font=f_font, fill="blue"); images["flag"] = ImageTk.PhotoImage(img)
    img_q = images["hidden"]._PhotoImage__photo.copy(); img = ImageTk.getimage(img_q); draw = ImageDraw.Draw(img)
    draw.text((10, 3), "?", font=q_font, fill="green"); images["question"] = ImageTk.PhotoImage(img)
    for i in range(1, 9):
        img_num = images["revealed"]._PhotoImage__photo.copy(); img = ImageTk.getimage(img_num); draw = ImageDraw.Draw(img)
        draw.text((12, 5), str(i), font=font, fill=num_colors[i]); images[str(i)] = ImageTk.PhotoImage(img)
    return images

# --- 메인 게임 클래스 ---
class FGradeFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("F학점 지뢰찾기")
        self.root.resizable(False, False)
        self.root.configure(bg="#c0c0c0")

        self.current_volume = 0.5
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("background.mp3")
            pygame.mixer.music.set_volume(self.current_volume)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("오류: 'background.mp3' 파일을 찾을 수 없거나 불러올 수 없습니다.")

        self.images = create_game_images()
        self.num_images = {i: self.images[str(i)] for i in range(1, 9)}

        self.difficulty_levels = { "쉬움": (9, 9, 10), "보통": (16, 16, 40), "어려움": (16, 30, 99), "사용자 설정": "custom" }
        self.current_difficulty = "보통"
        self.rows, self.cols, self.fgrades = self.difficulty_levels[self.current_difficulty]
        self.highscores = self.load_highscores()
        
        self.screenshot_images = []
        
        self.setup_ui()
        self.restart_game()

    def setup_ui(self):
        if hasattr(self, 'top_frame'): self.top_frame.destroy()
        self.top_frame = tk.Frame(self.root, bg="#c0c0c0")
        self.top_frame.pack(pady=5, padx=10, fill=tk.X)

        info_frame = tk.Frame(self.top_frame, bg="#c0c0c0")
        info_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        Label(info_frame, text="난이도:", bg="#c0c0c0").pack(side=tk.LEFT, padx=(5,0))
        self.diff_var = tk.StringVar(value=self.current_difficulty)
        diff_menu = tk.OptionMenu(info_frame, self.diff_var, *self.difficulty_levels.keys(), command=self.change_difficulty)
        diff_menu.config(bg="white", relief="raised", width=8)
        diff_menu.pack(side=tk.LEFT, padx=5)

        self.flags_label = tk.Label(info_frame, text="", font=("Arial", 12, "bold"), bg="#c0c0c0")
        self.flags_label.pack(side=tk.LEFT, padx=10)
        self.timer_label = tk.Label(info_frame, text="", font=("Arial", 12, "bold"), bg="#c0c0c0")
        self.timer_label.pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(self.top_frame, bg="#c0c0c0")
        button_frame.pack(side=tk.RIGHT, anchor=tk.E)

        self.gif_btn = Button(button_frame, text="GIF 저장", command=self.save_gif, width=8)
        self.gif_btn.pack(side=tk.LEFT, padx=5)
        self.restart_btn = Button(button_frame, text="재시작", command=self.restart_game, width=8)
        self.restart_btn.pack(side=tk.LEFT, padx=5)

        if hasattr(self, 'bottom_control_frame'): self.bottom_control_frame.destroy()
        self.bottom_control_frame = tk.Frame(self.root, bg="#c0c0c0")
        self.bottom_control_frame.pack(pady=5, padx=10, fill=tk.X)
        
        Label(self.bottom_control_frame, text="볼륨:", bg="#c0c0c0").pack(side=tk.LEFT, padx=(5,0))
        
        # --- 볼륨 슬라이더 그래픽 개선 ---
        self.volume_slider = Scale(
            self.bottom_control_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            command=self.set_volume, 
            length=150, 
            showvalue=0, # 숫자 표시 제거
            bg="#c0c0c0", # 배경색
            troughcolor="#e0e0e0", # 슬라이더 경로 색
            sliderrelief=tk.FLAT, # 슬라이더 핸들 스타일
            highlightthickness=0, # 포커스 테두리 제거
            activebackground="#a0a0a0" # 클릭 시 핸들 색
        )
        self.volume_slider.set(self.current_volume * 100)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        if hasattr(self, 'board_frame'): self.board_frame.destroy()
        self.board_frame = tk.Frame(self.root, bg="#c0c0c0")
        self.board_frame.pack(padx=10, pady=5)
        
        if hasattr(self, 'bottom_info_frame'): self.bottom_info_frame.destroy()
        self.bottom_info_frame = tk.Frame(self.root, bg="#c0c0c0")
        self.bottom_info_frame.pack(pady=(0, 10))
        self.highscore_label = tk.Label(self.bottom_info_frame, text="", font=("Malgun Gothic", 10, "bold"), fg="darkblue", bg="#c0c0c0")
        self.highscore_label.pack()
        self.status_label = tk.Label(self.bottom_info_frame, text="", font=("Malgun Gothic", 11), bg="#c0c0c0")
        self.status_label.pack()

    def set_volume(self, value_str):
        if not pygame.mixer.get_init(): return
        volume = int(value_str) / 100.0
        self.current_volume = volume
        pygame.mixer.music.set_volume(self.current_volume)

    def load_highscores(self):
        try:
            with open("highscore.json", "r") as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return { "쉬움": {"time": 999, "date": "N/A"}, "보통": {"time": 999, "date": "N/A"}, "어려움": {"time": 999, "date": "N/A"} }

    def save_highscores(self):
        with open("highscore.json", "w") as f: json.dump(self.highscores, f, indent=4)

    def update_highscore_label(self):
        if self.current_difficulty != "사용자 설정":
            score = self.highscores.get(self.current_difficulty)
            self.highscore_label.config(text=f"최고 기록 ({self.current_difficulty}): {score['time']}초 ({score['date']})")
        else:
            self.highscore_label.config(text="사용자 설정 모드에서는 기록이 저장되지 않습니다.")

    def restart_game(self):
        self.timer_running = False; self.game_started = False; self.game_over = False
        self.flags = set(); self.questions = set(); self.revealed = set()
        self.flags_left = self.fgrades; self.elapsed_time = 0
        
        if hasattr(self, 'board_frame'):
            for widget in self.board_frame.winfo_children(): widget.destroy()
        else:
            self.board_frame = tk.Frame(self.root)
            self.board_frame.pack(padx=10, pady=5)
        
        self.create_board()
        self.update_info_labels()
        self.status_label.config(text="칸을 클릭하여 게임을 시작하세요.")
        self.screenshot_images.clear()
        self.update_highscore_label()
        self.capture_screen()
        
        try:
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(self.current_volume)
        except pygame.error: pass

    def left_click(self, r, c):
        if self.game_over or (r,c) in self.flags or (r,c) in self.questions: return
        if not self.game_started:
            self.game_started = True; self.place_fgrades((r, c))
            self.start_timer(); self.status_label.config(text="F학점을 모두 피하세요!")
        if (r,c) in self.revealed: return
        if (r, c) in self.fgrade_positions:
            self.game_over = True; self.timer_running = False
            pygame.mixer.music.stop()
            self.reveal_all(); self.buttons[(r,c)].config(bg="red")
            self.status_label.config(text="게임 오버! F학점을 밟았어요...")
            self.capture_screen()
            messagebox.showinfo("학사경고", "F학점을 밟았습니다! 다음 학기에 재수강하세요.")
            return
        self.reveal_cell(r, c)
        if self.check_win():
            self.game_over = True; self.timer_running = False
            pygame.mixer.music.stop()
            self.reveal_all(); self.status_label.config(text="축하합니다! F학점을 모두 피했어요!")
            self.capture_screen()
            if self.current_difficulty != "사용자 설정" and self.elapsed_time < self.highscores[self.current_difficulty]["time"]:
                old_score = self.highscores[self.current_difficulty]["time"]
                self.highscores[self.current_difficulty] = {"time": self.elapsed_time, "date": datetime.datetime.now().strftime("%Y-%m-%d")}
                self.save_highscores()
                messagebox.showinfo("최고기록 경신!", f"새로운 기록 달성! {old_score}초 -> {self.elapsed_time}초")
                self.update_highscore_label()
            else: messagebox.showinfo("장학금", "완벽한 성적입니다! 모든 F학점을 피했습니다.")
            
    def right_click(self, r, c):
        if self.game_over or not self.game_started or (r, c) in self.revealed: return
        btn = self.buttons[(r, c)]
        if (r,c) in self.flags:
            self.flags.remove((r,c)); self.questions.add((r,c))
            btn.config(image=self.images["question"]); self.flags_left += 1
        elif (r,c) in self.questions:
            self.questions.remove((r,c)); btn.config(image=self.images["hidden"])
        else:
            if self.flags_left > 0:
                self.flags.add((r, c)); btn.config(image=self.images["flag"]); self.flags_left -= 1
        self.update_info_labels()

    def change_difficulty(self, value):
        self.current_difficulty = value
        if value == "사용자 설정": self.open_custom_difficulty_dialog()
        else:
            self.rows, self.cols, self.fgrades = self.difficulty_levels[value]
            self.restart_game()

    def create_board(self):
        self.buttons = {}
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, image=self.images["hidden"], relief="flat", borderwidth=0)
                btn.grid(row=r, column=c)
                btn.bind("<Button-1>", lambda e, x=r, y=c: self.left_click_with_capture(x, y))
                btn.bind("<Button-3>", lambda e, x=r, y=c: self.right_click_with_capture(x, y))
                self.buttons[(r, c)] = btn

    def place_fgrades(self, first_click_pos):
        self.fgrade_positions = set()
        while len(self.fgrade_positions) < self.fgrades:
            pos = (random.randint(0, self.rows-1), random.randint(0, self.cols-1))
            if pos != first_click_pos: self.fgrade_positions.add(pos)
        self.adjacent_counts = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.fgrade_positions: continue
                count = 0
                for nr in range(max(0, r-1), min(self.rows, r+2)):
                    for nc in range(max(0, c-1), min(self.cols, c+2)):
                        if (nr, nc) in self.fgrade_positions: count += 1
                self.adjacent_counts[(r, c)] = count

    def left_click_with_capture(self, r, c):
        if not self.game_over: self.capture_screen()
        self.left_click(r, c)
    def right_click_with_capture(self, r, c):
        if not self.game_over: self.capture_screen()
        self.right_click(r, c)
    def reveal_cell(self, r, c):
        if (r,c) in self.revealed or (r,c) in self.flags or (r,c) in self.questions: return
        self.revealed.add((r,c))
        btn = self.buttons[(r, c)]
        count = self.adjacent_counts.get((r, c), 0)
        if count > 0: btn.config(image=self.num_images[count], relief="flat")
        else:
            btn.config(image=self.images["revealed"], relief="flat")
            for nr in range(max(0, r-1), min(self.rows, r+2)):
                for nc in range(max(0, c-1), min(self.cols, c+2)):
                    if (nr, nc) != (r, c): self.reveal_cell(nr, nc)
    def reveal_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                pos = (r,c)
                if pos in self.revealed: continue
                btn = self.buttons[pos]
                if pos in self.fgrade_positions and pos not in self.flags: btn.config(image=self.images["f_grade"])
                elif pos not in self.fgrade_positions and pos in self.flags: btn.config(bg="red")
    def check_win(self): return len(self.revealed) == self.rows * self.cols - self.fgrades
    def start_timer(self):
        self.start_time = time.time(); self.timer_running = True
        threading.Thread(target=self.update_timer, daemon=True).start()
    def update_timer(self):
        while self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            self.update_info_labels(); time.sleep(1)
    def update_info_labels(self):
        self.flags_label.config(text=f"남은 F: {self.flags_left:02d}")
        self.timer_label.config(text=f"시간: {self.elapsed_time:03d}")
    def open_custom_difficulty_dialog(self):
        dialog = Toplevel(self.root); dialog.title("사용자 설정"); dialog.geometry("250x150"); dialog.resizable(False, False)
        Label(dialog, text="가로 (9-30):").grid(row=0, column=0, padx=5, pady=5)
        rows_entry = Entry(dialog, width=10); rows_entry.grid(row=0, column=1); rows_entry.insert(0, str(self.rows))
        Label(dialog, text="세로 (9-24):").grid(row=1, column=0, padx=5, pady=5)
        cols_entry = Entry(dialog, width=10); cols_entry.grid(row=1, column=1); cols_entry.insert(0, str(self.cols))
        Label(dialog, text="F학점 (10-668):").grid(row=2, column=0, padx=5, pady=5)
        fgrades_entry = Entry(dialog, width=10); fgrades_entry.grid(row=2, column=1); fgrades_entry.insert(0, str(self.fgrades))
        def on_ok():
            try:
                r,c,f = int(rows_entry.get()), int(cols_entry.get()), int(fgrades_entry.get())
                r,c,f = max(9, min(r, 30)), max(9, min(c, 24)), max(10, min(f, r * c - 9))
                self.rows, self.cols, self.fgrades = r, c, f
                self.restart_game(); dialog.destroy()
            except ValueError: messagebox.showerror("입력 오류", "숫자만 입력해주세요.", parent=dialog)
        Button(dialog, text="확인", command=on_ok).grid(row=3, column=0, columnspan=2, pady=10)
        dialog.transient(self.root); dialog.grab_set(); self.root.wait_window(dialog)
    def capture_screen(self): self.root.after(50, self._take_screenshot)
    def _take_screenshot(self):
        try:
            x,y,w,h = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height()
            self.screenshot_images.append(pyautogui.screenshot(region=(x, y, w, h)))
        except Exception as e: print(f"화면 캡처 오류: {e}")
    def save_gif(self):
        if not self.screenshot_images: messagebox.showinfo("알림", "저장할 게임 플레이 기록이 없습니다."); return
        gif_path = "fgrade_finder_play.gif"
        try:
            imageio.mimsave(gif_path, self.screenshot_images, duration=0.5)
            messagebox.showinfo("저장 완료", f"게임 플레이 GIF가 '{gif_path}'로 저장되었습니다.")
        except Exception as e: messagebox.showerror("오류", f"GIF 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main_root = tk.Tk()
    game = FGradeFinder(main_root)
    main_root.mainloop()
