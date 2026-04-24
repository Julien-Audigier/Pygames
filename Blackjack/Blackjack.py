import pygame as pg
import os
import random
import math


# To avoid audio errors on systems without sound
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg.init()

screen = pg.display.set_mode((800, 600))
pg.display.set_caption("Great Jack")

#const/global variables
clock = pg.time.Clock()
cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
cardsPrice = [1,2,3,4,5,6,7,8,9,10,10,10,10]

def pixelize_screen(pixel_size): 
    """Faster pixelization: scale down and back up instead of per-pixel work."""
    if pixel_size <= 1:
        return
    w, h = screen.get_size()
    small_w = max(1, w // pixel_size)
    small_h = max(1, h // pixel_size)
    # Scale the current screen surface down, then scale it back up.
    # This produces a pixelated look but is much faster than per-pixel draws.
    small = pg.transform.scale(screen, (small_w, small_h))
    scaled = pg.transform.scale(small, (w, h))
    screen.blit(scaled, (0, 0))

def lerp(end: float, var: float, speed: float=2.5):
   """returns var+result"""
   return var+(end-var)*speed/10

def point_c(angle: float, x, y, width, height):
    i = (angle * math.pi) / 180
    a = width / 2
    b = height / 2
    p = x + a * math.cos(i)
    j = y + b * math.sin(i)
    return (p, j)

def in_ballpark(var, equal, buffer = 10):
    return var < equal + 10 and var > equal - 10

def round_down(var):
    inter = round(var)
    if inter > var:
        return inter-1
    return inter

class IMAGE:
    def __init__(self, path, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = path
        # Load and convert once for faster blitting
        loaded = pg.image.load(path)
        try:
            self.image = loaded.convert()
        except Exception:
            self.image = loaded.convert_alpha()
        if (self.image.get_size() != (width, height)):
            self.image = pg.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(x,y))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self, x, y):
        self.x += x
        self.y += y
        self.rect.topleft = (self.x,self.y)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.image = pg.transform.scale(self.image, (width, height))
        self.rect.size = (width,height)

    def change_color(self, old_color, new_color):
        """Change all pixels of old_color to new_color in the image."""
        original_image = pg.image.load(self.path).convert_alpha()
        original_image.set_colorkey(old_color)
        new_image = pg.Surface(original_image.get_size(), pg.SRCALPHA)
        new_image.fill(new_color)
        new_image.blit(original_image, (0, 0))

class TEXT:
    def __init__(self, text, x, y, font_size=30, color=(0, 0, 0), hover_color=None,mode="center"):
        if hover_color is None:
            hover_color = color
        self.text = text
        self.x = x
        self.y = y
        self.start_color = color
        self.hover_color = hover_color
        self.deffont_size = font_size
        self.font_size = font_size
        # Create font and cache rendered surfaces to avoid recreating each frame
        self.font = pg.font.SysFont(None, font_size)
        self.text_surface_start = self.font.render(text, True, color)
        self.text_surface_hover = self.font.render(text, True, hover_color)
        self.mode = mode
        match mode:
            case "center":
                self.text_rect = self.text_surface_start.get_rect(center=(x, y))
            case "topleft":
                self.text_rect = self.text_surface_start.get_rect(topleft=(x, y))
        self._last_hover = False
        # Tracks whether a mouse press began while the cursor was over this text
        self._pressed_inside = False

    def is_clicked(self):
        return self.text_rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]
    
    def draw(self):
        pos = pg.mouse.get_pos()
        hover = self.text_rect.collidepoint(pos)
        # Only change rendering when hover state changes
        if hover:
            surf = self.text_surface_hover
        else:
            surf = self.text_surface_start
        # Respect alignment mode set at creation
        if getattr(self, 'mode', 'center') == 'topleft':
            text_rect = surf.get_rect(topleft=(self.x, self.y))
        else:
            text_rect = surf.get_rect(center=(self.x, self.y))
        # update stored rect so click detection stays accurate
        self.text_rect = text_rect
        screen.blit(surf, text_rect)

    def change_text(self, new_text):
        self.text = new_text
        self.text_surface_start = self.font.render(new_text, True, self.start_color)
        self.text_surface_hover = self.font.render(new_text, True, self.hover_color)
        # Update rect to match new text size 
        if getattr(self, 'mode', 'center') == 'topleft':
            self.text_rect = self.text_surface_start.get_rect(topleft=(self.x, self.y))
        else:
            self.text_rect = self.text_surface_start.get_rect(center=(self.x, self.y))

    def is_released(self):
        pos = pg.mouse.get_pos()
        pressed = pg.mouse.get_pressed()[0]
        hover = self.text_rect.collidepoint(pos)
        # If mouse pressed while hovering, remember that press started here
        if pressed and hover:
            self._pressed_inside = True
            return False
        # If mouse was pressed on this widget and is now released, count it as a release
        if (not pressed) and self._pressed_inside:
            # reset state and only return True if cursor is still over the widget
            self._pressed_inside = False
            return hover
        # Otherwise, no release event for this widget
        return False

    def move(self, x, y):
        self.x =x
        self.y = y
        match self.mode:
            case "center":
                self.text_rect = self.text_surface_start.get_rect(center=(self.x, self.y))
            case "topleft":
                self.text_rect = self.text_surface_start.get_rect(topleft=(self.x, self.y))

class SUIT:
    def __init__(self,name: str, symbol: str, color: tuple, font = "dejavusans"):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.font = font
    
    def draw(self, name: str, x: int = 0, y: int = 0, font_size = 30, card_color: tuple=(255, 249, 237), text_width_ratio=4.5, height_ratio=1.55, rotation: float = 0):
        """Draw a card with the suit symbol and name. Rotation is in degrees."""
        # Treat x,y as the center of the card
        width = int(text_width_ratio * font_size)
        height = int(text_width_ratio * font_size * height_ratio)
        
        # Create a temporary surface for the card
        card_surface = pg.Surface((width, height), pg.SRCALPHA)
        card_surface.fill(card_color)
        
        left = 0
        right = width
        top = 0
        bottom = height

        # Draw card background and border
        pg.draw.rect(card_surface, card_color, (left, top, width, height))  # White rectangle
        if name is not None:
            # DejaVu Sans is commonly available on Linux and contains hearts/playing symbols
            symbol_font = pg.font.SysFont(self.font, int(font_size * 0.5))
            symbol_surface = symbol_font.render(self.symbol, True, self.color)
            symbol_rect = symbol_surface.get_rect(center=(width // 2, height // 2))
            
            # Name in top left
            font = pg.font.SysFont(None, font_size)
            text_surface = font.render(name, True, self.color)
            text_rect = text_surface.get_rect()
            card_surface.blit(text_surface, (left - text_rect.width//2 + 20 * font_size//30, top - text_rect.height//2 + 20 * font_size//30))

            # Suit symbol in top left
            card_surface.blit(symbol_surface, (left - symbol_rect.width//2 + 20.5 * font_size//30, top - symbol_rect.height//2 + 40 * font_size//30))

            # Mirror Name in bottom right (no rotation—use flip instead)
            flipped_text = pg.transform.flip(text_surface, True, True)
            flipped_text_rect = flipped_text.get_rect(center=(right - 20 * font_size//30, bottom - 20 * font_size//30))
            card_surface.blit(flipped_text, flipped_text_rect)

            # Mirror Suit symbol in bottom right
            flipped_symbol = pg.transform.flip(symbol_surface, True, True)
            flipped_symbol_rect = flipped_symbol.get_rect(center=(right - 20.5 * font_size//30, bottom - 40 * font_size//30))
            card_surface.blit(flipped_symbol, flipped_symbol_rect)

        match name:
            case "A" | "1":
                # Suit symbol in center — use a font that includes the symbol glyph
                symbol_font = pg.font.SysFont(self.font, int(font_size * 1.5))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
            case "2":
                # Two symbols, one in upper half and one in lower half
                symbol_font = pg.font.SysFont(self.font, int(font_size * 1.2))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + height // 3))
                card_surface.blit(symbol_surface, symbol_rect)
                rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                symbol_rect = rotated_symbol.get_rect(center=(left + width // 2, top + 2 * height // 3))
                card_surface.blit(rotated_symbol, symbol_rect)
            case "3":
                # Three symbols, one in upper half, one in center, and one in lower half
                symbol_font = pg.font.SysFont(self.font, int(font_size * 1.2))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + height // 4))
                card_surface.blit(symbol_surface, symbol_rect)
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
                rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                symbol_rect = rotated_symbol.get_rect(center=(left + width // 2, top + 3 * height // 4))
                card_surface.blit(rotated_symbol, symbol_rect)
            case "4":
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                # Corners
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = height // 2 + dy * (height // 2) - dy * 40 * font_size // 30
                    if (dx, dy) in [(-1, 1), (1, 1)]:  # Bottom corners
                        rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                        symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(rotated_symbol, symbol_rect)
                    else:
                        symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(symbol_surface, symbol_rect)
            case "5":
                # Five symbols: four in corners and one in center
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                # Center
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
                # Corners
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = height // 2 + dy * (height // 2) - dy * 40 * font_size // 30
                    if (dx, dy) in [(-1, 1), (1, 1)]:  # Bottom corners
                        rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                        symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(rotated_symbol, symbol_rect)
                    else:
                        symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(symbol_surface, symbol_rect)
            case "6":
                # Six symbols: two columns of three
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                # Centers
                symbol_rect = symbol_surface.get_rect(center=(left + 40 * font_size // 30, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
                symbol_rect = symbol_surface.get_rect(center=(right - 40 * font_size // 30, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
                # Corners
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = height // 2 + dy * (height // 2) - dy * 40 * font_size // 30
                    if (dx, dy) in [(-1, 1), (1, 1)]:  # Bottom corners
                        rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                        symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(rotated_symbol, symbol_rect)
                    else:
                        symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(symbol_surface, symbol_rect)
            case "7":
                # Six symbols: two columns of three
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                # Centers
                symbol_rect = symbol_surface.get_rect(center=(left + 40 * font_size // 30, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
                symbol_rect = symbol_surface.get_rect(center=(right - 40 * font_size // 30, top + height // 2))
                card_surface.blit(symbol_surface, symbol_rect)
                # Corners
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = height // 2 + dy * (height // 2) - dy * 40 * font_size // 30
                    if (dx, dy) in [(-1, 1), (1, 1)]:  # Bottom corners
                        rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                        symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(rotated_symbol, symbol_rect)
                    else:
                        symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                        card_surface.blit(symbol_surface, symbol_rect)
                # Top center
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + 70 * font_size // 30))
                card_surface.blit(symbol_surface, symbol_rect)
            case "8":
                # Top Corners
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = (height // 2 + dy * (height // 3.45) - dy * 40 * font_size // 30)-40 * font_size // 30 * height_ratio//1.55
                    symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                    card_surface.blit(symbol_surface, symbol_rect)
                # Bottom Corners
                rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = (height // 2 + dy * (height // 3.45) - dy * 40 * font_size // 30)+40 * font_size // 30 * height_ratio//1.55
                    symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                    card_surface.blit(rotated_symbol, symbol_rect)
            case "9":
                # Top Corners
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = (height // 2 + dy * (height // 3.45) - dy * 40 * font_size // 30)-40 * font_size // 30
                    symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                    card_surface.blit(symbol_surface, symbol_rect)
                # Bottom Corners
                rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = (height // 2 + dy * (height // 3.45) - dy * 40 * font_size // 30)+40 * font_size // 30
                    symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                    card_surface.blit(rotated_symbol, symbol_rect)
                #Top Middle
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + 65 * font_size // 30))
                card_surface.blit(symbol_surface, symbol_rect)
            case "10":
                # Top Corners
                symbol_font = pg.font.SysFont(self.font, int(font_size * 0.9))
                symbol_surface = symbol_font.render(self.symbol, True, self.color)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = (height // 2 + dy * (height // 3.45) - dy * 40 * font_size // 30)-40 * font_size // 30
                    symbol_rect = symbol_surface.get_rect(center=(corner_x, corner_y))
                    card_surface.blit(symbol_surface, symbol_rect)
                # Bottom Corners
                rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = width // 2 + dx * (width // 2) - dx * 40 * font_size // 30
                    corner_y = (height // 2 + dy * (height // 3.45) - dy * 40 * font_size // 30)+40 * font_size // 30
                    symbol_rect = rotated_symbol.get_rect(center=(corner_x, corner_y))
                    card_surface.blit(rotated_symbol, symbol_rect)
                # Top Middle
                symbol_rect = symbol_surface.get_rect(center=(left + width // 2, top + 65 * font_size // 30))
                card_surface.blit(symbol_surface, symbol_rect)
                # Bottom Middle
                rotated_symbol = pg.transform.rotate(symbol_surface, 180)
                symbol_rect = rotated_symbol.get_rect(center=(left + width // 2, top + 2 * height // 3))
                card_surface.blit(rotated_symbol, symbol_rect)
            case None:
                # Draw card back pattern
                pg.draw.rect(card_surface, (200, 0, 0), (left, top, width, height),5, border_radius=100)
                pg.draw.rect(card_surface, (200, 0, 0), (left, top, width, height),7) # Red border for card back
                #for i in range(0, width + height, 20):
                #    pg.draw.line(card_surface, (200, 0, 0), (i, 0), (i - height, height), 2)
                #for i in range(width + height,0, -20):
                #    pg.draw.line(card_surface, (200, 0, 0), (i, 0), (i - height, height), 2)
            case _:
                # Put name in the middle
                font = pg.font.SysFont(None, int(font_size * 2))
                text_surface = font.render(name, True, self.color)
                text_rect = text_surface.get_rect(center=(left + width // 2, top + height // 2))
                card_surface.blit(text_surface, text_rect)

        # Rotate the card surface if needed and blit to screen
        if rotation != 0:
            rotated_card = pg.transform.rotate(card_surface, rotation)
            rotated_rect = rotated_card.get_rect(center=(x, y))
            return (rotated_card, rotated_rect)
        else:
            card_rect = card_surface.get_rect(center=(x, y))
            return (card_surface, card_rect)
             
class CARD:
    def __init__(self, suit: SUIT, name: str, weight: int, font_size: int = 30, rotation: float = 0, card_color: tuple=(255, 249, 237),side="front"):
        self.suit = suit
        self.name = name
        self.weight = weight
        self.font_size = font_size
        self.rotation = rotation
        self.card_color = card_color
        self.x = 0
        self.y = 0
        if side not in ["front","back"]:
            side = "front"
        if side == "back":
            name = None
        self.surface = suit.draw(name, 0, 0, self.font_size, card_color=card_color, rotation=rotation)
        self.side = side

    def draw(self, x = None, y = None, rotation=0, shadow=False, shadow_alpha=128, shadow_offset=(5, 5), hover:bool=False, hover_offset:float=6, front_hover:bool=False):
        surface = self.surface[0]
        self.x = x if x is not None else self.surface[1].centerx
        self.y = y if y is not None else self.surface[1].centery
        if rotation != 0:
            surface = pg.transform.rotate(surface, rotation)
        
        card_rect = surface.get_rect(center=(x, y) if (x is not None and y is not None) else self.surface[1].center)
        
        if (hover and not front_hover) or (hover and front_hover and self.side == "front"):
            mouse_pos = pg.mouse.get_pos()
            if card_rect.collidepoint(mouse_pos):
                w, h = surface.get_size()
                new_w = w + int(hover_offset)
                new_h = h + int(hover_offset)
                surface = pg.transform.scale(surface, (new_w, new_h))
                card_rect = surface.get_rect(center=card_rect.center)

        if shadow:
            shadow_surf = surface.copy()
            shadow_surf.fill((0, 0, 0, shadow_alpha), special_flags=pg.BLEND_RGBA_MULT)
            shadow_rect = shadow_surf.get_rect(center=(card_rect.centerx + shadow_offset[0], card_rect.centery + shadow_offset[1]))
            screen.blit(shadow_surf, shadow_rect)
        
        screen.blit(surface, card_rect)
    
    def resize(self, font_size):
        self.font_size = font_size
        if self.side == "back":
            name = None
        else:
            name = self.name
        self.surface = self.suit.draw(name, self.x, self.y, self.font_size, card_color=self.card_color, rotation=self.rotation)      

    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.surface = (pg.transform.rotate(self.surface[0], angle), self.surface[1])

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.surface = (self.surface[0], self.surface[0].get_rect(center=(x, y)))

    def move_right(self, distance, rotation=None):
        if rotation == None:
            rotation = self.rotation
        x = math.sin((rotation % 360)) * distance
        y = math.sqrt(x*x - distance*distance) if x*x-distance*distance >= 0 else 0
        self.set_pos(self.x + x, self.y + y)

    def is_clicked(self, mouse_pos):
        # Get the current drawn surface and compute its rect at the card's center.
        surface = self.surface[0]
        card_rect = surface.get_rect(center=(self.x, self.y))
        return card_rect.collidepoint(mouse_pos)

class DECK:
    def __init__(self, num_decks=1, deck = None):
        """If deck is provided, use it instead of generating a new one. Otherwise, create a standard deck with num_decks."""
        if deck is not None:
            self.cards = deck
        else:
            self.cards = []
            for _ in range(num_decks):
                for suit in suits:
                    for name, weight in zip(cards, cardsPrice):
                        self.cards.append(CARD(suit, name, weight))
        self.x=None
        self.y=None
        self.angle = 0 #Just for easy access, not actually used for drawing/positioning since each card tracks its own rotation and position
        self.rotation = 0
    
    def shuffle(self):
        """Shuffle the deck using random.shuffle."""
        random.shuffle(self.cards)
    
    def flip_all(self, side: str = None):
        """Flip all cards to the specified side ('front' or 'back')."""
        for i in range(len(self.cards)):
            card = self.cards[i]
            if side is None:
                side = "back" if card.side == "front" else "front"
            if side not in ["front","back"]:
                side = "front"
            if card.side != side:
                if side == "back":
                    name = None
                else:
                    name = card.name
                card.surface = card.suit.draw(name, 0, 0, card.font_size, card_color=card.card_color, rotation=card.rotation)
                card.side = side
    
    def flip_card(self, index: int, side: str = None):
        """Flip a specific card at index to the specified side ('front' or 'back')."""
        index = index % len(self.cards)
        card = self.cards[index]
        if side is None:
            side = "back" if card.side == "front" else "front"
        if side not in ["front","back"]:
            side = "front"
        if card.side != side:
            if side == "back":
                name = None
            else:
                name = card.name
            card.surface = card.suit.draw(name, 0, 0, card.font_size, card_color=card.card_color, rotation=card.rotation)
            card.side = side

    def pick_card(self):
        """Draw a card from the top of the deck. Returns None if the deck is empty."""
        if len(self.cards) == 0:
            return None
        return self.cards.pop(0)
    
    def add_card(self, card):
        """Add a card to the Top of the deck."""
        self.cards.append(card)
    
    def resize(self, size):
        """Change Size of the deck."""
        for card in self.cards:
            card.resize(size)

    def card(self, index):
        """Get the card at the specified index without removing it from the deck."""
        return self.cards[index % len(self.cards)]
    
    def pos(self, x, y):
        """Set the position of all cards in the deck to (x, y)."""
        self.x = x
        self.y = y
        for card in self.cards:
            card.set_pos(x, y)

    def move(self, x_offset, y_offset):
        """Add x_offset to x and y_offset to y"""
        self.x += x_offset
        self.y += y_offset
        for card in self.cards:
            card.set_pos(card.x + x_offset, card.y + y_offset)

    def draw(self, shadow=False, shadow_alpha=128, shadow_offset=(5, 5), hover:bool=False, hover_offset:float=6, front_hover = False):
        """Draw all cards in the deck."""
        for card in self.cards:
            card.draw(shadow=shadow, shadow_alpha=shadow_alpha, shadow_offset=shadow_offset,hover=hover,hover_offset=hover_offset, front_hover=front_hover)

    def draw_as_hand(self, center_ellipse:pg.rect.Rect, spacing=10, middle_angle:int = None, shadow=True, shadow_alpha=128, shadow_offset=(5, 5), hover:bool=False, hover_offset:float=6, front_hover = False, exclude_cards=None):
        total_cards = len(self.cards)
        if total_cards == 0:
            return
        if exclude_cards is None:
            exclude_cards = []
        if middle_angle is None:
            middle_angle = self.angle

        if total_cards % 2 == 0: #Even number of cards
            start_angle = middle_angle + spacing/2 + (total_cards//2 - 1) * spacing
        else: #Odd number of cards
            start_angle = middle_angle + (total_cards//2) * spacing
            
        for index, card in enumerate(self.cards):
            if card in exclude_cards:
                continue
            angle = start_angle - index * spacing
            card.set_pos(*point_c(angle, center_ellipse.centerx, center_ellipse.centery, center_ellipse.width, center_ellipse.height))
            card.rotate(-(angle-90) - card.rotation) #Rotate card to match its position on the ellipse
            card.draw(shadow=shadow, shadow_alpha=shadow_alpha, shadow_offset=shadow_offset,hover=hover,hover_offset=hover_offset, front_hover=front_hover)   
    
    def rotate(self, angle=int):
        self.rotation = (self.rotation + angle) % 360
        for card in self.cards:
            card.rotate(angle)

#Objects
 #Menu
menuBackground = IMAGE("Blackjack/GreenBackground3.jpg", -40, 0, 1600, 600)
menuText1 = TEXT("Black Jack", 400, 100, font_size=64, color=(255, 255, 255))
menuButton1 = TEXT("Play", 550, 225, mode="topleft", font_size=32, color=(255, 255, 255), hover_color=(220, 50, 50))
menuButton2 = TEXT("Edit Settings", 550, 300, mode="topleft", font_size=32, color=(255, 255, 255), hover_color=(220, 50, 50))
menuButton3 = TEXT("Exit", 550, 375, mode="topleft", font_size=32, color=(255, 255, 255), hover_color=(220, 50, 50))
 #Play
  #Turns
hitButton = TEXT("Hit", 375, 390, mode="topleft", font_size=32, color=(225,225, 225), hover_color=(220, 50, 50))
stayButton = TEXT("Stay", 375, 425, mode="topleft", font_size=32, color=(225,225, 225), hover_color=(220, 50, 50))
  #vars
playBackground = IMAGE("Blackjack/GreenBackground1.jpg", -40, 0, 1600, 600)
card_index = 0
deckCreate_speed = 1
play_mode = "create deck"
player_index = 0
ai_index = 0
angle =0
decks = [] #[Ai, Players, Dealer]
deck_index = 0
decks_turning = 0
deck_speed = 1
turned = 0
selected_card = None  # For moving clicked card to bottom right
last_card = None  # To track the last card drawn for animation
selected_card_size = 90
#Settings
settingsBackground = IMAGE("Blackjack/GreenBackground2.jpg", 0, 0, 800, 800)
numDecks = 1
numPlayers = 1
numAi = 2
pixelize = False
numPixels = 2
num_delt = 2
    #Text
numDecksText = TEXT("Number of Decks:", 260, 50, font_size=34, color=(255, 255, 255),mode="topleft")
numPlayerText = TEXT("Number of Players:", 260, 100, font_size=34, color=(255, 255, 255),mode="topleft")
numAiText = TEXT("Number of AI:", 260, 150, font_size=34, color=(255, 255, 255),mode="topleft")
numDeltText = TEXT("Cards per Player:", 260, 200, font_size=34, color=(255, 255, 255),mode="topleft")
pixelizedText = TEXT("Pixelized:", 260, 250, mode="topleft", font_size=34, color=(255, 255, 255))
invalidInputText = TEXT("Invalid Input!", 400, 400, mode="center", font_size=60, color=(255, 0, 0))
numPixelText = TEXT("Pixel Density:", 260, 300, mode="topleft", font_size=34, color=(255, 255, 255))
    #Buttons
numDeckButton = TEXT(f"{numDecks}", 495, 65, mode="center", font_size=34, color=(255, 255, 255), hover_color=(220, 50, 50))
numPlayerButton = TEXT(f"{numPlayers}", 495, 115, mode="center", font_size=34, color=(255, 255, 255), hover_color=(220, 50, 50))
numAiButton = TEXT(f"{numAi}", 495, 165, mode="center", font_size=34, color=(255, 255, 255), hover_color=(220, 50, 50))
numDeltButton = TEXT(f"{num_delt}", 495, 215, mode="center", font_size=34, color=(255, 255, 255), hover_color=(220, 50, 50))
pixelizedButton = TEXT("On" if pixelize else "Off", 495, 265, mode="center", font_size=34, color=(255, 255, 255), hover_color=(220, 50, 50))
numPixelButton = TEXT(f"{numPixels}", 495, 315, mode="center", font_size=34, color=(255, 255, 255), hover_color=(220, 50, 50))
settingButton1 = TEXT("Save", 400, 500, mode="center", font_size=60, color=(255, 255, 255), hover_color=(220, 50, 50))


#vars
running = True
mode = "menu"
suits = [SUIT("Hearts", "♥", (255, 0, 0)), SUIT("Diamonds", "♦", (255, 0, 0)), SUIT("Clubs", "♣", (0, 0, 0)), SUIT("Spades", "♠", (0, 0, 0))]
gameDeck = DECK(num_decks=numDecks)
gameDeck.shuffle()
gameDeck.flip_all("back")
gameDeck.resize(20)
tempDeck = DECK(deck=[])  # Create a temporary deck to animate, moved outside the loop
keyPressed = None
card = CARD(suits[0],"0",0) #temp card
deckEllipse = pg.rect.Rect(0,0,667,469)
deckEllipse.center = (400,300)
mouse_click_pos = None

while running:
    try:
        screen.fill((0, 153, 0)) #Clear screen for each frame

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                keyPressed = event.key
            if event.type == pg.KEYUP:
                keyPressed = None
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                mouse_click_pos = event.pos
                
        match mode:
            case "menu":
                menuBackground.draw()
                menuText1.draw()
                menuButton1.draw()
                menuButton2.draw()
                menuButton3.draw()
                menuButton1.is_clicked() and (mode := "play")  # Switch to play mode if clicked
                menuButton1.is_clicked() and (play_mode := "setup vars")
                menuButton2.is_clicked() and (mode := "settings")  # Switch to settings mode if clicked
                menuButton3.is_clicked() and (running := False)  # Exit if clicked  # Example card drawing
            case "play":
                playBackground.draw()
                match play_mode:
                    case "setup vars":
                        gameDeck.cards = []
                        gameDeck = DECK(num_decks=numDecks)
                        tempDeck.cards = []
                        gameDeck.shuffle()
                        gameDeck.flip_all("back")
                        gameDeck.resize(20)
                        card_index = 0
                        deckCreate_speed = 1
                        player_index = 0
                        ai_index = 0
                        angle =0
                        decks = [] #[Ai, Players, Dealer]
                        deck_index = 0
                        play_mode = "create deck"
                        decks_turning = 0
                        turned = 0
                        selected_card = None
                        last_card = None
                    case "create deck":
                        tempDeck.draw(shadow=True, shadow_alpha=50)  # Draw all cards in the temporary deck
                        if card_index < len(gameDeck.cards):
                            card = gameDeck.card(card_index)

                            if keyPressed == pg.K_SPACE:   # Speed up animation when space is held
                                deckCreate_speed = lerp(5, deckCreate_speed, 0.1)
                            elif keyPressed == pg.K_RETURN:
                                for i in range(card_index, len(gameDeck.cards)): #End animation
                                    gameDeck.resize(start_size)
                                    gameDeck.card(i).set_pos(400, 300)  # Set all remaining cards to the center
                                    gameDeck.card(i).resize(30)  # Ensure all cards are the correct size
                                    gameDeck.card(i).rotate(random.uniform(-8, 8))  # Add some random rotation for visual interest
                                    gameDeck.card(i).set_pos(random.randint(397, 403), random.randint(297, 303))  # Start from the left edge
                                    tempDeck.add_card(gameDeck.card(i))
                                card_index = len(gameDeck.cards)  # Skip to the end of the deck
                            else:
                                deckCreate_speed = lerp(1, deckCreate_speed, 0.75)  # Normal speed when space is not held

                            if card.y <= 0:
                                card.rotate(random.uniform(-8, 8))
                                card.set_pos(random.randint(397, 403), -10)  # Start from the left edge
                                start_size = 20
                                card.resize(card.font_size * 2)  # Start larger for dramatic effect

                            card.resize(round(max(start_size, card.font_size - deckCreate_speed)))  # Gradually shrink to normal size
                            card.set_pos(card.x, lerp(317, card.y, deckCreate_speed))
                            if card.y >= 301:  # Snap to final position and next
                                card.set_pos(card.x, random.randint(297, 303))
                                card.resize(start_size)  # Ensure final size is correct
                                tempDeck.add_card(card)
                                card_index += 1

                            card.draw(shadow=True)
                        else: #End creation of deck
                            play_mode = "deal down"
                            gameDeck.cards = tempDeck.cards  # Replace gameDeck with the animated tempDeck
                            gameDeck.resize(start_size)
                    case "deal down":
                        gameDeck.draw(shadow=True, shadow_alpha=50)
                        if decks==[]: #Start of dealing
                            totalPlayers = numAi+numPlayers+1
                            angle = 90 #Starting angle
                            for d in range(0,totalPlayers): #Set up Decks
                                xy = point_c(angle,400,300,deckEllipse.width,deckEllipse.height)
                                decks.append(DECK(deck=[]))
                                decks[d].pos(xy[0],xy[1])
                                decks[d].resize(20)
                                decks[d].angle = angle
                                angle -= 360/totalPlayers
                            angle = 90 #Return to starting angle

                            #Setup First card and Deck
                            deck = decks[deck_index]
                            deck.resize(20)
                            deck.add_card(gameDeck.card(-1))
                            gameDeck.cards[-1] = "~"  #Set card for easy removal
                            gameDeck.cards.remove("~") #Remove Card
                            card = deck.cards[-1]
                            target_x = deck.x
                            target_y = deck.y
                            target_r = angle+270 #Rotation
                            side = "back"
                            deck.flip_card(-1, side)
                            card.rotation = 0

                        #Modify Card Values
                        card.x = round(lerp(target_x,card.x,1.5))
                        card.y = round(lerp(target_y,card.y,1.5))
                        card.rotation = round(lerp(target_r,card.rotation,3.5))

                        if in_ballpark(card.x, target_x) and in_ballpark(card.y, target_y): #Give some wiggle room
                            card.x = target_x #Set values to target
                            card.y = target_y
                            card.rotation = target_r
                            #Next deck
                            deck_index += 1 #Next deck
                            if deck_index == len(decks) or len(gameDeck.cards) <= 0: #loop if run of decks
                                side = "front"
                                deck_index = 0
                                if len(deck.cards) == num_delt or len(gameDeck.cards) <= 0: #End dealing ******
                                    deck_index = 0
                                    play_mode = "turns"
                                    continue
                            #New Card

                            angle += 360/totalPlayers
                            deck = decks[deck_index]
                            deck.resize(20)
                            deck.add_card(gameDeck.card(-1)) #Add a copy of card to deck
                            gameDeck.cards[-1] = "~"
                            gameDeck.cards.remove("~")#Remove orignal Card
                            card = deck.cards[-1]
                            target_x = deck.x
                            target_y = deck.y
                            target_r = angle+270 #Rotation
                            deck.flip_card(-1,side=side)
                            card.rotation = 0 #Looks better


                        for index,i in enumerate(decks): #Draw Decks
                            i.resize(20) #Just for insurance
                            decks[index].draw()
                    case "turns":
                        if stayButton.is_clicked() and decks_turning <= 0:
                            deck_index+=1
                            decks_turning = 360/totalPlayers
                        if deck_index+1 > len(decks): #Everyone played
                            play_mode = None #End Game

                    # Apply rotation to all decks if turning is active
                        if decks_turning > 0:
                            selected_card = None  # Deselect any selected card during rotation
                            turned += 5 * deck_speed
                            for index, i in enumerate(decks):
                                i.angle += 5 * deck_speed
                                xy = point_c(i.angle, deckEllipse.centerx, deckEllipse.centery, deckEllipse.width, deckEllipse.height)
                                i.move(xy[0]-i.x,xy[1]-i.y)
                                i.rotate(-5 * deck_speed)
                        decks_turning -= 5 * deck_speed  # Decrement only once per frame
                        
                        if turned >= 360/totalPlayers: #Reset angles after full turn
                            decks_turning = 0
                            for index, i in enumerate(decks):
                                for n in range(0, int(turned/(5 * deck_speed))):
                                    i.angle -= 5 * deck_speed #Reset angle to original position
                                    i.rotate(5 * deck_speed) #Reset rotation to original position
                                i.angle += 360/totalPlayers #Set angle to new position
                                i.rotate(-360/totalPlayers) #Rotate to new position
                                xy = point_c(i.angle, deckEllipse.centerx, deckEllipse.centery, deckEllipse.width, deckEllipse.height)
                                i.pos(xy[0],xy[1])
                            turned = 0


                        # Draw
                        gameDeck.draw(shadow=True, shadow_alpha=50)  # Draw the main deck in the center
                        for index, i in enumerate(decks): #Decks
                            i.resize(20)  # Just for insurance
                            exclude = [selected_card] if selected_card and selected_card in i.cards else []
                            if decks_turning > 0:
                                i.draw_as_hand(deckEllipse, shadow=True, shadow_alpha=50, exclude_cards=exclude)  # Draw each deck as a hand with its current angle and shadow
                            i.draw_as_hand(deckEllipse,shadow=True, shadow_alpha=50, hover=True, hover_offset = 20, front_hover=True, exclude_cards=exclude)  # Draw each deck as a hand with its current angle
                        #Buttons
                        if decks_turning <= 0: #Only show buttons when not turning
                            hitButton.draw()
                            stayButton.draw()
                            
                            # Handle card clicks
                            if 'mouse_click_pos' in globals() and mouse_click_pos is not None:                            
                                for deck in decks:
                                    for card in deck.cards:
                                        if selected_card and card == selected_card:
                                            selected_card.resize(selected_card_size)
                                        if card.side == "front" and card.is_clicked(mouse_click_pos):
                                            last_card = selected_card
                                            if selected_card == card:
                                                selected_card = None  # Deselect if the same card is clicked again
                                            else:
                                                selected_card = card
                                            break
                                mouse_click_pos = None  # Reset after handling
                        
                        # Draw selected card at bottom right if exists
                        if selected_card:
                            selected_card.set_pos(690, 700)  # Bottom right position
                            selected_card.rotate(-selected_card.rotation)  # Reset rotation
                            selected_card.resize(selected_card_size)
                            selected_card.draw(shadow=True, shadow_alpha=50)  # Draw selected card without additional hover effect     
                    case _:
                        mode = "menu"
            case "settings":
                settingsBackground.draw()
                numDecksText.draw()
                numPlayerText.draw()
                numAiText.draw()
                numDeckButton.draw()
                numPlayerButton.draw()
                numAiButton.draw()
                settingButton1.draw()
                pixelizedText.draw()
                pixelizedButton.draw()
                numDeltText.draw()
                numDeltButton.draw()
                if pixelize: numPixelText.draw()
                if pixelize: numPixelButton.draw()
                if pixelize and numPixelButton.is_released():
                    numPixels = (numPixels % 6) + 1  # Cycle from 2 to 6
                    if numPixels == 1: numPixels = 2
                    numPixelButton.change_text(f"{numPixels}")
                if numDeckButton.is_released():
                    numDecks = ((numDecks) % 5)+1 # Cycle from 1 to 5
                    numDeckButton.change_text(f"{numDecks}")
                if numPlayerButton.is_released():
                    numPlayers = (numPlayers + 1) % 11  # Cycle from 0 to 10
                    numPlayerButton.change_text(f"{numPlayers}")
                if numAiButton.is_released():
                    numAi = (numAi + 1) % 11  # Cycle from 0 to 10
                    numAiButton.change_text(f"{numAi}")
                if pixelizedButton.is_released():
                    pixelize = not pixelize
                    pixelizedButton.change_text("On" if pixelize else "Off")
                if numDeltButton.is_released():
                    num_delt = ((num_delt) % 5)+1 # Cycle from 1 to 5
                    numDeltButton.change_text(f"{num_delt}")
                if settingButton1.is_clicked() or settingButton1.is_released():
                    if numPlayers + numAi == 0:
                        invalidInputText.draw()
                    else:
                        mode = "menu"
        if pixelize: pixelize_screen(numPixels)
        pg.display.flip()
        clock.tick(60)
    except KeyboardInterrupt:
        continue
pg.quit()