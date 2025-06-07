# dimethyltryptamine GDI payload <3

import sys
import ctypes
import time
import random
import math
import colorsys
import threading
import numpy as np
import winsound
from ctypes import windll, byref, Structure, c_long, c_void_p, c_int, POINTER, c_wchar_p, c_uint32, c_int32, c_uint16
from ctypes.wintypes import RECT, DWORD, HWND, UINT, BOOL, WORD, LONG, POINT, HDC, HBITMAP, HPEN, HBRUSH
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtMultimedia import QSound

if sys.maxsize > 2**32:
    LPARAM = ctypes.c_longlong
    WPARAM = ctypes.c_ulonglong
    LRESULT = ctypes.c_longlong
else:
    LPARAM = ctypes.c_long
    WPARAM = ctypes.c_uint
    LRESULT = ctypes.c_long

HINSTANCE = HWND
HICON = HWND
HCURSOR = HWND

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
msimg32 = ctypes.WinDLL('msimg32')

WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
IDC_ARROW = 32512
WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_KEYDOWN = 0x0100
WM_CLOSE = 0x0010
WM_COMMAND = 0x0111
VK_ESCAPE = 0x1B
VK_F4 = 0x73
SW_SHOW = 5
BLACK_BRUSH = 4
SRCCOPY = 0x00CC0020
MB_OK = 0x0
MB_ICONERROR = 0x10
MB_TOPMOST = 0x40000
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

class BITMAPINFOHEADER(Structure):
    _fields_ = [
        ("biSize", c_uint32),
        ("biWidth", c_int32),
        ("biHeight", c_int32),
        ("biPlanes", c_uint16),
        ("biBitCount", c_uint16),
        ("biCompression", c_uint32),
        ("biSizeImage", c_uint32),
        ("biXPelsPerMeter", c_int32),
        ("biYPelsPerMeter", c_int32),
        ("biClrUsed", c_uint32),
        ("biClrImportant", c_uint32)
    ]

class BITMAPINFO(Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", c_void_p)
    ]

class PAINTSTRUCT(Structure):
    _fields_ = [("hdc", HDC),
                ("fErase", BOOL),
                ("rcPaint", RECT),
                ("fRestore", BOOL),
                ("fIncUpdate", BOOL),
                ("rgbReserved", ctypes.c_char * 32)]

class MSG(Structure):
    _fields_ = [("hwnd", HWND),
                ("message", UINT),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
                ("time", DWORD),
                ("pt", POINT)]

class Particle:
    def __init__(self, x, y, vx, vy, life, color_shift, ptype="normal"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color_shift = color_shift
        self.size = random.uniform(2, 12)
        self.ptype = ptype
        self.rotation = random.uniform(0, 2 * math.pi)
        self.mass = self.size * 0.5
        self.charge = random.choice([-1, 1]) * random.uniform(0.5, 2.0)

class Sphere3D:
    def __init__(self, x, y, z, vx, vy, vz, radius, life):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.radius = radius
        self.life = life
        self.max_life = life
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rot_speed = random.uniform(-0.2, 0.2)

class MeltColumn:
    def __init__(self, x):
        self.x = x
        self.pixels = []
        self.melt_speed = random.uniform(1, 4)
        self.heat = 0

class Vortex:
    def __init__(self, x, y, strength, radius):
        self.x = x
        self.y = y
        self.strength = strength
        self.radius = radius
        self.rotation = 0
        self.life = random.randint(200, 400)

class LightningBolt:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.points = self.generate_bolt(start_x, start_y, end_x, end_y)
        self.life = 30
        self.max_life = 30
        self.branches = []
        
    def generate_bolt(self, x1, y1, x2, y2, detail=5):
        if detail == 0:
            return [(x1, y1), (x2, y2)]
        
        mid_x = (x1 + x2) / 2 + random.randint(-50, 50)
        mid_y = (y1 + y2) / 2 + random.randint(-50, 50)
        
        points = []
        points.extend(self.generate_bolt(x1, y1, mid_x, mid_y, detail - 1))
        points.extend(self.generate_bolt(mid_x, mid_y, x2, y2, detail - 1))
        
        if detail > 2 and random.random() < 0.3:
            branch_x = mid_x + random.randint(-100, 100)
            branch_y = mid_y + random.randint(-100, 100)
            self.branches.append(self.generate_bolt(mid_x, mid_y, branch_x, branch_y, detail - 2))
        
        return points

class Metaball:
    def __init__(self, x, y, vx, vy, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.life = random.randint(100, 300)

class SpringConstraint:
    def __init__(self, p1, p2, rest_length, strength):
        self.p1 = p1
        self.p2 = p2
        self.rest_length = rest_length
        self.strength = strength

class SoundThread(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.sound_types = ['beep', 'explosion', 'laser', 'glitch', 'alarm']
        
    def run(self):
        while self.running:
            sound_type = random.choice(self.sound_types)
            
            if sound_type == 'beep':
                for _ in range(random.randint(1, 3)):
                    winsound.Beep(random.randint(200, 2000), random.randint(50, 200))
                    time.sleep(random.uniform(0.05, 0.2))
            elif sound_type == 'explosion':
                for freq in range(1000, 100, -50):
                    winsound.Beep(freq, 20)
            elif sound_type == 'laser':
                for freq in range(500, 2000, 100):
                    winsound.Beep(freq, 10)
            elif sound_type == 'glitch':
                for _ in range(random.randint(5, 15)):
                    winsound.Beep(random.randint(100, 4000), random.randint(10, 50))
            elif sound_type == 'alarm':
                for _ in range(3):
                    winsound.Beep(800, 200)
                    time.sleep(0.1)
                    winsound.Beep(1200, 200)
                    time.sleep(0.1)
            
            time.sleep(random.uniform(0.5, 3.0))
    
    def stop(self):
        self.running = False

class EffectsThread(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.width = user32.GetSystemMetrics(0)
        self.height = user32.GetSystemMetrics(1)
        self.particles = []
        self.spheres_3d = []
        self.melt_columns = []
        self.plasma_time = 0
        self.tunnel_rotation = 0
        self.shockwave_effects = []
        self.screen_shake = {'x': 0, 'y': 0, 'intensity': 0}
        self.collapse_effect = {'active': False, 'progress': 0, 'center_x': 0, 'center_y': 0}
        self.desktop_dc = None
        self.pixel_buffer = {}
        self.vortices = []
        self.lightning_bolts = []
        self.metaballs = []
        self.reaction_diffusion = [[0.0 for _ in range(self.width//4)] for _ in range(self.height//4)]
        self.reaction_diffusion_b = [[0.0 for _ in range(self.width//4)] for _ in range(self.height//4)]
        self.particle_springs = []
        self.chromatic_offset = 0
        self.fractal_zoom = 1.0
        self.fractal_offset_x = 0
        self.fractal_offset_y = 0
        self.pixel_sort_regions = []
        self.z_buffer_corruption = 0
        self.error_messages = [
            "System32.dll corrupted!",
            "Fatal error: Memory overflow.",
            "Unknown error at 0x004FF21.",
            "Registry access denied.",
            "Critical system failure!",
            "Error: Access Violation.",
            "Exception: STACK_OVERFLOW",
            "Alert: SYSTEM MALFUNCTION",
            "Fatal exception occurred!",
            "ERROR: 0x0000007B",
        ]
        self.shooting_star_active = False
        self.shooting_star_particles = []
        self.shooting_star_speed = 50
        self.shooting_star_frequency = 1
        self.shooting_star_colors = [(0, 0, 255), (255, 0, 0), (255, 255, 0)]
        self.grid_size = 100
        self.diffusion = 0.00001
        self.viscosity = 0.00001
        self.time_step = 0.1
        self.turbulence_strength = 0.1
        self.force_strength = 5.0
        self.gravity = 0.98
        self.particle_count = 8000
        self.density = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        self.velocity_x = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        self.velocity_y = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        self.fluid_particles = np.zeros((self.particle_count, 4), dtype=np.float32)
        self.fluid_particles[:, 0] = np.random.uniform(0, self.width - 1, self.particle_count)
        self.fluid_particles[:, 1] = np.random.uniform(0, self.height - 1, self.particle_count)
        self.fluid_particles[:, 2] = np.random.uniform(-1, 1, self.particle_count) * 0.5
        self.fluid_particles[:, 3] = np.random.uniform(-1, 1, self.particle_count) * 0.5
        self.color_palette = np.array([
            (66, 30, 15), (25, 7, 26), (9, 1, 47), (4, 4, 73), (0, 7, 100),
            (12, 44, 138), (24, 82, 177), (57, 125, 209), (134, 181, 229),
            (211, 236, 248), (241, 233, 191), (248, 201, 95), (255, 170, 0),
            (204, 128, 0), (153, 87, 0), (106, 52, 3),
        ], dtype=np.uint8)
        
        for i in range(0, self.width, 2):
            self.melt_columns.append(MeltColumn(i))
        
        for y in range(len(self.reaction_diffusion)):
            for x in range(len(self.reaction_diffusion[0])):
                if random.random() < 0.1:
                    self.reaction_diffusion[y][x] = 1.0
                    self.reaction_diffusion_b[y][x] = 1.0
    
    def get_desktop_dc(self):
        try:
            desktop_hwnd = user32.GetDesktopWindow()
            hdc = user32.GetDC(None)
            return hdc
        except Exception:
            return None
    
    def get_rainbow_color(self, alpha=255, hue_shift=0.0, saturation=1.0, brightness=1.0):
        hue = (time.time() * 0.8 + hue_shift) % 1.0
        r, g, b = [int(c * 255 * brightness) for c in colorsys.hsv_to_rgb(hue, saturation, 1.0)]
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return (r << 16) | (g << 8) | b
    
    def get_transparent_color(self, alpha, hue_shift=0.0):
        hue = (time.time() * 0.03 + hue_shift) % 1.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
        return (alpha << 24) | (r << 16) | (g << 8) | b
    
    def hsv_to_rgb_int(self, h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(b * 255) | (int(g * 255) << 8) | (int(r * 255) << 16)
    
    def project_3d_point(self, x, y, z, distance=400):
        if z <= -distance:
            z = -distance + 1
        screen_x = int((x * distance) / (distance + z)) + self.width // 2
        screen_y = int((y * distance) / (distance + z)) + self.height // 2
        return screen_x, screen_y
    
    def draw_transparent_blocks(self, hdc, duration, block_size=100, alpha=128):
        start_time = time.time()
        while time.time() - start_time < duration:
            color = random.choice([0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0xFFFFFF])
            r, g, b = (color & 0xFF), (color >> 8) & 0xFF, (color >> 16) & 0xFF
            blend_color = (r // 2, g // 2, b // 2)
            blend_brush = gdi32.CreateSolidBrush((blend_color[2] << 16) | (blend_color[1] << 8) | blend_color[0])
            x = random.randint(0, self.width - block_size)
            y = random.randint(0, self.height - block_size)
            gdi32.SelectObject(hdc, blend_brush)
            gdi32.PatBlt(hdc, x, y, block_size, block_size, 0x00FB00F0)
            gdi32.DeleteObject(blend_brush)
    
    def shift_screen_quadrants(self, hdc):
        half_width = self.width // 2
        half_height = self.height // 2
        for shift in range(0, max(half_width, half_height), 10):
            gdi32.BitBlt(hdc, 0, 0, half_width, half_height, hdc, -shift, -shift, 0x00CC0020)
            gdi32.BitBlt(hdc, half_width, 0, half_width, half_height, hdc, half_width + shift, -shift, 0x00CC0020)
            gdi32.BitBlt(hdc, 0, half_height, half_width, half_height, hdc, -shift, half_height + shift, 0x00CC0020)
            gdi32.BitBlt(hdc, half_width, half_height, half_width, half_height, hdc, half_width + shift, half_height + shift, 0x00CC0020)
            time.sleep(0.01)
    
    def fog_effect(self, hdc_mem):
        overlay_color = self.get_transparent_color(alpha=int(255 * 0.7))
        overlay_brush = gdi32.CreateSolidBrush(overlay_color)
        gdi32.SelectObject(hdc_mem, overlay_brush)
        gdi32.PatBlt(hdc_mem, 0, 0, self.width, self.height, 0x00FA0089)
        gdi32.DeleteObject(overlay_brush)
    
    def burn_effect(self, hdc_mem):
        burn_color = self.get_transparent_color(alpha=int(255 * 0.85), hue_shift=0.1)
        burn_brush = gdi32.CreateSolidBrush(burn_color)
        gdi32.SelectObject(hdc_mem, burn_brush)
        gdi32.PatBlt(hdc_mem, 0, 0, self.width, self.height, 0x005A0044)
        gdi32.DeleteObject(burn_brush)
    
    def kaleidoscope_effect(self, hdc_mem):
        tile_size = min(self.width, self.height) // 4
        for x in range(0, self.width, tile_size):
            for y in range(0, self.height, tile_size):
                angle = math.pi / 4 * ((x + y) % 4)
                dest_points = (POINT * 3)(
                    POINT(x + int(tile_size * math.cos(angle)), y + int(tile_size * math.sin(angle))),
                    POINT(x + int(tile_size * math.sin(angle)), y + int(tile_size * -math.cos(angle))),
                    POINT(x - int(tile_size * math.sin(angle)), y + int(tile_size * math.cos(angle)))
                )
                gdi32.PlgBlt(self.desktop_dc, dest_points, hdc_mem, x, y, tile_size, tile_size, 0, 0, 0)
    
    def wave_warp_effect(self, hdc_mem):
        wave_intensity = 8
        wave_frequency = 0.1
        for y in range(0, self.height, wave_intensity):
            offset = int(wave_intensity * math.sin(time.time() * wave_frequency + y * wave_frequency))
            gdi32.BitBlt(self.desktop_dc, offset, y, self.width, wave_intensity, hdc_mem, 0, y, 0x00CC0020)
    
    def jitter_effect(self, hdc_mem):
        jitter_x = random.randint(-5, 5)
        jitter_y = random.randint(-5, 5)
        gdi32.BitBlt(self.desktop_dc, jitter_x, jitter_y, self.width, self.height, hdc_mem, 0, 0, 0x00CC0020)
    
    def spherical_distortion(self, x, y, intensity=2.0):
        center_x, center_y = self.width // 2, self.height // 2
        dx, dy = x - center_x, y - center_y
        distance = math.sqrt(dx**2 + dy**2)
        max_dist = math.sqrt(center_x**2 + center_y**2)
        distort_factor = intensity * (0.5 + 0.5 * math.cos(distance / max_dist * math.pi))
        warped_x = int(center_x + dx * distort_factor)
        warped_y = int(center_y + dy * distort_factor)
        return warped_x, warped_y
    
    def apply_psychedelic_spherical_effect(self, hdc):
        hdc_mem = gdi32.CreateCompatibleDC(hdc)
        hbm_mem = gdi32.CreateCompatibleBitmap(hdc, self.width, self.height)
        gdi32.SelectObject(hdc_mem, hbm_mem)
        gdi32.BitBlt(hdc_mem, 0, 0, self.width, self.height, hdc, 0, 0, 0x00CC0020)
        
        pulse_alpha = 180 + int(75 * (0.5 + 0.5 * math.sin(time.time() * 8.0)))
        overlay_color = self.get_transparent_color(alpha=pulse_alpha)
        
        for y in range(0, self.height, 15):
            for x in range(0, self.width, 15):
                warped_x, warped_y = self.spherical_distortion(x, y, intensity=2.0)
                final_x = warped_x + random.randint(-20, 20)
                final_y = warped_y + random.randint(-20, 20)
                gdi32.BitBlt(hdc, final_x, final_y, 15, 15, hdc_mem, x, y, 0x00CC0020)
        
        brush = gdi32.CreateSolidBrush(overlay_color)
        gdi32.SelectObject(hdc, brush)
        msimg32.AlphaBlend(hdc, 0, 0, self.width, self.height, hdc_mem, 0, 0, self.width, self.height, overlay_color)
        
        gdi32.DeleteObject(hbm_mem)
        gdi32.DeleteDC(hdc_mem)
    
    def simulate_fluid(self):
        velocity_x_new = self.velocity_x.copy()
        velocity_y_new = self.velocity_y.copy()
        density_new = self.density.copy()

        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                vx_update = self.viscosity * (
                    (self.velocity_x[i+1, j] + self.velocity_x[i-1, j] + self.velocity_x[i, j+1] + self.velocity_x[i, j-1] - 4 * self.velocity_x[i, j])
                    * self.time_step
                ) + self.force_strength * math.sin(j * self.turbulence_strength) + self.gravity * self.time_step
                
                vy_update = self.viscosity * (
                    (self.velocity_y[i+1, j] + self.velocity_y[i-1, j] + self.velocity_y[i, j+1] + self.velocity_y[i, j-1] - 4 * self.velocity_y[i, j])
                    * self.time_step
                ) + self.force_strength * math.cos(i * self.turbulence_strength) + self.gravity * self.time_step
                
                velocity_x_new[i, j] += vx_update
                velocity_y_new[i, j] += vy_update

                density_new[i, j] = self.density[i, j] + self.diffusion * (
                    (self.density[i+1, j] + self.density[i-1, j] + self.density[i, j+1] + self.density[i, j-1] - 4 * self.density[i, j])
                    * self.time_step
                )
        
        np.copyto(self.velocity_x, velocity_x_new)
        np.copyto(self.velocity_y, velocity_y_new)
        np.copyto(self.density, density_new)

        gx = np.clip((self.fluid_particles[:, 0] * self.grid_size / self.width).astype(int), 0, self.grid_size - 1)
        gy = np.clip((self.fluid_particles[:, 1] * self.grid_size / self.height).astype(int), 0, self.grid_size - 1)

        self.fluid_particles[:, 2] += self.velocity_x[gx, gy]
        self.fluid_particles[:, 3] += self.velocity_y[gx, gy]
        self.fluid_particles[:, 0] += self.fluid_particles[:, 2]
        self.fluid_particles[:, 1] += self.fluid_particles[:, 3]

        self.fluid_particles[:, 0] %= self.width
        self.fluid_particles[:, 1] %= self.height
    
    def create_shooting_star(self):
        angle = np.random.uniform(0, 2 * np.pi)
        radius = 10
        num_particles = 100

        if np.random.rand() < 0.5:
            x_start = -radius if np.random.rand() < 0.5 else self.width + radius
            y_start = np.random.uniform(0, self.height)
        else:
            y_start = -radius if np.random.rand() < 0.5 else self.height + radius
            x_start = np.random.uniform(0, self.width)

        x_start = np.clip(x_start, 0, self.width)
        y_start = np.clip(y_start, 0, self.height)

        particles = np.zeros((num_particles, 4), dtype=np.float32)
        particles[:, 0] = x_start
        particles[:, 1] = y_start
        particles[:, 2] = np.cos(angle) * self.shooting_star_speed
        particles[:, 3] = np.sin(angle) * self.shooting_star_speed

        color = random.choice(self.shooting_star_colors)
        decay_rate = np.random.uniform(0.01, 0.05)
        tail_length = np.random.uniform(50, 200)
        
        speed_multiplier = 1.5
        vx = np.cos(angle) * self.shooting_star_speed * speed_multiplier
        vy = np.sin(angle) * self.shooting_star_speed * speed_multiplier

        self.shooting_star_particles.append({
            'particles': particles,
            'vx': vx,
            'vy': vy,
            'color': color,
            'origin_x': x_start,
            'origin_y': y_start,
            'decay_rate': decay_rate,
            'tail_length': tail_length
        })
    
    def simulate_shooting_stars(self):
        new_shooting_star_particles = []

        for star in self.shooting_star_particles:
            if not all(k in star for k in ['particles', 'vx', 'vy', 'color', 'origin_x', 'origin_y', 'decay_rate', 'tail_length']):
                continue

            particles = star['particles']
            vx = star['vx']
            vy = star['vy']
            decay_rate = star['decay_rate']
            tail_length = star['tail_length']

            particles[:, 0] += vx
            particles[:, 1] += vy

            distance_traveled = np.sqrt((particles[:, 0] - star['origin_x'])**2 + 
                                        (particles[:, 1] - star['origin_y'])**2)
            brightness = np.maximum(0, 1 - distance_traveled / tail_length)
            sizes = np.clip(np.linspace(1, 0, len(particles)), 0.5, 1) * (brightness ** 0.5)
            
            particles[:, 3] *= (1 - decay_rate)
            
            within_screen = (particles[:, 0] >= 0) & (particles[:, 0] < self.width) & \
                            (particles[:, 1] >= 0) & (particles[:, 1] < self.height) & \
                            (particles[:, 3] > 0.1)
            star['particles'] = particles[within_screen]
            
            if len(star['particles']) > 0:
                new_shooting_star_particles.append(star)

        self.shooting_star_particles = new_shooting_star_particles
    
    def draw_particles_fluid(self, hdc):
        bmi = BITMAPINFO()
        bmi.bmiHeader = BITMAPINFOHEADER()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = self.width
        bmi.bmiHeader.biHeight = -self.height
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0
        bmi.bmiHeader.biSizeImage = 0
        bmi.bmiHeader.biXPelsPerMeter = 0
        bmi.bmiHeader.biYPelsPerMeter = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0
        
        buffer = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        buffer = (buffer * 0.9).astype(np.uint8)

        gx = np.clip((self.fluid_particles[:, 0] * self.grid_size / self.width).astype(int), 0, self.grid_size - 1)
        gy = np.clip((self.fluid_particles[:, 1] * self.grid_size / self.height).astype(int), 0, self.grid_size - 1)

        density_values = self.density[gx, gy]
        color_indices = np.clip((density_values * (len(self.color_palette) - 1)).astype(int), 0, len(self.color_palette) - 1)
        colors = self.color_palette[color_indices]

        for i in range(self.particle_count):
            x, y = int(self.fluid_particles[i, 0]), int(self.fluid_particles[i, 1])
            if 0 <= x < self.width and 0 <= y < self.height:
                r, g, b = colors[i]
                buffer[y, x] = (b, g, r, 255)

        for star in self.shooting_star_particles:
            for particle in star['particles']:
                x, y = int(particle[0]), int(particle[1])
                if 0 <= x < self.width and 0 <= y < self.height:
                    buffer[y, x] = (*star['color'], 255)

        gdi32.SetDIBitsToDevice(hdc, 0, 0, self.width, self.height, 0, 0, 0, self.height, buffer.ctypes.data, byref(bmi), 0)
    
    def add_initial_conditions(self):
        x = np.random.randint(10, self.grid_size-10, 2000)
        y = np.random.randint(10, self.grid_size-10, 2000)
        self.density[x, y] += np.random.random(2000) * 10
        self.velocity_x[x, y] += np.random.random(2000) * 2 - 1
        self.velocity_y[x, y] += np.random.random(2000) * 2 - 1
    
    def draw_xor_fractal_with_color_cycle(self, hdc, x_start, y_start, width, height, max_iterations, color_shift):
        for y in range(height):
            for x in range(width):
                value = (x ^ y) % max_iterations
                hue = (value / max_iterations + color_shift) % 1.0
                color = self.hsv_to_rgb_int(hue, 1.0, 1.0)
                gdi32.SetPixel(hdc, x_start + x, y_start + y, color)
    
    def spectrum_cycle_effects(self, hdc, color_shift):
        for _ in range(random.randint(3, 7)):
            fractal_size = random.randint(50, 200)
            x_start = random.randint(0, self.width - fractal_size)
            y_start = random.randint(0, self.height - fractal_size)
            max_iterations = random.randint(50, 300)
            self.draw_xor_fractal_with_color_cycle(hdc, x_start, y_start, fractal_size, fractal_size, max_iterations, color_shift)

        for _ in range(random.randint(5, 15)):
            src_x = random.randint(0, self.width)
            src_y = random.randint(0, self.height)
            dest_x = random.randint(0, self.width)
            dest_y = random.randint(0, self.height)
            block_size = random.randint(10, 100)
            gdi32.BitBlt(hdc, dest_x, dest_y, block_size, block_size, hdc, src_x, src_y, 0x00CC0020)
    
    def generate_triangle(self, center_x, center_y, size, angle):
        return [
            POINT(int(center_x + size * math.cos(angle)), int(center_y + size * math.sin(angle))),
            POINT(int(center_x + size * math.cos(angle + 2 * math.pi / 3)), int(center_y + size * math.sin(angle + 2 * math.pi / 3))),
            POINT(int(center_x + size * math.cos(angle + 4 * math.pi / 3)), int(center_y + size * math.sin(angle + 4 * math.pi / 3))),
        ]
    
    def draw_triangle(self, hdc, vertices, fill_color):
        fill_brush = gdi32.CreateSolidBrush(fill_color)
        gdi32.SelectObject(hdc, fill_brush)
        gdi32.BeginPath(hdc)
        gdi32.MoveToEx(hdc, vertices[0].x, vertices[0].y, None)
        gdi32.LineTo(hdc, vertices[1].x, vertices[1].y)
        gdi32.LineTo(hdc, vertices[2].x, vertices[2].y)
        gdi32.LineTo(hdc, vertices[0].x, vertices[0].y)
        gdi32.EndPath(hdc)
        gdi32.FillPath(hdc)
        gdi32.DeleteObject(fill_brush)
    
    def invert_square(self, hdc, center_x, center_y, size, rotation):
        half_size = size // 2
        vertices = [
            POINT(int(center_x + half_size * math.cos(rotation)), int(center_y + half_size * math.sin(rotation))),
            POINT(int(center_x + half_size * math.cos(rotation + math.pi / 2)), int(center_y + half_size * math.sin(rotation + math.pi / 2))),
            POINT(int(center_x + half_size * math.cos(rotation + math.pi)), int(center_y + half_size * math.sin(rotation + math.pi))),
            POINT(int(center_x + half_size * math.cos(rotation + 3 * math.pi / 2)), int(center_y + half_size * math.sin(rotation + 3 * math.pi / 2))),
        ]
        
        gdi32.BeginPath(hdc)
        gdi32.MoveToEx(hdc, vertices[0].x, vertices[0].y, None)
        for i in range(1, len(vertices)):
            gdi32.LineTo(hdc, vertices[i].x, vertices[i].y)
        gdi32.LineTo(hdc, vertices[0].x, vertices[0].y)
        gdi32.EndPath(hdc)
        gdi32.BitBlt(hdc, center_x - half_size, center_y - half_size, size, size, hdc, center_x - half_size, center_y - half_size, 0x00550009)
    
    def draw_wave(self, hdc, center_x, center_y, radius, thickness, color):
        pen = gdi32.CreatePen(0, thickness, color)
        gdi32.SelectObject(hdc, pen)
        gdi32.Ellipse(hdc, center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        gdi32.DeleteObject(pen)
    
    def show_chaotic_message(self):
        message = random.choice(self.error_messages)
        corrupted_message = "".join(
            random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()") 
            for _ in message
        )
        
        x = random.randint(0, self.width - 200)
        y = random.randint(0, self.height - 100)
        hwnd = user32.MessageBoxW(0, corrupted_message, "Error", MB_OK | MB_ICONERROR | MB_TOPMOST)
    
    def melt_screen(self, hdc):
        hdc_mem = gdi32.CreateCompatibleDC(hdc)
        hbm_mem = gdi32.CreateCompatibleBitmap(hdc, self.width, self.height)
        gdi32.SelectObject(hdc_mem, hbm_mem)
        gdi32.BitBlt(hdc_mem, 0, 0, self.width, self.height, hdc, 0, 0, 0x00CC0020)

        for _ in range(15):
            strip_y = random.randint(0, self.height - 30)
            strip_height = random.randint(5, 20)
            shift_down = random.randint(10, 40)
            dest_y = strip_y + shift_down
            if dest_y + strip_height > self.height:
                dest_y = self.height - strip_height
            gdi32.BitBlt(hdc, 0, dest_y, self.width, strip_height, hdc_mem, 0, strip_y, 0x00CC0020)

        for _ in range(10):
            strip_x = random.randint(0, self.width - 30)
            strip_width = random.randint(5, 15)
            shift_right = random.randint(10, 20)
            dest_x = strip_x + shift_right
            if dest_x + strip_width > self.width:
                dest_x = self.width - strip_width
            gdi32.BitBlt(hdc, dest_x, 0, strip_width, self.height, hdc_mem, strip_x, 0, 0x00CC0020)

        gdi32.DeleteObject(hbm_mem)
        gdi32.DeleteDC(hdc_mem)
    
    def explosive_cloning(self, hdc):
        hdc_mem = gdi32.CreateCompatibleDC(hdc)
        hbm_mem = gdi32.CreateCompatibleBitmap(hdc, self.width, self.height)
        gdi32.SelectObject(hdc_mem, hbm_mem)
        
        clone_size = 50
        growth_rate = 1.2
        half_width = self.width // 2
        half_height = self.height // 2
        
        for i in range(0, self.width, int(clone_size)):
            for j in range(0, self.height, int(clone_size)):
                src_x = random.choice([0, half_width])
                src_y = random.choice([0, half_height])
                gdi32.StretchBlt(hdc, i, j, int(clone_size), int(clone_size), hdc, src_x, src_y, half_width, half_height, 0x00CC0020)
        
        gdi32.DeleteObject(hbm_mem)
        gdi32.DeleteDC(hdc_mem)
    
    def spawn_mega_explosion(self, x, y):
        try:
            for column in self.melt_columns:
                dist = abs(column.x - x)
                if dist < 100:
                    column.heat += 50 * (1.0 - dist / 100.0)
            
            for _ in range(80):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(5, 25)
                self.particles.append(Particle(
                    x, y,
                    speed * math.cos(angle), speed * math.sin(angle),
                    random.randint(60, 120),
                    random.uniform(0, 1),
                    "explosive"
                ))
            
            for _ in range(40):
                self.particles.append(Particle(
                    x + random.randint(-50, 50), y + random.randint(-50, 50),
                    random.uniform(-2, 2), random.uniform(-5, 2),
                    random.randint(100, 200),
                    random.uniform(0, 1),
                    "floating"
                ))
            
            if len(self.particles) > 20 and random.random() < 0.3:
                particle_group = self.particles[-20:]
                for i in range(len(particle_group)):
                    for j in range(i + 1, len(particle_group)):
                        if random.random() < 0.2:
                            p1, p2 = particle_group[i], particle_group[j]
                            dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
                            self.particle_springs.append(SpringConstraint(p1, p2, dist, 0.1))
            
            for _ in range(8):
                self.spheres_3d.append(Sphere3D(
                    x - self.width // 2, y - self.height // 2, random.randint(-100, 100),
                    random.uniform(-15, 15), random.uniform(-15, 15), random.uniform(-10, 20),
                    random.randint(20, 60),
                    random.randint(200, 400)
                ))
            
            self.vortices.append(Vortex(
                x, y,
                random.uniform(0.5, 2.0),
                random.randint(100, 200)
            ))
            
            for _ in range(5):
                end_x = x + random.randint(-300, 300)
                end_y = y + random.randint(-300, 300)
                self.lightning_bolts.append(LightningBolt(x, y, end_x, end_y))
            
            for _ in range(6):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(3, 10)
                self.metaballs.append(Metaball(
                    x, y,
                    speed * math.cos(angle),
                    speed * math.sin(angle),
                    random.randint(30, 60)
                ))
            
            self.shockwave_effects.append({
                'x': x, 'y': y, 'radius': 0, 'speed': 12,
                'life': 100, 'max_life': 100,
                'hue_shift': random.uniform(0, 1)
            })
            
            self.screen_shake['intensity'] = 30
            
            rd_x = int(x / 4)
            rd_y = int(y / 4)
            if 0 < rd_x < len(self.reaction_diffusion[0]) - 1 and 0 < rd_y < len(self.reaction_diffusion) - 1:
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        if 0 <= rd_y + dy < len(self.reaction_diffusion) and 0 <= rd_x + dx < len(self.reaction_diffusion[0]):
                            self.reaction_diffusion[rd_y + dy][rd_x + dx] = 1.0
                            self.reaction_diffusion_b[rd_y + dy][rd_x + dx] = 1.0
            
        except Exception:
            pass
    
    def update_screen_shake(self):
        if random.random() < 0.3:
            self.screen_shake['intensity'] = random.uniform(5, 25)
        
        if self.screen_shake['intensity'] > 0:
            self.screen_shake['x'] = random.randint(-int(self.screen_shake['intensity']), 
                                                  int(self.screen_shake['intensity']))
            self.screen_shake['y'] = random.randint(-int(self.screen_shake['intensity']), 
                                                  int(self.screen_shake['intensity']))
            self.screen_shake['intensity'] *= 0.85
        else:
            self.screen_shake['x'] = 0
            self.screen_shake['y'] = 0
    
    def update_collapse_effect(self):
        if random.random() < 0.02:
            self.collapse_effect['active'] = True
            self.collapse_effect['progress'] = 0
            self.collapse_effect['center_x'] = random.randint(200, self.width - 200)
            self.collapse_effect['center_y'] = random.randint(200, self.height - 200)
        
        if self.collapse_effect['active']:
            self.collapse_effect['progress'] += 0.02
            if self.collapse_effect['progress'] >= 1.0:
                self.collapse_effect['active'] = False
    
    def draw_intense_plasma(self, hdc):
        try:
            for y in range(0, self.height, 3):
                for x in range(0, self.width, 3):
                    plasma1 = math.sin(x * 0.02 + self.plasma_time * 2)
                    plasma2 = math.sin(y * 0.02 + self.plasma_time * 1.5)
                    plasma3 = math.sin((x + y) * 0.015 + self.plasma_time * 3)
                    plasma4 = math.sin(math.sqrt(x*x + y*y) * 0.02 + self.plasma_time * 4)
                    plasma5 = math.sin((x - y) * 0.01 + self.plasma_time * 2.5)
                    
                    combined = plasma1 + plasma2 + plasma3 + plasma4 + plasma5
                    
                    if self.collapse_effect['active']:
                        dx = x - self.collapse_effect['center_x']
                        dy = y - self.collapse_effect['center_y']
                        dist = math.sqrt(dx*dx + dy*dy)
                        distortion = math.sin(dist * 0.05 - self.collapse_effect['progress'] * 10) * self.collapse_effect['progress'] * 50
                        combined += distortion
                    
                    hue = (combined + 5) / 10.0
                    saturation = 0.9 + 0.1 * math.sin(self.plasma_time * 3)
                    brightness = 0.8 + 0.2 * math.sin(self.plasma_time * 2)
                    
                    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue % 1.0, saturation, brightness)]
                    color = (r << 16) | (g << 8) | b
                    
                    render_x = x + self.screen_shake['x']
                    render_y = y + self.screen_shake['y']
                    
                    if 0 <= render_x < self.width - 3 and 0 <= render_y < self.height - 3:
                        brush = gdi32.CreateSolidBrush(color)
                        if brush:
                            rect = RECT(render_x, render_y, render_x + 3, render_y + 3)
                            user32.FillRect(hdc, byref(rect), brush)
                            gdi32.DeleteObject(brush)
        except Exception:
            pass
    
    def draw_3d_spheres(self, hdc):
        try:
            for sphere in self.spheres_3d[:]:
                sphere.x += sphere.vx
                sphere.y += sphere.vy
                sphere.z += sphere.vz
                sphere.rotation += sphere.rot_speed
                sphere.life -= 1
                
                if sphere.z > 200:
                    sphere.vz = -abs(sphere.vz)
                elif sphere.z < -200:
                    sphere.vz = abs(sphere.vz)
                
                if sphere.life <= 0:
                    self.spheres_3d.remove(sphere)
                    continue
                
                screen_x, screen_y = self.project_3d_point(sphere.x, sphere.y, sphere.z)
                
                if -100 <= screen_x <= self.width + 100 and -100 <= screen_y <= self.height + 100:
                    scale = max(0.1, 400 / (400 + sphere.z))
                    apparent_radius = int(sphere.radius * scale)
                    
                    alpha = int(255 * sphere.life / sphere.max_life)
                    
                    for lat in range(-90, 91, 20):
                        lat_radius = apparent_radius * math.cos(math.radians(lat))
                        lat_y = screen_y + int(apparent_radius * math.sin(math.radians(lat)))
                        
                        if lat_radius > 2:
                            color = self.get_rainbow_color(alpha, sphere.rotation + lat * 0.01)
                            pen = gdi32.CreatePen(0, 2, color)
                            if pen:
                                old_pen = gdi32.SelectObject(hdc, pen)
                                gdi32.Ellipse(hdc, 
                                            int(screen_x - lat_radius), int(lat_y - 2),
                                            int(screen_x + lat_radius), int(lat_y + 2))
                                gdi32.SelectObject(hdc, old_pen)
                                gdi32.DeleteObject(pen)
                    
                    for lon in range(0, 360, 30):
                        color = self.get_rainbow_color(alpha, sphere.rotation + lon * 0.01)
                        pen = gdi32.CreatePen(0, 1, color)
                        if pen:
                            old_pen = gdi32.SelectObject(hdc, pen)
                            
                            points = []
                            for angle in range(-90, 91, 10):
                                x_offset = int(apparent_radius * math.cos(math.radians(angle)) * math.cos(math.radians(lon + sphere.rotation * 50)))
                                y_offset = int(apparent_radius * math.sin(math.radians(angle)))
                                points.append((screen_x + x_offset, screen_y + y_offset))
                            
                            for i in range(len(points) - 1):
                                gdi32.MoveToEx(hdc, points[i][0], points[i][1], None)
                                gdi32.LineTo(hdc, points[i+1][0], points[i+1][1])
                            
                            gdi32.SelectObject(hdc, old_pen)
                            gdi32.DeleteObject(pen)
        except Exception:
            pass
    
    def draw_advanced_particles(self, hdc):
        try:
            for particle in self.particles[:]:
                particle.x += particle.vx
                particle.y += particle.vy
                
                if particle.ptype == "explosive":
                    particle.vx *= 0.95
                    particle.vy *= 0.95
                    particle.vy += 0.3
                elif particle.ptype == "floating":
                    particle.vx += random.uniform(-0.5, 0.5)
                    particle.vy += random.uniform(-0.5, 0.5)
                    particle.vx *= 0.98
                    particle.vy *= 0.98
                else:
                    particle.vx *= 0.97
                    particle.vy *= 0.97
                    particle.vy += 0.15
                
                particle.rotation += 0.1
                particle.life -= 1
                
                if particle.life <= 0 or particle.y > self.height + 50:
                    self.particles.remove(particle)
                    continue
                
                alpha = particle.life / particle.max_life
                
                for trail in range(5):
                    trail_alpha = alpha * (0.8 - trail * 0.15)
                    trail_x = particle.x - particle.vx * trail
                    trail_y = particle.y - particle.vy * trail
                    trail_size = particle.size * (1.0 - trail * 0.2)
                    
                    if trail_alpha > 0:
                        color = self.get_rainbow_color(int(255 * trail_alpha), particle.color_shift + trail * 0.1)
                        brush = gdi32.CreateSolidBrush(color)
                        if brush:
                            size = int(trail_size)
                            gdi32.SelectObject(hdc, brush)
                            gdi32.Ellipse(hdc, 
                                        int(trail_x - size), int(trail_y - size),
                                        int(trail_x + size), int(trail_y + size))
                            gdi32.DeleteObject(brush)
        except Exception:
            pass
    
    def draw_lightning_system(self, hdc):
        try:
            for bolt in self.lightning_bolts[:]:
                bolt.life -= 1
                if bolt.life <= 0:
                    self.lightning_bolts.remove(bolt)
                    continue
                
                alpha = bolt.life / bolt.max_life
                
                for i in range(len(bolt.points) - 1):
                    x1, y1 = bolt.points[i]
                    x2, y2 = bolt.points[i + 1]
                    
                    for glow in range(3):
                        width = 6 - glow * 2
                        glow_alpha = alpha * (0.3 - glow * 0.1)
                        color = self.get_rainbow_color(int(255 * glow_alpha), 0.6, 0.5, 1.0)
                        pen = gdi32.CreatePen(0, width, color)
                        if pen:
                            old_pen = gdi32.SelectObject(hdc, pen)
                            gdi32.MoveToEx(hdc, int(x1), int(y1), None)
                            gdi32.LineTo(hdc, int(x2), int(y2))
                            gdi32.SelectObject(hdc, old_pen)
                            gdi32.DeleteObject(pen)
                    
                    color = self.get_rainbow_color(int(255 * alpha), 0.6, 0.2, 1.0)
                    pen = gdi32.CreatePen(0, 2, color)
                    if pen:
                        old_pen = gdi32.SelectObject(hdc, pen)
                        gdi32.MoveToEx(hdc, int(x1), int(y1), None)
                        gdi32.LineTo(hdc, int(x2), int(y2))
                        gdi32.SelectObject(hdc, old_pen)
                        gdi32.DeleteObject(pen)
                
                for branch in bolt.branches:
                    for i in range(len(branch) - 1):
                        x1, y1 = branch[i]
                        x2, y2 = branch[i + 1]
                        color = self.get_rainbow_color(int(128 * alpha), 0.6, 0.3, 0.8)
                        pen = gdi32.CreatePen(0, 1, color)
                        if pen:
                            old_pen = gdi32.SelectObject(hdc, pen)
                            gdi32.MoveToEx(hdc, int(x1), int(y1), None)
                            gdi32.LineTo(hdc, int(x2), int(y2))
                            gdi32.SelectObject(hdc, old_pen)
                            gdi32.DeleteObject(pen)
        except Exception:
            pass
    
    def draw_metaballs(self, hdc):
        try:
            for ball in self.metaballs[:]:
                ball.x += ball.vx
                ball.y += ball.vy
                ball.vx *= 0.98
                ball.vy *= 0.98
                
                if ball.x < ball.radius or ball.x > self.width - ball.radius:
                    ball.vx = -ball.vx
                if ball.y < ball.radius or ball.y > self.height - ball.radius:
                    ball.vy = -ball.vy
                
                ball.life -= 1
                if ball.life <= 0:
                    self.metaballs.remove(ball)
            
            grid_size = 8
            threshold = 1.0
            
            for y in range(0, self.height, grid_size):
                for x in range(0, self.width, grid_size):
                    sum_influence = 0
                    
                    for ball in self.metaballs:
                        dx = x - ball.x
                        dy = y - ball.y
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist > 0:
                            sum_influence += (ball.radius * ball.radius) / (dist * dist)
                    
                    if sum_influence > threshold:
                        intensity = min(1.0, sum_influence / 2.0)
                        color = self.get_rainbow_color(int(255 * intensity), 0.3, 0.9, intensity)
                        brush = gdi32.CreateSolidBrush(color)
                        if brush:
                            rect = RECT(x, y, x + grid_size, y + grid_size)
                            user32.FillRect(hdc, byref(rect), brush)
                            gdi32.DeleteObject(brush)
        except Exception:
            pass
    
    def update_particle_physics(self):
        try:
            for spring in self.particle_springs[:]:
                if spring.p1 not in self.particles or spring.p2 not in self.particles:
                    self.particle_springs.remove(spring)
                    continue
                
                dx = spring.p2.x - spring.p1.x
                dy = spring.p2.y - spring.p1.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist > 0:
                    force = (dist - spring.rest_length) * spring.strength
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force
                    
                    spring.p1.vx += fx / spring.p1.mass
                    spring.p1.vy += fy / spring.p1.mass
                    spring.p2.vx -= fx / spring.p2.mass
                    spring.p2.vy -= fy / spring.p2.mass
            
            for i, p1 in enumerate(self.particles):
                for p2 in self.particles[i+1:]:
                    dx = p2.x - p1.x
                    dy = p2.y - p1.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    if 0 < dist < 100:
                        force = (p1.charge * p2.charge * 50) / (dist * dist)
                        fx = (dx / dist) * force
                        fy = (dy / dist) * force
                        
                        p1.vx -= fx / p1.mass
                        p1.vy -= fy / p1.mass
                        p2.vx += fx / p2.mass
                        p2.vy += fy / p2.mass
        except Exception:
            pass
    
    def update_reaction_diffusion(self):
        try:
            width = len(self.reaction_diffusion[0])
            height = len(self.reaction_diffusion)
            
            feed_rate = 0.055
            kill_rate = 0.062
            diffusion_a = 1.0
            diffusion_b = 0.5
            dt = 1.0
            
            new_a = [[0.0 for _ in range(width)] for _ in range(height)]
            new_b = [[0.0 for _ in range(width)] for _ in range(height)]
            
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    a = self.reaction_diffusion[y][x]
                    b = self.reaction_diffusion_b[y][x]
                    
                    lap_a = (self.reaction_diffusion[y-1][x] + self.reaction_diffusion[y+1][x] +
                             self.reaction_diffusion[y][x-1] + self.reaction_diffusion[y][x+1] - 4 * a)
                    
                    lap_b = (self.reaction_diffusion_b[y-1][x] + self.reaction_diffusion_b[y+1][x] +
                             self.reaction_diffusion_b[y][x-1] + self.reaction_diffusion_b[y][x+1] - 4 * b)
                    
                    reaction = a * b * b
                    new_a[y][x] = a + (diffusion_a * lap_a - reaction + feed_rate * (1 - a)) * dt
                    new_b[y][x] = b + (diffusion_b * lap_b + reaction - (kill_rate + feed_rate) * b) * dt
                    
                    new_a[y][x] = max(0, min(1, new_a[y][x]))
                    new_b[y][x] = max(0, min(1, new_b[y][x]))
            
            self.reaction_diffusion = new_a
            self.reaction_diffusion_b = new_b
        except Exception:
            pass
    
    def draw_reaction_diffusion(self, hdc):
        try:
            scale = 4
            for y in range(len(self.reaction_diffusion)):
                for x in range(len(self.reaction_diffusion[0])):
                    value = self.reaction_diffusion_b[y][x]
                    if value > 0.1:
                        intensity = min(1.0, value * 2)
                        color = self.get_rainbow_color(int(255 * intensity), value, 0.8, intensity)
                        brush = gdi32.CreateSolidBrush(color)
                        if brush:
                            rect = RECT(x * scale, y * scale, (x + 1) * scale, (y + 1) * scale)
                            user32.FillRect(hdc, byref(rect), brush)
                            gdi32.DeleteObject(brush)
        except Exception:
            pass
    
    def draw_extreme_melt(self, hdc):
        try:
            current_time = time.time()
            
            for column in self.melt_columns:
                x = column.x
                
                column.heat += random.uniform(0, 5) * math.sin(current_time * column.melt_speed)
                column.heat = max(0, column.heat * 0.95)
                
                if column.heat > 10:
                    melt_amount = int(column.heat * 2)
                    
                    for y in range(self.height - 1, melt_amount, -1):
                        source_y = y - melt_amount
                        if source_y >= 0:
                            source_color = gdi32.GetPixel(hdc, x, source_y)
                            if source_color != 0xFFFFFFFF:
                                gdi32.SetPixel(hdc, x, y, source_color)
                    
                    for glow_y in range(min(melt_amount * 2, self.height)):
                        glow_intensity = 1.0 - (glow_y / (melt_amount * 2))
                        heat_color = self.get_rainbow_color(
                            int(200 * glow_intensity), 
                            0.0, 
                            1.0, 
                            glow_intensity
                        )
                        gdi32.SetPixel(hdc, x, glow_y, heat_color)
                        
                    if random.random() < 0.1:
                        drip_length = random.randint(5, 20)
                        drip_x = x + random.randint(-2, 2)
                        drip_color = self.get_rainbow_color(180, 0.1, 0.8, 0.9)
                        
                        for drip_y in range(self.height - drip_length, self.height):
                            if 0 <= drip_x < self.width and 0 <= drip_y < self.height:
                                gdi32.SetPixel(hdc, drip_x, drip_y, drip_color)
        except Exception:
            pass
    
    def apply_vortex_distortion(self, x, y):
        dist_x, dist_y = x, y
        
        for vortex in self.vortices:
            dx = x - vortex.x
            dy = y - vortex.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < vortex.radius and dist > 0:
                angle = math.atan2(dy, dx)
                strength = (1.0 - dist / vortex.radius) * vortex.strength
                angle += strength * vortex.rotation
                
                new_dist = dist * (1.0 - strength * 0.1)
                dist_x += math.cos(angle) * new_dist - dx
                dist_y += math.sin(angle) * new_dist - dy
        
        return int(dist_x), int(dist_y)
    
    def draw_shockwaves(self, hdc):
        for shockwave in self.shockwave_effects[:]:
            shockwave['radius'] += shockwave['speed']
            shockwave['life'] -= 1
            
            if shockwave['life'] <= 0 or shockwave['radius'] > 1000:
                self.shockwave_effects.remove(shockwave)
                continue
            
            alpha = shockwave['life'] / shockwave['max_life']
            color = self.get_rainbow_color(int(255 * alpha), shockwave['hue_shift'])
            
            pen = gdi32.CreatePen(0, 4, color)
            if pen:
                old_pen = gdi32.SelectObject(hdc, pen)
                
                for ring in range(3):
                    ring_radius = int(shockwave['radius'] + ring * 15)
                    gdi32.Ellipse(hdc,
                                shockwave['x'] - ring_radius, shockwave['y'] - ring_radius,
                                shockwave['x'] + ring_radius, shockwave['y'] + ring_radius)
                
                gdi32.SelectObject(hdc, old_pen)
                gdi32.DeleteObject(pen)
    
    def run(self):
        self.desktop_dc = self.get_desktop_dc()
        if not self.desktop_dc:
            return
        
        self.add_initial_conditions()
        self.spawn_mega_explosion(self.width // 2, self.height // 2)
        
        explosion_timer = 0
        sphere_timer = 0
        lightning_timer = 0
        vortex_timer = 0
        metaball_timer = 0
        star_timer = 0
        triangle_timer = 0
        error_timer = 0
        color_shift = 0.0
        triangle_x, triangle_y = self.width // 2, self.height // 2
        speed_x, speed_y = 5, 3
        fragments = []
        waves = []
        last_pulse_time = time.time()
        base_size = 140
        square_size = 30
        square_distance = int(base_size * 1.4)
        square_positions = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        square_rotations = [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]
        
        effects = [self.fog_effect, self.burn_effect, self.kaleidoscope_effect, self.wave_warp_effect, self.jitter_effect]
        effect_duration = 13 # o~ 3
        current_effect_index = 0
        effect_start_time = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                explosion_timer += 1
                sphere_timer += 0.1 #o~ 1
                lightning_timer += 1
                vortex_timer += 1
                metaball_timer += 1
                star_timer += 1
                triangle_timer += 1
                error_timer += 1
                
                if explosion_timer >= 25:
                    self.spawn_mega_explosion(
                        random.randint(100, self.width - 100),
                        random.randint(100, self.height - 100)
                    )
                    explosion_timer = 0
                
                if sphere_timer >= 15:
                    for _ in range(3):
                        self.spheres_3d.append(Sphere3D(
                            random.randint(-200, 200), random.randint(-200, 200), -300,
                            random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(8, 15),
                            random.randint(15, 40),
                            random.randint(150, 300)
                        ))
                    sphere_timer = 0
                
                if lightning_timer >= 30:
                    for _ in range(2):
                        x1 = random.randint(0, self.width)
                        y1 = 0
                        x2 = random.randint(0, self.width)
                        y2 = self.height
                        self.lightning_bolts.append(LightningBolt(x1, y1, x2, y2))
                    
                    if random.random() < 0.3:
                        y = random.randint(0, self.height)
                        self.lightning_bolts.append(LightningBolt(0, y, self.width, y))
                    
                    lightning_timer = 0
                
                if vortex_timer >= 50:
                    self.vortices.append(Vortex(
                        random.randint(100, self.width - 100),
                        random.randint(100, self.height - 100),
                        random.uniform(0.3, 1.5),
                        random.randint(80, 200)
                    ))
                    vortex_timer = 0
                
                if metaball_timer >= 20:
                    for _ in range(4):
                        self.metaballs.append(Metaball(
                            random.randint(50, self.width - 50),
                            random.randint(50, self.height - 50),
                            random.uniform(-5, 5),
                            random.uniform(-5, 5),
                            random.randint(20, 80)
                        ))
                    metaball_timer = 0
                
                if star_timer >= 60:
                    self.create_shooting_star()
                    star_timer = 0
                
                if error_timer >= 20: # 0~ 100
                    threading.Thread(target=self.show_chaotic_message, daemon=True).start()
                    error_timer = 0
                
                if len(self.particles) > 1000:
                    self.particles = self.particles[-800:]
                if len(self.spheres_3d) > 50:
                    self.spheres_3d = self.spheres_3d[-40:]
                if len(self.lightning_bolts) > 15:
                    self.lightning_bolts = self.lightning_bolts[-10:]
                if len(self.vortices) > 10:
                    self.vortices = self.vortices[-8:]
                if len(self.metaballs) > 30:
                    self.metaballs = self.metaballs[-25:]
                if len(self.particle_springs) > 100:
                    self.particle_springs = self.particle_springs[-80:]
                
                self.update_screen_shake()
                self.update_collapse_effect()
                self.update_reaction_diffusion()
                self.update_particle_physics()
                
                for vortex in self.vortices[:]:
                    vortex.rotation += 0.1
                    vortex.life -= 1
                    if vortex.life <= 0:
                        self.vortices.remove(vortex)
                
                self.fractal_zoom = 1.0 + 0.5 * math.sin(self.plasma_time * 0.3)
                self.fractal_offset_x = 0.1 * math.sin(self.plasma_time * 0.4)
                self.fractal_offset_y = 0.1 * math.cos(self.plasma_time * 0.5)
                
                hdc_mem = gdi32.CreateCompatibleDC(self.desktop_dc)
                if not hdc_mem:
                    continue
                
                hbm_mem = gdi32.CreateCompatibleBitmap(self.desktop_dc, self.width, self.height)
                if not hbm_mem:
                    gdi32.DeleteDC(hdc_mem)
                    continue
                
                old_bitmap = gdi32.SelectObject(hdc_mem, hbm_mem)
                
                gdi32.BitBlt(hdc_mem, 0, 0, self.width, self.height, self.desktop_dc, 0, 0, 0x00CC0020)
                
                self.draw_intense_plasma(hdc_mem)
                
                self.draw_reaction_diffusion(hdc_mem)
                
                if current_time - effect_start_time > effect_duration:
                    current_effect_index = (current_effect_index + 1) % len(effects)
                    effect_start_time = current_time
                effects[current_effect_index](hdc_mem)
                
                self.simulate_fluid()
                self.simulate_shooting_stars()
                self.draw_particles_fluid(hdc_mem)
                
                self.draw_3d_spheres(hdc_mem)
                
                self.draw_metaballs(hdc_mem)
                
                self.draw_advanced_particles(hdc_mem)
                
                self.draw_lightning_system(hdc_mem)
                
                self.draw_shockwaves(hdc_mem)
                
                self.apply_psychedelic_spherical_effect(hdc_mem)
                
                self.spectrum_cycle_effects(hdc_mem, color_shift)
                color_shift = (color_shift + 0.01) % 1.0
                
                pulse_size = base_size + int(30 * math.sin(current_time * 4))
                angle = current_time
                triangle_color = self.get_rainbow_color(alpha=180)
                triangle_vertices = self.generate_triangle(triangle_x, triangle_y, pulse_size, angle)
                
                if current_time - last_pulse_time >= 0.4:
                    for i in range(6):
                        waves.append({
                            'radius': 0,
                            'thickness': 4 + i,
                            'color': self.get_rainbow_color(alpha=220 - i * 30, hue_shift=0.1 * i),
                            'start_time': current_time + 0.04 * i
                        })

                    for _ in range(12):
                        direction_angle = random.uniform(0, 2 * math.pi)
                        fragment_speed = random.uniform(3, 9)
                        fragment_size = random.randint(6, 16)
                        fragment_hue_shift = random.uniform(0, 1)
                        spin_speed = random.uniform(0.3, 0.6)
                        fragments.append({
                            'x': triangle_x,
                            'y': triangle_y,
                            'size': fragment_size,
                            'direction': direction_angle,
                            'rotation': 0,
                            'speed': fragment_speed,
                            'spin_speed': spin_speed,
                            'hue_shift': fragment_hue_shift,
                            'start_time': current_time
                        })

                    last_pulse_time = current_time
                
                for wave in waves[:]:
                    elapsed_wave_time = current_time - wave['start_time']
                    wave['radius'] = int(elapsed_wave_time * 180)
                    if wave['radius'] > 180:
                        waves.remove(wave)
                        continue
                    wave_color = self.get_rainbow_color(alpha=max(0, 220 - int(elapsed_wave_time * 90)), hue_shift=0.2)
                    self.draw_wave(hdc_mem, triangle_x, triangle_y, wave['radius'], wave['thickness'], wave_color)
                
                for fragment in fragments[:]:
                    elapsed_time = current_time - fragment['start_time']
                    fragment['x'] += int(fragment['speed'] * math.cos(fragment['direction']))
                    fragment['y'] += int(fragment['speed'] * math.sin(fragment['direction']))
                    fragment['rotation'] += fragment['spin_speed']
                    fragment_color = self.get_rainbow_color(alpha=max(0, 200 - int(elapsed_time * 120)), hue_shift=fragment['hue_shift'])
                    fragment_vertices = self.generate_triangle(fragment['x'], fragment['y'], fragment['size'], fragment['rotation'])
                    self.draw_triangle(hdc_mem, fragment_vertices, fragment_color)

                    if elapsed_time > 1.5:
                        fragments.remove(fragment)
                
                self.draw_triangle(hdc_mem, triangle_vertices, triangle_color)
                
                for i, position in enumerate(square_positions):
                    square_x = triangle_x + int(square_distance * math.cos(position + angle))
                    square_y = triangle_y + int(square_distance * math.sin(position + angle))
                    square_rotation = square_rotations[i] + current_time * 2
                    self.invert_square(hdc_mem, square_x, square_y, square_size, square_rotation)
                
                triangle_x += speed_x
                triangle_y += speed_y
                if triangle_x > self.width - base_size or triangle_x < base_size:
                    speed_x = -speed_x
                if triangle_y > self.height - base_size or triangle_y < base_size:
                    speed_y = -speed_y
                
                self.draw_extreme_melt(hdc_mem)
                self.melt_screen(hdc_mem)
                
                if random.random() < 0.1:
                    self.explosive_cloning(hdc_mem)
                
                if random.random() < 0.05:
                    self.draw_transparent_blocks(hdc_mem, 0.5)
                
                if random.random() < 0.03:
                    self.shift_screen_quadrants(hdc_mem)
                
                gdi32.BitBlt(self.desktop_dc, 0, 0, self.width, self.height, hdc_mem, 0, 0, 0x00CC0020)
                
                gdi32.SelectObject(hdc_mem, old_bitmap)
                gdi32.DeleteObject(hbm_mem)
                gdi32.DeleteDC(hdc_mem)
                
                self.plasma_time += 0.06
                self.tunnel_rotation += 2
                
                time.sleep(0.01667)
                
            except Exception as e:
                continue
        
        if self.desktop_dc:
            user32.ReleaseDC(None, self.desktop_dc)
    
    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMT Effects Payload")
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        warning_label = QLabel(
            "<h1>DiMethylTryptamine</h1>"
            "<h3 style='color: red;'>EPILEPSY WARNING</h3>"
            "<p>This application produces intense visual effects.</p>"
            "<p>_______________________________________________________________________</p>"
            "<p><b>DO NOT RUN</b> if you have epilepsy or are sensitive to flashing lights.</p>"
            "<p>Enjoy the effects of DMT on your computer</p>"
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("background-color: black; color: white; padding: 20px; font-size: 14px;")
        layout.addWidget(warning_label)
        
        self.start_button = QPushButton("I understand - START")
        self.start_button.setStyleSheet(
            "QPushButton { background-color: red; color: white; font-size: 16px; padding: 15px; }"
            "QPushButton:hover { background-color: darkred; }"
        )
        self.start_button.clicked.connect(self.confirm_start)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("STOP")
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: green; color: white; font-size: 16px; padding: 15px; }"
            "QPushButton:hover { background-color: darkgreen; }"
        )
        self.stop_button.clicked.connect(self.stop_effects)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        self.effects_thread = None
        self.sound_thread = None
        self.escape_timer = QTimer()
        self.escape_timer.timeout.connect(self.check_escape)
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def confirm_start(self):
        reply = QMessageBox.critical(
            self,
            "DMT Payload ~ Final Warning",
            "Are you ABSOLUTELY SURE you want to start?\n\n"
            "This will create multiple visual effect over a period of time which will lead towards your GPU to fail(crash) and will cause a full system meltdown. Your CPU will have to re-train the RAM and overwrite the bootsector(specificly the MBR) to make a simple but trippy game with shaders on boot.(The boot re-write is not implemented in this script)\n\n"
            "Only proceed if you are willing to accept any risks!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_effects()
    
    def start_effects(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.effects_thread = EffectsThread()
        self.effects_thread.start()
        
        self.sound_thread = SoundThread()
        self.sound_thread.start()
        
        self.escape_timer.start(1) # o~ 100
        
        self.showMinimized()
    
    def check_escape(self):
        if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
            self.stop_effects()
    
    def stop_effects(self):
        self.escape_timer.stop()
        
        if self.effects_thread:
            self.effects_thread.stop()
            self.effects_thread.wait()
            self.effects_thread = None
        
        if self.sound_thread:
            self.sound_thread.stop()
            self.sound_thread.wait()
            self.sound_thread = None
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    def closeEvent(self, event):
        self.stop_effects()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
