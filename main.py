import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import font as tkfont
from PIL import Image, ImageTk  # para trabalhar com imagens

def analise_p():
    print("Análise P iniciada...")

def analise_d():
    print("Análise D iniciada...")

def criacao_i():
    print("Criação I iniciada...")

def analise_dates():
    print("Análise Dates iniciada...")

# --- Janela principal ---
app = ttk.Window(
    title="Painel de Análises - Maria Pitanga",
    themename="flatly",
    size=(1000, 800),
    resizable=(True, True)
)

# --- Configurações da grade ---
app.rowconfigure(1, weight=1)
app.columnconfigure(0, weight=1)

# --- Carrega e define o fundo ---
bg_image = Image.open("img.png")
bg_image = bg_image.resize((1000, 800), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

background_label = ttk.Label(app, image=bg_photo)
background_label.image = bg_photo
background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

# --- Cores e fontes ---
COR_TEXTO = "white"
title_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
footer_font = tkfont.Font(family="Arial", size=10)

# --- Título ---
titulo = ttk.Label(
    app,
    text="Painel de Análises e Criação",
    font=title_font,
    foreground=COR_TEXTO
    # background removido para evitar erro e “caixa” sólida
)
titulo.grid(row=0, column=0, pady=40, sticky="n")

# --- Frame central ---
frame_botoes = ttk.Frame(app, bootstyle="dark")
frame_botoes.grid(row=1, column=0, padx=40, pady=40, sticky="nsew")
frame_botoes.configure(style="TFrame")

for r in range(2):
    frame_botoes.rowconfigure(r, weight=1, uniform="rows")
for c in range(2):
    frame_botoes.columnconfigure(c, weight=1, uniform="cols")

# --- Estilo dos botões ---
style = ttk.Style()
style.configure(
    "Pitanga.TButton",
    font=("Helvetica", 14, "bold"),
    foreground=COR_TEXTO,
    background="#4B006E",
    padding=12,
    borderwidth=0
)
style.map(
    "Pitanga.TButton",
    background=[("active", "#7B1FA2")],
    relief=[("pressed", "sunken")]
)

# --- Botões ---
ttk.Button(frame_botoes, text="Análise P", command=analise_p, style="Pitanga.TButton")\
    .grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
ttk.Button(frame_botoes, text="Análise D", command=analise_d, style="Pitanga.TButton")\
    .grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
ttk.Button(frame_botoes, text="Criação I", command=criacao_i, style="Pitanga.TButton")\
    .grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
ttk.Button(frame_botoes, text="Análise Dates", command=analise_dates, style="Pitanga.TButton")\
    .grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

# --- Rodapé ---
rodape = ttk.Label(
    app,
    text="© 2025 Maria Pitanga - Assistência de TI",
    font=footer_font,
    foreground=COR_TEXTO
    # background removido (antes estava "#00000000")
)
rodape.grid(row=2, column=0, pady=10, sticky="s")

# --- Resize dinâmico da imagem de fundo ---
def on_resize(event):
    # Evita redimensionar com valores inválidos (0 ou negativos)
    w = max(1, int(event.width))
    h = max(1, int(event.height))

    try:
        new_bg = bg_image.resize((w, h), Image.LANCZOS)
        bg_photo_resized = ImageTk.PhotoImage(new_bg)
        background_label.configure(image=bg_photo_resized)
        background_label.image = bg_photo_resized  # mantém referência
    except Exception as e:
        # Log simples pra você ver se algo diferente acontecer
        print(f"[on_resize] erro ao redimensionar: {e} (w={w}, h={h})")


app.bind("<Configure>", on_resize)

# --- Executar app ---
app.mainloop()
