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

   