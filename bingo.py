import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Adicione esta importação
import sqlite3
import random
from datetime import datetime

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("bingo.db")
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS rodadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS numeros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rodada_id INTEGER,
    numero INTEGER,
    FOREIGN KEY (rodada_id) REFERENCES rodadas(id)
)
""")
conn.commit()

# Configurações padrão
DEFAULT_MIN_NUM = 1
DEFAULT_MAX_NUM = 75

numeros_sorteados = []
bingo_ativado = False
config = {
    'min_num': DEFAULT_MIN_NUM,
    'max_num': DEFAULT_MAX_NUM
}

# Cores temáticas
COLORS = {
    'background': '#F8F1E5',  # Bege claro
    'primary': '#8B0000',     # Vermelho escuro (sangue de Cristo)
    'secondary': '#1E3F66',   # Azul mariano
    'accent': '#C9A227',      # Dourado (elementos sagrados)
    'text': '#333333',        # Texto escuro
    'highlight': '#FFFFFF'    # Branco puro
}

# Fonte temática
FONT_TITLE = ("Poppins", 45, "bold")
FONT_NUMBER = ("Poppins", 250, "bold")
FONT_BUTTON = ("Poppins", 28, "bold")
FONT_TEXT = ("Poppins", 24)
FONT_SMALL = ("Poppins", 20)

# Função para sortear um número
def sortear_numero():
    if bingo_ativado:
        return

    if len(numeros_sorteados) >= (config['max_num'] - config['min_num'] + 1):
        messagebox.showinfo("Aviso", "Todos os números já foram sorteados!")
        return

    numero = random.randint(config['min_num'], config['max_num'])
    tentativas = 0
    max_tentativas = (config['max_num'] - config['min_num'] + 1) * 2
    
    while numero in numeros_sorteados and tentativas < max_tentativas:
        numero = random.randint(config['min_num'], config['max_num'])
        tentativas += 1
    
    if tentativas >= max_tentativas:
        messagebox.showinfo("Aviso", "Não há mais números disponíveis para sorteio!")
        return

    numeros_sorteados.append(numero)
    numero_label.config(text=f"{numero}", font=FONT_NUMBER, fg=COLORS['primary'])
    atualizar_rodadas()

# Atualizar exibição dos números sorteados
def atualizar_rodadas():
    rodadas_label.config(text=f"Números Sorteados ({len(numeros_sorteados)}):\n" + ", ".join(map(str, numeros_sorteados)), 
                        font=FONT_TEXT, fg=COLORS['text'])

# Finalizar rodada e salvar no banco
def bingo():
    global bingo_ativado
    
    if not numeros_sorteados:
        return
    
    bingo_ativado = True
    numero_label.config(text="BINGO!", font=FONT_NUMBER, fg=COLORS['primary'])
    sortear_button.config(state="disabled")
    bingo_button.config(state="disabled")
    
    # Frame para os botões de ação do Bingo
    bingo_action_frame = tk.Frame(frame_bingo, bg=COLORS['background'])
    bingo_action_frame.pack(pady=20)
    
    def continuar_rodada():
        global bingo_ativado
        bingo_ativado = False
        numero_label.config(text=f"{numeros_sorteados[-1]}", font=FONT_NUMBER, fg=COLORS['primary'])
        sortear_button.config(state="normal")
        bingo_button.config(state="normal")
        bingo_action_frame.pack_forget()
    
    def terminar_rodada():
        cursor.execute("INSERT INTO rodadas (data) VALUES (?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
        rodada_id = cursor.lastrowid

        for numero in numeros_sorteados:
            cursor.execute("INSERT INTO numeros (rodada_id, numero) VALUES (?, ?)", (rodada_id, numero))

        conn.commit()
        atualizar_lista_rodadas()
        bingo_action_frame.pack_forget()
        nova_rodada_button.pack(pady=20)
    
    # Botão para continuar a rodada
    continuar_button = tk.Button(bingo_action_frame, text="Continuar Rodada", font=FONT_BUTTON, 
                               command=continuar_rodada, bg=COLORS['secondary'], fg=COLORS['highlight'], width=15)
    continuar_button.grid(row=0, column=0, padx=10)
    
    # Botão para terminar a rodada
    terminar_button = tk.Button(bingo_action_frame, text="Terminar Rodada", font=FONT_BUTTON, 
                              command=terminar_rodada, bg=COLORS['primary'], fg=COLORS['highlight'], width=15)
    terminar_button.grid(row=0, column=1, padx=10)

def nova_rodada():
    global bingo_ativado, numeros_sorteados
    bingo_ativado = False
    numeros_sorteados = []
    numero_label.config(text="Clique para Sortear", font=FONT_TITLE, fg=COLORS['secondary'])
    rodadas_label.config(text="Números Sorteados:", font=FONT_TEXT)
    sortear_button.config(state="normal")
    bingo_button.config(state="normal")
    nova_rodada_button.pack_forget()

# Configurações personalizadas
def abrir_configuracoes():
    config_window = tk.Toplevel(root)
    config_window.title("Configurações")
    config_window.geometry("400x250")
    config_window.resizable(False, False)
    config_window.grab_set()
    config_window.configure(bg=COLORS['background'])
    
    # Frame para configurações
    frame_config = tk.Frame(config_window, padx=20, pady=20, bg=COLORS['background'])
    frame_config.pack(fill=tk.BOTH, expand=True)
    
    # Intervalo de números
    tk.Label(frame_config, text="Intervalo de Números:", font=FONT_TEXT, 
             bg=COLORS['background'], fg=COLORS['text']).grid(row=0, column=0, sticky="w", pady=5)
    
    tk.Label(frame_config, text="De:", font=FONT_SMALL, 
             bg=COLORS['background'], fg=COLORS['text']).grid(row=1, column=0, sticky="w")
    min_entry = tk.Entry(frame_config, width=5, font=FONT_SMALL)
    min_entry.grid(row=1, column=1, sticky="w")
    min_entry.insert(0, str(config['min_num']))
    
    tk.Label(frame_config, text="Até:", font=FONT_SMALL, 
             bg=COLORS['background'], fg=COLORS['text']).grid(row=2, column=0, sticky="w")
    max_entry = tk.Entry(frame_config, width=5, font=FONT_SMALL)
    max_entry.grid(row=2, column=1, sticky="w")
    max_entry.insert(0, str(config['max_num']))
    
    # Botão Salvar
    def salvar_config():
        try:
            min_num = int(min_entry.get())
            max_num = int(max_entry.get())
            
            if min_num >= max_num:
                messagebox.showerror("Erro", "O número mínimo deve ser menor que o máximo!")
                return
                
            if min_num < 1:
                messagebox.showerror("Erro", "O número mínimo deve ser pelo menos 1!")
                return
                
            config['min_num'] = min_num
            config['max_num'] = max_num
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            config_window.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira números válidos!")
    
    save_button = tk.Button(frame_config, text="Salvar Configurações", command=salvar_config,
                          font=FONT_BUTTON, bg=COLORS['primary'], fg=COLORS['highlight'])
    save_button.grid(row=3, column=0, columnspan=2, pady=20)

# Prevenir fechamento acidental
def on_closing():
    if not bingo_ativado and len(numeros_sorteados) > 0:
        if messagebox.askyesno("Sair", "Há uma rodada em andamento. Deseja realmente sair?"):
            root.destroy()
    else:
        root.destroy()

# Criar janela principal
root = tk.Tk()
root.title("Bingo - Nossa Senhora do Monte Bérico")
root.attributes("-fullscreen", True)
root.configure(bg=COLORS['background'])
root.protocol("WM_DELETE_WINDOW", on_closing)

# Carregar a imagem de Nossa Senhora
try:
    img = Image.open("nossa-senhora.png")
    # Redimensionar mantendo a proporção (ajuste o tamanho conforme necessário)
    img.thumbnail((200, 200), Image.LANCZOS)
    nossa_senhora_img = ImageTk.PhotoImage(img)
except:
    nossa_senhora_img = None
    print("Imagem de Nossa Senhora não encontrada ou com problemas")

# Adicionar cabeçalho com título religioso
header_frame = tk.Frame(root, bg=COLORS['primary'])
header_frame.pack(fill=tk.X)

# Adicionar a imagem no canto esquerdo do cabeçalho
if nossa_senhora_img:
    img_label = tk.Label(header_frame, image=nossa_senhora_img, bg=COLORS['primary'])
    img_label.image = nossa_senhora_img  # Manter referência
    img_label.pack(side="left", padx=20)

title_label = tk.Label(header_frame, text="Bingo Beneficente - Nossa Senhora do Monte Bérico", 
                       font=FONT_TITLE, fg=COLORS['highlight'], bg=COLORS['primary'], pady=20)
title_label.pack(side="left", expand=True)

# Adicionar cabeçalho com título religioso
header_frame = tk.Frame(root, bg=COLORS['primary'])
header_frame.pack(fill=tk.X)

# Criar abas
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

style = ttk.Style()
style.configure("TNotebook", background=COLORS['background'])
style.configure("TNotebook.Tab", font=FONT_TEXT, background=COLORS['background'], 
                foreground=COLORS['text'])

# Criar aba do Bingo
frame_bingo = tk.Frame(notebook, bg=COLORS['background'])
notebook.add(frame_bingo, text="Sorteio")

# Frame container para centralizar todo o conteúdo verticalmente
center_container = tk.Frame(frame_bingo, bg=COLORS['background'])
center_container.pack(expand=True, fill='both')

# Frame para centralizar horizontalmente
center_frame = tk.Frame(center_container, bg=COLORS['background'])
center_frame.pack(expand=True)

# Criar aba das rodadas anteriores
frame_rodadas = tk.Frame(notebook, bg=COLORS['background'])
notebook.add(frame_rodadas, text="Histórico")

# Menu de configurações
menubar = tk.Menu(root, bg=COLORS['background'], fg=COLORS['text'])
config_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['background'], fg=COLORS['text'])
config_menu.add_command(label="Configurações", command=abrir_configuracoes, font=FONT_SMALL)
menubar.add_cascade(label="Opções", menu=config_menu)
root.config(menu=menubar)

# Número sorteado em destaque (agora dentro do center_frame)
numero_frame = tk.Frame(center_frame, bg=COLORS['background'])
numero_frame.pack(pady=40)

numero_label = tk.Label(numero_frame, text="Clique para Sortear", font=FONT_TITLE, 
                       bg=COLORS['background'], fg=COLORS['secondary'])
numero_label.pack()

# Botões (agora dentro do center_frame)
button_frame = tk.Frame(center_frame, bg=COLORS['background'])
button_frame.pack(pady=20)

sortear_button = tk.Button(button_frame, text="Sortear Número", font=FONT_BUTTON, command=sortear_numero, 
                         bg=COLORS['primary'], fg=COLORS['highlight'], width=15, height=1)
sortear_button.grid(row=0, column=0, padx=20)

bingo_button = tk.Button(button_frame, text="BINGO!", font=FONT_BUTTON, command=bingo, 
                       bg=COLORS['accent'], fg=COLORS['text'], width=10, height=1)
bingo_button.grid(row=0, column=1, padx=20)

nova_rodada_button = tk.Button(center_frame, text="Nova Rodada", font=FONT_BUTTON, command=nova_rodada, 
                             bg=COLORS['primary'], fg=COLORS['highlight'], width=15, height=1)

# Números sorteados (agora dentro do center_frame)
rodadas_frame = tk.Frame(center_frame, bg=COLORS['background'])
rodadas_frame.pack(pady=30)

rodadas_label = tk.Label(rodadas_frame, text="Números Sorteados:", font=FONT_TEXT, 
                        bg=COLORS['background'], fg=COLORS['text'])
rodadas_label.pack()

# Exibir rodadas anteriores
def atualizar_lista_rodadas():
    for widget in frame_rodadas.winfo_children():
        widget.destroy()

    cursor.execute("""
    SELECT r.id, r.data, GROUP_CONCAT(n.numero, ', ')
    FROM rodadas r
    JOIN numeros n ON r.id = n.rodada_id
    GROUP BY r.id
    ORDER BY r.id DESC
    """)
    rodadas = cursor.fetchall()

    scroll_frame = tk.Frame(frame_rodadas, bg=COLORS['background'])
    scroll_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(scroll_frame, bg=COLORS['background'])
    scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for rodada in rodadas:
        rodada_frame = tk.Frame(scrollable_frame, bg=COLORS['background'], pady=10)
        rodada_frame.pack(fill=tk.X)
        
        tk.Label(rodada_frame, text=f"Rodada {rodada[0]} - {rodada[1]}", 
                font=FONT_TEXT, bg=COLORS['background'], fg=COLORS['primary']).pack(anchor="w")
        tk.Label(rodada_frame, text=f"Números: {rodada[2]}", 
                font=FONT_SMALL, bg=COLORS['background'], fg=COLORS['text']).pack(anchor="w")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Atualizar rodadas no início
atualizar_lista_rodadas()

# Iniciar loop
root.mainloop()