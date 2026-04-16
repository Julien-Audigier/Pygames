import os
import pygame
import math
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # To avoid audio errors on systems without sound
pygame.init()
pygame.font.init()

# Set up the game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Clicker")

# Define colors
DARKRED = (139, 0, 0)
DARKGRAY = (64, 64, 64)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEONGREEN = (44,255,5)

#Functions
def round(var):
    if math.ceil(var) <= var+0.5:
        return math.ceil(var)
    return math.floor(var)

def lerp(end: float, var: float, speed: float=2.5):
   return var+(end-var)*speed/10

def draw_text(text: str, color: list, x: float, y: float, font: pygame.font.Font, mode=0,size_factors=[1,1], surface = screen):
    text_surf = font.render(text, True, color)
    text_surf = pygame.transform.smoothscale(text_surf, (int(text_surf.width * size_factors[0]), int(text_surf.height * size_factors[1])))
    text_rect = text_surf.get_rect(center=(x, y))
    if mode == 1:
        text_rect.left = x
        text_rect.centery = y
    elif mode == 2:
        text_rect.right = x
        text_rect.centery = y
    surface.blit(text_surf, text_rect)

def draw_percent(x,y,width,height,dividend,divisor,font_path,screen=screen):
    pygame.draw.rect(screen,DARKGRAY,pygame.rect.Rect(x-width/2,y-height/2,width, height))
    perWidth = (dividend*width)/divisor
    if perWidth >= width:
        perWidth = width
    pygame.draw.rect(screen, NEONGREEN,pygame.rect.Rect(x-width/2,y-height/2,perWidth, height))
    pygame.draw.rect(screen, BLACK, pygame.rect.Rect(x-width/2,y-height/2,width, height),10)
    draw_text("".join([str(round(perWidth/width*100)), "%"]),WHITE, x, y,pygame.font.Font(font_path, int(height/2)))

#Classes
class OBJECT:
    def __init__(self, x, y, width, height, visable = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.rect.Rect(x-width/2, y-height/2, width, height)
        self.visable = visable

    def pos(self,item = "~"):
        match item:
            case "~":
                return [self.x,self.y]
            case 1:
                return self.y
            case 0:
                return self.x

    def move_pos(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.rect.Rect(self.x-self.width/2, self.y-self.height/2, self.width, self.height)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.rect = pygame.rect.Rect(self.x-self.width/2, self.y-self.height/2, self.width, self.height)

class IMAGE:
    def __init__(self, path, x, y, width, height):
        self.image = pygame.image.load(path).convert_alpha()
        self.ORGimage = self.image.copy()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def pos(self,item = "~"):
        match item:
            case "~":
                return [self.x,self.y]
            case 1:
                return self.y
            case 0:
                return self.x

    def resize(self, width, height):
        self.image = pygame.transform.scale(self.ORGimage, (width, height))
        self.width = width
        self.height = height
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def move_pos(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface=screen):
        surface.blit(self.image, self.rect)

class IMAGE_GROUP:
    def __init__(self, x:int, y:int, width:int, height:int, Num_Images:int, Folder_Name:str="Image_Sprites", Sprite_Name:str="Image_"):
        self.FOLDER_NAME = Folder_Name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.index=0
        self.numImages = Num_Images
        self.ARRimages = []
        for i in range(0, Num_Images):
            try:
                self.ARRimages.append(IMAGE("".join(["Clicker/",Folder_Name,"/",Sprite_Name, str(i),".png"]),x,y,width,height))
            except FileNotFoundError:
                self.ARRimages.append(IMAGE("".join(["Clicker/",Folder_Name,"/",Sprite_Name, str(i),".jpeg"]),x,y,width,height))

    def rect(self):
        return self.ARRimages[self.index].rect
    
    def pos(self,item = "~"):
        match item:
            case "~":
                return [self.x,self.y]
            case 1:
                return self.y
            case 0:
                return self.x

    def move_pos(self, x, y):
        for i in range(0, len(self.ARRimages)):
            self.ARRimages[i].move_pos(x,y)

    def resize(self, width, height):
        self.width = width
        self.height = height
        for i in range(0, len(self.ARRimages)):
            self.ARRimages[i].resize(width, height)

    def draw(self, index = None):
        if index == None:
            index = self.index
        self.ARRimages[index].draw()

class BUTTON:
    def __init__(self,x,y,width,height,NAME_,num_images,TEXT,TEXT_COLOR,TEXT_x,TEXT_y,FONT, price = 0):
        self.TEXT = TEXT
        self.TEXT_COLOR = TEXT_COLOR
        self.TEXT_x = TEXT_x
        self.TEXT_y = TEXT_y
        self.FONT = FONT
        self.price = price
        self.size_factors = [1,1]
        self.ORG_size = [width,height]
        self.IMAGES = IMAGE_GROUP(x,y,width,height,num_images,"".join([NAME_, "Sprites"]),NAME_)

    def pos(self,item = "~"):
        match item:
            case "~":
                return self.IMAGES.pos()
            case 1:
                return self.IMAGES.y
            case 0:
                return self.IMAGES.x

    def size(self,item = 1):
        match item:
            case 2:
                return [self.IMAGES.width,self.IMAGES.height]
            case 1:
                return self.IMAGES.height
            case 0:
                return self.IMAGES.width
    
    def rect(self):
        return self.IMAGES.rect()
    
    def move_pos(self, x, y):
        self.IMAGES.move_pos(x,y)

    def resize(self, width, height):
        self.size_factors = [width/self.ORG_size[0],height/self.ORG_size[1]]
        self.IMAGES.resize(width, height)

    def draw(self, mode = 0, surface=screen):
        self.IMAGES.draw()
        draw_text(self.TEXT, self.TEXT_COLOR,self.pos(0)+self.TEXT_x*self.size_factors[0],self.pos(1)+self.TEXT_y*self.size_factors[1], self.FONT, mode, self.size_factors,screen)

class SCROLL_BOX:
    def __init__(self,x,y,width,height, Objects,):
        self.CenterObject = OBJECT(x,y,width,height)
        self.REL_y = 0
        self.Objects=Objects

    def pos(self, item:int = "~", index:int = "~"):
        if index == "~": #For CenterObject
            match item:
                case 0:
                    return self.CenterObject.x
                case 1:
                    return self.CenterObject.y
                case "~":
                    return [self.pos(0),self.pos(1)]
    
    def scroll(self, amount):
        self.REL_y += amount
        for object in self.Objects:
            pass
                
#Declaring
Cookie = IMAGE_GROUP(200, 300, 170, 170, 6, "Cookie_Sprites", "Cookie_")
score = 0
numCookies = 1
genTime = 4000
genStart = 0
cookieMax = 1
grandmaButton = BUTTON(600,300,156,60,"Grandma_",1,"Price: 0", BLACK,-72,12,pygame.font.Font("Clicker/PixelGamingRegular-d9w0g.ttf",17),15)

running = True
clock = pygame.time.Clock()
while running:
    if (pygame.time.get_ticks() >= genStart+genTime) and (numCookies < cookieMax):
        numCookies += 1
        genStart = pygame.time.get_ticks()
    if numCookies == cookieMax:
        genStart = pygame.time.get_ticks()
    
    mousePOS = pygame.mouse.get_pos()
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            if Cookie.rect().collidepoint(mousePOS[0], mousePOS[1]) and Cookie.index != 5: #Clicked Cookie
                Cookie.index = (1+Cookie.index)%Cookie.numImages
                if Cookie.index == 5:
                    score += 1

    if numCookies >= 1 and Cookie.index == 5:
        numCookies-=1
        Cookie.index = 0


    if Cookie.rect().collidepoint(mousePOS[0], mousePOS[1]):
        Cookie.resize(lerp(190,Cookie.width),lerp(190,Cookie.height))
    else:
        Cookie.resize(lerp(170,Cookie.width), lerp(170,Cookie.height))
    Cookie.draw()
    if grandmaButton.rect().collidepoint(mousePOS[0], mousePOS[1]):
        grandmaButton.resize(lerp(163.8,grandmaButton.size(0)),lerp(63,grandmaButton.size(1)))
    else:
        grandmaButton.resize(lerp(156,grandmaButton.size(0)), lerp(60,grandmaButton.size(1)))
    grandmaButton.draw(1)
    draw_percent(200,20,400,40,pygame.time.get_ticks()-genStart,genTime,"Clicker/PixelGamingRegular-d9w0g.ttf")
    draw_text(str(score), BLACK, 200, 120, pygame.font.Font("Clicker/PixelGamingRegular-d9w0g.ttf",50))
    draw_text("".join(["Cookies In Stock: ", str(numCookies)]), BLACK, 5, 55, pygame.font.Font("Clicker/PixelGamingRegular-d9w0g.ttf",20), 1)
    pygame.display.flip()
    clock.tick(60)