import board
import displayio
import framebufferio
import rgbmatrix
import time
import random

class DVDLogo:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(0, 64 - width)
        self.y = random.randint(0, 32 - height)
        self.dx = 1
        self.dy = 1
        self.color_index = 1
        self.rainbow_mode = False
        self.rainbow_counter = 0
        
        # DVD text as pixel art (12x5 pixels)
        self.dvd_text = [
            [1,1,1,0,1,1,0,0,1,1,1,0],
            [1,0,1,0,1,0,1,0,1,0,0,0],
            [1,0,1,0,1,0,1,0,1,1,1,0],
            [1,0,1,0,1,0,1,0,1,0,0,0],
            [1,1,1,0,1,1,0,0,1,1,1,0]
        ]
        
    def move(self, max_width, max_height):
        self.x += self.dx
        self.y += self.dy
        
        # Check for corner hits
        hit_corner = False
        if (self.x <= 0 and self.y <= 0) or \
           (self.x <= 0 and self.y + self.height >= max_height) or \
           (self.x + self.width >= max_width and self.y <= 0) or \
           (self.x + self.width >= max_width and self.y + self.height >= max_height):
            hit_corner = True
            self.rainbow_mode = True
            self.rainbow_counter = 0
            
        # Normal wall hits
        if self.x <= 0 or self.x + self.width >= max_width:
            self.dx *= -1
            if not self.rainbow_mode:
                self.color_index = (self.color_index % 6) + 1
        if self.y <= 0 or self.y + self.height >= max_height:
            self.dy *= -1
            if not self.rainbow_mode:
                self.color_index = (self.color_index % 6) + 1
                
    def draw(self, bitmap):
        if self.rainbow_mode:
            self.rainbow_counter += 1
            if self.rainbow_counter > 30:  # Turn off rainbow mode after 30 frames
                self.rainbow_mode = False
            color = (self.rainbow_counter // 5) % 6 + 1
        else:
            color = self.color_index
            
        for y in range(int(self.y), int(self.y + self.height)):
            for x in range(int(self.x), int(self.x + self.width)):
                if 0 <= x < bitmap.width and 0 <= y < bitmap.height:
                    bitmap[x, y] = color
                        
displayio.release_displays()
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

bitmap = displayio.Bitmap(64, 32, 7)
palette = displayio.Palette(7)
palette[0] = 0x000000  # Black background
palette[1] = 0xFF0000  # Red
palette[2] = 0x00FF00  # Green
palette[3] = 0x0000FF  # Blue
palette[4] = 0xFF00FF  # Magenta
palette[5] = 0xFFFF00  # Yellow
palette[6] = 0x00FFFF  # Cyan

tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
group = displayio.Group()
group.append(tile_grid)
display.root_group = group

dvd = DVDLogo(16, 9)

while True:
    for i in range(bitmap.width * bitmap.height):
        bitmap[i] = 0
        
    dvd.move(bitmap.width, bitmap.height)
    dvd.draw(bitmap)
    
    time.sleep(0.05)