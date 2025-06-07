import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import threading
import pygame
import pyautogui
import imageio
from PIL import Image

class FGradeFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("F학점 찾기")
        self.root.resizable(False, False)

        # 배경음악 초기화
        pygame.mixer.init()
        pygame.mixer.music.load("background.mp3")  # 배경음악 파일은 같은 폴더에 넣으세요
        pygame.mixer.music.play(-1)

        # 변수 초기화
        self.difficulty_levels = {
            "쉬움": (9, 9, 10),
            "보통": (16, 16, 40),
            "어려움": (16, 30, 99)
        }
        self.rows, self.cols, self.fgrades = self.difficulty_levels["보통"]
        self.flags_left = self.fgrades
        self.game_started = False
        self.start_time = 0
        self.elapsed_time = 0
        self.timer_running = False
        self.screenshot_images = []

        # UI 구성
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.diff_label = tk.Label(self.top_frame, text="난이도:")
        self.diff_label.pack(side=tk.LEFT)

        self.diff_var = tk.StringVar(value="보통")
        self.diff_menu = tk.OptionMenu(self.top_frame, self.diff_var, *self.difficulty_levels.keys(), command=self.change_difficulty)
        self.diff_menu.pack(side=tk.LEFT)

        self.flags_label = tk.Label(self.top_frame, text=f"남은 F학점: {self.flags_left}")
        self.flags_label.pack(side=tk.LEFT, padx=20)

        self.timer_label = tk.Label(self.top_frame, text="시간: 0초")
        self.timer_label.pack(side=tk.LEFT, padx=20)

        self.gif_btn = tk.Button(self.top_frame, text="GIF 저장", command=self.save_gif)
        self.gif_btn.pack(side=tk.LEFT, padx=10)

        self.restart_btn = tk.Button(self.top_frame, text="재시작", command=self.restart_game)
        self.restart_btn.pack(side=tk.LEFT)

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.status_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.create_board()
        self.place_fgrades()

    def change_difficulty(self, value):
        self.rows, self.cols, self.fgrades = self.difficulty_levels[value]
        self.flags_left = self.fgrades
        self.flags_label.config(text=f"남은 F학점: {self.flags_left}")
        self.restart_game()

    def create_board(self):
        self.buttons = {}
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, font=("Arial", 12, "bold"), relief=tk.RAISED)
                btn.grid(row=r, column=c)
                btn.bind("<Button-1>", lambda e, x=r, y=c: self.left_click_with_capture(x, y))
                btn.bind("<Button-3>", lambda e, x=r, y=c: self.right_click_with_capture(x, y))
                self.buttons[(r, c)] = btn

    def place_fgrades(self):
        self.fgrade_positions = set()
        while len(self.fgrade_positions) < self.fgrades:
            pos = (random.randint(0, self.rows-1), random.randint(0, self.cols-1))
            self.fgrade_positions.add(pos)

        self.flags = set()
        self.revealed = set()
        self.adjacent_counts = {}

        for r in range(self.rows):
            for c in range(self.cols):
                count = 0
                for nr in range(max(0, r-1), min(self.rows, r+2)):
                    for nc in range(max(0, c-1), min(self.cols, c+2)):
                        if (nr, nc) in self.fgrade_positions:
                            count += 1
                if (r, c) in self.fgrade_positions:
                    count -= 1
                self.adjacent_counts[(r, c)] = count

    def left_click_with_capture(self, r, c):
        self.capture_screen()
        self.left_click(r, c)

    def right_click_with_capture(self, r, c):
        self.capture_screen()
        self.right_click(r, c)

    def left_click(self, r, c):
        if not self.game_started:
            self.game_started = True
            self.start_timer()

        if (r, c) in self.flags:
            return
        if (r, c) in self.revealed:
            return

        if (r, c) in self.fgrade_positions:
            self.reveal_all()
            self.status_label.config(text="게임 오버! F학점을 밟았어요...")
            self.game_started = False
            self.timer_running = False
            pygame.mixer.music.stop()
            messagebox.showinfo("패배", "F학점을 밟았습니다! 게임 종료!")
            return

        self.reveal_cell(r, c)
        if self.check_win():
            self.status_label.config(text="축하합니다! F학점을 모두 피했어요!")
            self.game_started = False
            self.timer_running = False
            pygame.mixer.music.stop()
            messagebox.showinfo("승리", "모든 안전한 칸을 열었어요! 승리!")
            return

    def right_click(self, r, c):
        if not self.game_started:
            return
        if (r, c) in self.revealed:
            return

        btn = self.buttons[(r, c)]
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            btn.config(text="")
            self.flags_left += 1
        else:
            if self.flags_left == 0:
                return
            self.flags.add((r, c))
            btn.config(text="F", fg="red")
            self.flags_left -= 1
        self.flags_label.config(text=f"남은 F학점: {self.flags_left}")

    def reveal_cell(self, r, c):
        if (r, c) in self.revealed or (r, c) in self.flags:
            return
        btn = self.buttons[(r, c)]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED)
        count = self.adjacent_counts[(r, c)]
        if count > 0:
            btn.config(text=str(count), fg="blue")
        else:
            btn.config(text="")
            # 빈칸이면 주변도 자동으로 오픈
            for nr in range(max(0, r-1), min(self.rows, r+2)):
                for nc in range(max(0, c-1), min(self.cols, c+2)):
                    if (nr, nc) != (r, c):
                        self.reveal_cell(nr, nc)
        self.revealed.add((r, c))

    def reveal_all(self):
        for pos in self.fgrade_positions:
            btn = self.buttons[pos]
            btn.config(text="F", fg="red", relief=tk.SUNKEN, state=tk.DISABLED)

    def check_win(self):
        return len(self.revealed) == self.rows * self.cols - self.fgrades

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        threading.Thread(target=self.update_timer, daemon=True).start()

    def update_timer(self):
        while self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"시간: {self.elapsed_time}초")
            time.sleep(1)

    def restart_game(self):
        self.timer_running = False
        self.game_started = False
        self.flags_left = self.fgrades
        self.flags_label.config(text=f"남은 F학점: {self.flags_left}")
        self.timer_label.config(text="시간: 0초")
        self.status_label.config(text="")
        self.screenshot_images.clear()
        pygame.mixer.music.play(-1)

        for btn in self.buttons.values():
            btn.destroy()
        self.board_frame.destroy()

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.create_board()
        self.place_fgrades()

    def capture_screen(self):
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        self.screenshot_images.append(screenshot)

    def save_gif(self):
        if not self.screenshot_images:
            messagebox.showinfo("알림", "캡처된 화면이 없습니다.")
            return
        gif_path = "gameplay.gif"
        frames = [img.convert("RGB") for img in self.screenshot_images]
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=500, loop=0)
        messagebox.showinfo("완료", f"게임 플레이 GIF가 '{gif_path}'로 저장되었습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    game = FGradeFinder(root)
    root.mainloop()
