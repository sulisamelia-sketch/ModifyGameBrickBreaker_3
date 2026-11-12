import tkinter as tk
import random

class GameObject:
    """Parent Class untuk semua objek di dalam Canvas (OOP: Inheritance)"""
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class BackgroundStar(GameObject):
    """Kelas untuk Bintang/Partikel Latar Belakang yang Berjalan Terus ke Bawah"""
    def __init__(self, canvas, x, y, speed, size):
        self.speed = speed
        item = canvas.create_oval(x, y, x + size, y + size, fill="#E0F7FA", outline="")
        super().__init__(canvas, item)

    def update(self, height):
        self.move(0, self.speed)
        coords = self.get_position()
        # Jika keluar layar bawah, pindahkan kembali ke atas secara acak
        if coords[1] > height:
            self.canvas.coords(self.item, coords[0], -10, coords[0] + (coords[2]-coords[0]), -10 + (coords[3]-coords[1]))


class Ball(GameObject):
    """Child Class Bola"""
    def __init__(self, canvas, x, y, speed=5):
        self.radius = 9
        self.direction = [random.choice([-1, 1]), -1]
        self.speed = speed
        item = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill="#FF80AB", outline="#FFFFFF", width=2
        )
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)


class Paddle(GameObject):
    """Child Class Papan Pemantul"""
    def __init__(self, canvas, x, y):
        self.width = 110
        self.height = 15
        item = canvas.create_rectangle(
            x - self.width / 2, y - self.height / 2,
            x + self.width / 2, y + self.height / 2,
            fill="#4DD0E1", outline="#FFFFFF", width=2
        )
        super().__init__(canvas, item)

    def move(self, offset, max_width):
        coords = self.get_position()
        if coords[0] + offset >= 0 and coords[2] + offset <= max_width:
            super().move(offset, 0)

    def expand(self):
        coords = self.get_position()
        if (coords[2] - coords[0]) < 170:
            self.canvas.coords(self.item, coords[0] - 15, coords[1], coords[2] + 15, coords[3])


class Brick(GameObject):
    """Child Class Balok Multi-Hit dengan Nuansa Petualangan"""
    COLORS = {1: "#80DEEA", 2: "#F48FB1", 3: "#CE93D8"}

    def __init__(self, canvas, x, y, hits, callback):
        self.width = 75
        self.height = 24
        self.hits = hits
        self.max_hits = hits
        self.callback = callback
        item = canvas.create_rectangle(
            x - self.width / 2, y - self.height / 2,
            x + self.width / 2, y + self.height / 2,
            fill=Brick.COLORS[hits], outline="#0D1B2A", width=1, tags="brick"
        )
        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            coords = self.get_position()
            self.delete()
            if self.callback:
                self.callback(self.max_hits * 10, (coords[0] + coords[2]) / 2, coords[3])
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])


class PowerUp(GameObject):
    """Item Bonus Unik yang Jatuh"""
    def __init__(self, canvas, x, y, kind):
        self.kind = kind
        colors = {"multi": "#FFD54F", "life": "#81C784", "laser": "#FF4081"}
        item = canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill=colors[kind], outline="white", width=2)
        super().__init__(canvas, item)

    def update(self):
        self.move(0, 3.5)


class Laser(GameObject):
    """Peluru Laser yang ditembakkan Paddle"""
    def __init__(self, canvas, x, y):
        item = canvas.create_rectangle(x - 2, y - 10, x + 2, y, fill="#FF4081", outline="")
        super().__init__(canvas, item)

    def update(self):
        self.move(0, -7)


class Game(tk.Frame):
    """Kelas Utama Game dengan Latar Belakang Berjalan (Parallax Background)"""
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3
        self.score = 0
        self.level = 1
        self.width = 640
        self.height = 480
        self.is_running = False
        self.game_over_state = False
        self.has_laser = False

        # Background warna malam petualangan luar angkasa / dunia fantasi gelap
        self.canvas = tk.Canvas(self, bg="#0B132B", width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.background_stars = []
        self.setup_background_stars()

        self.items = {}
        self.balls = []
        self.powerups = []
        self.lasers = []
        self.paddle = Paddle(self.canvas, self.width / 2, 430)
        
        self.hud = None
        self.text = None
        self.avatar_face = None
        self.avatar_text = None

        self.setup_ui_elements()
        self.setup_level()

        self.canvas.focus_set()
        self.canvas.bind("<Left>", lambda _: self.paddle.move(-30, self.width))
        self.canvas.bind("<Right>", lambda _: self.paddle.move(30, self.width))
        self.canvas.bind("<Up>", lambda _: self.shoot_laser() if self.has_laser else None)
        self.canvas.bind("<space>", lambda _: self.start_game())
        self.canvas.bind("r", lambda _: self.restart_game())
        self.canvas.bind("R", lambda _: self.restart_game())

    def setup_background_stars(self):
        # Membuat partikel bintang latar belakang yang berjalan (efek seperti jalan di Genshin/game penjelajahan)
        for _ in range(35):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            speed = random.uniform(0.5, 2.0)
            size = random.randint(2, 4)
            star = BackgroundStar(self.canvas, x, y, speed, size)
            self.background_stars.append(star)

    def setup_ui_elements(self):
        self.canvas.create_rectangle(525, 10, 630, 55, fill="#1C2541", outline="#4DD0E1", width=2)
        self.avatar_face = self.canvas.create_text(555, 32, text="(>_<)", fill="#F48FB1", font=("Consolas", 14, "bold"))
        self.avatar_text = self.canvas.create_text(595, 32, text="Ready", fill="#4DD0E1", font=("Consolas", 9, "bold"))

    def set_avatar(self, face, status, color):
        self.canvas.itemconfig(self.avatar_face, text=face)
        self.canvas.itemconfig(self.avatar_text, text=status, fill=color)

    def setup_level(self):
        self.clear_objects()
        
        ball = Ball(self.canvas, self.width / 2, 410, speed=4.5 + (self.level * 0.6))
        self.balls.append(ball)

        rows = min(2 + self.level, 5)
        for row in range(rows):
            hits = max(1, 3 - row)
            for col in range(7):
                x = col * 78 + 55
                y = row * 30 + 70
                brick = Brick(self.canvas, x, y, hits, self.on_brick_destroyed)
                self.items[brick.item] = brick

        self.update_hud()
        self.show_message(f"LEVEL {self.level}\nTekan [SPASI] untuk Mulai", "#4DD0E1")
        self.set_avatar("(^o^)", "Travel", "#FFD54F")

    def clear_objects(self):
        for b in self.balls:
            b.delete()
        self.balls.clear()
        for item_id in list(self.items.keys()):
            if isinstance(self.items[item_id], Brick):
                self.items[item_id].delete()
                del self.items[item_id]

    def on_brick_destroyed(self, points, x, y):
        self.score += points
        self.update_hud()
        self.set_avatar("(>.<)", "Nice!", "#81C784")
        
        if random.random() < 0.30:
            kind = random.choice(["multi", "life", "laser"])
            pu = PowerUp(self.canvas, x, y, kind)
            self.powerups.append(pu)

    def shoot_laser(self):
        p_coords = self.paddle.get_position()
        center_x = (p_coords[0] + p_coords[2]) / 2
        laser = Laser(self.canvas, center_x, p_coords[1])
        self.lasers.append(laser)

    def update_hud(self):
        text = f"Nyawa: {self.lives}  |  Skor: {self.score}  |  Level: {self.level}"
        if self.hud is None:
            self.hud = self.canvas.create_text(180, 25, text=text, fill="#F48FB1", font=("Consolas", 10, "bold"))
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def show_message(self, msg, color="#F48FB1"):
        if self.text is not None:
            self.canvas.delete(self.text)
        self.text = self.canvas.create_text(
            self.width / 2, self.height / 2 + 20,
            text=msg, fill=color, font=("Consolas", 14, "bold"), justify="center"
        )

    def start_game(self):
        if not self.is_running and not self.game_over_state:
            self.is_running = True
            if self.text is not None:
                self.canvas.delete(self.text)
                self.text = None
            self.game_loop()

    def restart_game(self):
        if self.game_over_state:
            self.canvas.delete("all")
            self.lives = 3
            self.score = 0
            self.level = 1
            self.items.clear()
            self.powerups.clear()
            self.lasers.clear()
            self.hud = None
            self.text = None
            self.game_over_state = False
            self.has_laser = False
            self.setup_background_stars()
            self.setup_ui_elements()
            self.paddle = Paddle(self.canvas, self.width / 2, 430)
            self.setup_level()

    def game_loop(self):
        # 1. Update Latar Belakang Berjalan (Parallax Background Effect)
        for star in self.background_stars:
            star.update(self.height)

        if not self.is_running:
            self.after(16, self.game_loop)
            return

        # Update Bola
        for ball in list(self.balls):
            ball.update()
            b_coords = ball.get_position()
            p_coords = self.paddle.get_position()

            if not (b_coords[2] < p_coords[0] or b_coords[0] > p_coords[2] or 
                    b_coords[3] < p_coords[1] or b_coords[1] > p_coords[3]) and ball.direction[1] > 0:
                ball.direction[1] *= -1

            overlap_items = self.canvas.find_overlapping(*b_coords)
            for item_id in overlap_items:
                if item_id in self.items and isinstance(self.items[item_id], Brick):
                    self.items[item_id].hit()
                    ball.direction[1] *= -1
                    break

            if b_coords[3] >= self.height:
                ball.delete()
                self.balls.remove(ball)

        # Update Laser
        for laser in list(self.lasers):
            laser.update()
            l_coords = laser.get_position()
            if l_coords[1] <= 0:
                laser.delete()
                self.lasers.remove(laser)
                continue
            
            overlap_items = self.canvas.find_overlapping(*l_coords)
            hit_brick = False
            for item_id in overlap_items:
                if item_id in self.items and isinstance(self.items[item_id], Brick):
                    self.items[item_id].hit()
                    hit_brick = True
                    break
            if hit_brick:
                laser.delete()
                self.lasers.remove(laser)

        # Update Power-ups
        p_coords = self.paddle.get_position()
        for pu in list(self.powerups):
            pu.update()
            pu_coords = pu.get_position()
            if not (pu_coords[2] < p_coords[0] or pu_coords[0] > p_coords[2] or
                    pu_coords[3] < p_coords[1] or pu_coords[1] > p_coords[3]):
                if pu.kind == "multi":
                    if len(self.balls) > 0:
                        b_ref = self.balls[0]
                        bx, by = b_ref.get_position()[:2]
                        new_ball = Ball(self.canvas, bx, by, speed=b_ref.speed)
                        new_ball.direction = [-b_ref.direction[0], -b_ref.direction[1]]
                        self.balls.append(new_ball)
                elif pu.kind == "life":
                    self.lives += 1
                elif pu.kind == "laser":
                    self.has_laser = True
                    self.paddle.expand()
                
                self.update_hud()
                pu.delete()
                self.powerups.remove(pu)
            elif pu_coords[1] > self.height:
                pu.delete()
                self.powerups.remove(pu)

        # Cek Kondisi Game Over atau Naik Level
        num_bricks = len([i for i in self.items.values() if isinstance(i, Brick)])
        if num_bricks == 0:
            self.is_running = False
            self.level += 1
            self.setup_level()
        elif len(self.balls) == 0:
            self.lives -= 1
            self.update_hud()
            self.set_avatar("(;_;)", "Ouch!", "#FF4081")
            self.is_running = False
            if self.lives <= 0:
                self.game_over_state = True
                self.show_message(f"GAME OVER\nSkor Akhir: {self.score}\nTekan [R] untuk Restart", "#F48FB1")
            else:
                self.has_laser = False
                ball = Ball(self.canvas, self.width / 2, 410, speed=4.5 + (self.level * 0.6))
                self.balls.append(ball)
                self.show_message("Nyawa Berkurang!\nTekan [SPASI] untuk Lanjut", "#4DD0E1")
        else:
            self.after(16, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ModifyGameBrickBreaker_3 - Moving Background Edition")
    root.resizable(False, False)
    game = Game(root)
    game.mainloop()