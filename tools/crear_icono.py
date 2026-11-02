from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 512
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 1. Fondo degradado azul oscuro
for y in range(SIZE):
    t = y / SIZE
    r = int(15 + t * 25)
    g = int(20 + t * 25)
    b = int(45 + t * 50)
    draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# 2. Patrón de ajedrez sutil
square = SIZE // 8
checker = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
cd = ImageDraw.Draw(checker)
for row in range(8):
    for col in range(8):
        if (row + col) % 2 == 0:
            cd.rectangle([col*square, row*square, (col+1)*square, (row+1)*square],
                         fill=(255, 255, 255, 8))
img = Image.alpha_composite(img, checker)
draw = ImageDraw.Draw(img)

# 3. Resplandor azul detrás de la pieza
glow = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([SIZE//2 - 200, SIZE//2 - 200, SIZE//2 + 200, SIZE//2 + 200],
           fill=(70, 130, 200, 130))
glow = glow.filter(ImageFilter.GaussianBlur(70))
img = Image.alpha_composite(img, glow)
draw = ImageDraw.Draw(img)

# 4. Cargar fuente con glifos de ajedrez
font_paths = [
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]
font = None
for fp in font_paths:
    try:
        font = ImageFont.truetype(fp, 340)
        break
    except Exception:
        continue
if font is None:
    font = ImageFont.load_default()

# 5. Dibujar el Rey de ajedrez dorado (♚) con sombra y brillo
text = "♚"
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = (SIZE - tw) // 2 - bbox[0]
ty = (SIZE - th) // 2 - bbox[1] - 30

# Sombra
draw.text((tx + 8, ty + 8), text, font=font, fill=(0, 0, 0, 170))
# Rey dorado
draw.text((tx, ty), text, font=font, fill=(250, 210, 90, 255))
# Reflejo superior
draw.text((tx - 2, ty - 2), text, font=font, fill=(255, 245, 200, 90))

# 6. Robot del coach en la esquina inferior derecha
rx, ry = SIZE - 85, SIZE - 85
rs = 42

# Antena
draw.line([(rx, ry - rs - 5), (rx, ry - rs - 28)], fill=(200, 200, 200), width=4)
draw.ellipse([rx - 8, ry - rs - 38, rx + 8, ry - rs - 22], fill=(255, 80, 80))

# Orejas
draw.rounded_rectangle([rx - rs - 10, ry - 10, rx - rs - 2, ry + 18], radius=3, fill=(80, 130, 180))
draw.rounded_rectangle([rx + rs + 2, ry - 10, rx + rs + 10, ry + 18], radius=3, fill=(80, 130, 180))

# Cabeza
draw.rounded_rectangle(
    [rx - rs, ry - rs + 8, rx + rs, ry + rs],
    radius=14, fill=(100, 160, 220), outline=(255, 255, 255), width=3
)

# Ojos
draw.ellipse([rx - 20, ry - 12, rx - 4, ry + 4], fill=(40, 40, 40))
draw.ellipse([rx + 4, ry - 12, rx + 20, ry + 4], fill=(40, 40, 40))
# Brillo de ojos
draw.ellipse([rx - 18, ry - 10, rx - 11, ry - 3], fill=(255, 255, 255))
draw.ellipse([rx + 6, ry - 10, rx + 13, ry - 3], fill=(255, 255, 255))

# Sonrisa
draw.arc([rx - 16, ry + 10, rx + 16, ry + 28], 0, 180, fill=(40, 40, 40), width=3)

# 7. Bordes redondeados
mask = Image.new('L', (SIZE, SIZE), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([0, 0, SIZE, SIZE], radius=95, fill=255)
final = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
final.paste(img, (0, 0), mask)
img = final

# 8. Borde exterior brillante
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([3, 3, SIZE - 4, SIZE - 4], radius=92,
                       outline=(70, 150, 220, 255), width=5)

# Guardar
img.save('assets/icon.png')
print("✅ Icono creado en assets/icon.png")
