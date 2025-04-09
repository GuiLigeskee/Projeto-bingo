import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv

# Configuração do banco de dados
def setup_database():
    conn = sqlite3.connect("bingo.db")
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS numeros")
    cursor.execute("DROP TABLE IF EXISTS rodadas")
    
    cursor.execute("""
    CREATE TABLE rodadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE numeros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rodada_id INTEGER,
        numero INTEGER,
        letra TEXT,
        FOREIGN KEY (rodada_id) REFERENCES rodadas(id)
    )
    """)
    
    conn.commit()
    return conn, conn.cursor()

# Inicializar banco de dados
conn, cursor = setup_database()

# Variáveis globais
colunas_bingo = {'B': [], 'I': [], 'N': [], 'G': [], 'O': []}
bingo_ativado = False
DEFAULT_MIN_NUM = 1
DEFAULT_MAX_NUM = 75

# Configurações de tamanho
class Tamanhos:
    def __init__(self, root):
        self.root = root
        self.atualizar_tamanhos()
        
    def atualizar_tamanhos(self):
    # Altura disponível para a cartela (70% da altura da tela)
        altura_disponivel = int(self.root.winfo_screenheight() * 0.7)
        
        # Calcula altura das células (8 linhas + cabeçalho)
        self.ALTURA_CELULA = max(50, altura_disponivel // 9)  # Ajuste para 8 linhas
        
        # Define fontes
        tamanho_fonte_numeros = max(22, self.ALTURA_CELULA // 2)
        tamanho_fonte_cabecalho = int(tamanho_fonte_numeros * 1.2)
        
        self.FONTE_TITULO = ("Arial", 36, "bold")
        self.FONTE_NUMERO_SORTEADO = ("Arial", 120, "bold")
        self.FONTE_CABECALHO = ("Arial", tamanho_fonte_cabecalho, "bold")
        self.FONTE_NUMEROS = ("Arial", tamanho_fonte_numeros, "bold")
        self.FONTE_TEXTO = ("Arial", 18)
        self.FONTE_BOTAO = ("Arial", 20, "bold")
        self.FONTE_BINGO = ("Arial", 140, "bold")
        self.LARGURA_COLUNA = max(140, int(self.root.winfo_screenwidth() * 0.15))

# Cores
CORES = {
    'fundo': '#FFFFFF',
    'cabecalho': '#8B0000',
    'texto': '#000000',
    'destaque': '#C9A227',
    'botao': '#1E3F66',
    'cartela': '#FFFFFF',
    'borda': '#000000',
    'header_bg': '#8B0000',
    'header_fg': '#FFFFFF',
    'cell_bg': '#F8F8F8',
    'numero_sorteado': '#FF0000'
}

# Inicializar tamanhos
root = tk.Tk()
root.title("Bingo - Show de Prêmios (Telão)")
root.state('zoomed')  # Maximiza a janela
tamanhos = Tamanhos(root)

# Funções do jogo
def classificar_numero(numero):
    if 1 <= numero <= 15: return 'B'
    if 16 <= numero <= 30: return 'I'
    if 31 <= numero <= 45: return 'N'
    if 46 <= numero <= 60: return 'G'
    if 61 <= numero <= 75: return 'O'
    return None

def adicionar_numero():
    try:
        entrada = numero_entry.get().strip()
        if not entrada:
            messagebox.showerror("Erro", "Por favor, insira um número!")
            return
            
        numero = int(entrada)
        letra = classificar_numero(numero)
        
        if letra is None:
            messagebox.showerror("Erro", f"Número deve estar entre {DEFAULT_MIN_NUM} e {DEFAULT_MAX_NUM}")
            return
            
        if numero in colunas_bingo[letra]:
            messagebox.showerror("Erro", "Número já foi sorteado!")
            return
        
        colunas_bingo[letra].append(numero)
        colunas_bingo[letra].sort()
        numero_entry.delete(0, tk.END)
        numero_label.config(text=str(numero), font=tamanhos.FONTE_NUMERO_SORTEADO, fg=CORES['numero_sorteado'])
        atualizar_cartela()
        
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido (1-75)!")

def atualizar_cartela():
    for widget in tabela_frame.winfo_children():
        widget.destroy()
    
    # Configurar colunas (10 colunas - 2 para cada letra BINGO)
    for i in range(10):
        tabela_frame.grid_columnconfigure(i, weight=1, minsize=tamanhos.LARGURA_COLUNA//2)
    
    # Cabeçalho B B I I N N G G O O
    for col in range(5):
        header = tk.Frame(tabela_frame,
                         bg=CORES['header_bg'],
                         height=tamanhos.ALTURA_CELULA//3,
                         highlightthickness=1,
                         highlightbackground=CORES['borda'])
        header.grid(row=0, column=col*2, columnspan=2, sticky="nsew")
        
        tk.Label(header,
                text=list(colunas_bingo.keys())[col],
                font=tamanhos.FONTE_CABECALHO,
                fg=CORES['header_fg'],
                bg=CORES['header_bg']).pack(expand=True)
    
    # Números sorteados - 8 linhas (16 números em pares horizontais)
    for linha in range(1, 9):  # Alterado para 8 linhas
        for col in range(5):  # 5 letras BINGO
            bg_color = CORES['cartela'] if linha % 2 == 0 else CORES['cell_bg']
            
            # Célula que vai conter o par de números
            cell = tk.Frame(tabela_frame,
                          bg=bg_color,
                          highlightthickness=1,
                          highlightbackground=CORES['borda'],
                          height=tamanhos.ALTURA_CELULA)
            cell.grid(row=linha, column=col*2, columnspan=2, sticky="nsew")
            
            letra = list(colunas_bingo.keys())[col]
            numeros_coluna = colunas_bingo[letra]
            
            # Frame interno para os 2 números
            num_frame = tk.Frame(cell, bg=bg_color)
            num_frame.pack(expand=True, fill=tk.BOTH)
            
            # Primeiro número (esquerda) - (linha*2-2)
            if (linha*2-2) < len(numeros_coluna):
                num1 = numeros_coluna[linha*2-2]
                tk.Label(num_frame,
                        text=str(num1),
                        font=tamanhos.FONTE_NUMEROS,
                        fg=CORES['texto'],
                        bg=bg_color,
                        width=4).pack(side=tk.LEFT, expand=True)
            else:
                # Célula vazia para manter alinhamento
                tk.Label(num_frame,
                        text="",
                        bg=bg_color,
                        width=4).pack(side=tk.LEFT, expand=True)
            
            # Segundo número (direita) - (linha*2-1)
            if (linha*2-1) < len(numeros_coluna):
                num2 = numeros_coluna[linha*2-1]
                tk.Label(num_frame,
                        text=str(num2),
                        font=tamanhos.FONTE_NUMEROS,
                        fg=CORES['texto'],
                        bg=bg_color,
                        width=4).pack(side=tk.LEFT, expand=True)
            else:
                # Célula vazia para manter alinhamento
                tk.Label(num_frame,
                        text="",
                        bg=bg_color,
                        width=4).pack(side=tk.LEFT, expand=True)

def nova_rodada():
    global bingo_ativado
    for letra in colunas_bingo:
        colunas_bingo[letra].clear()
    bingo_ativado = False
    numero_label.config(text="--", font=tamanhos.FONTE_NUMERO_SORTEADO, fg=CORES['texto'])
    atualizar_cartela()

def finalizar_rodada():
    global bingo_ativado
    
    if not any(colunas_bingo.values()):
        messagebox.showwarning("Aviso", "Nenhum número foi sorteado ainda!")
        return
    
    bingo_ativado = True
    
    cursor.execute("INSERT INTO rodadas (data) VALUES (?)", 
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
    rodada_id = cursor.lastrowid
    
    for letra in colunas_bingo:
        for numero in colunas_bingo[letra]:
            cursor.execute("INSERT INTO numeros (rodada_id, numero, letra) VALUES (?, ?, ?)", 
                         (rodada_id, numero, letra))
    conn.commit()
    
    mostrar_bingo_no_painel()

def mostrar_bingo_no_painel():
    global botoes_bingo_frame
    
    numero_label.config(text="BINGO!", font=tamanhos.FONTE_BINGO, fg=CORES['cabecalho'])
    
    if botoes_bingo_frame is not None:
        botoes_bingo_frame.destroy()
    
    botoes_bingo_frame = tk.Frame(controle_frame, bg=CORES['fundo'])
    botoes_bingo_frame.pack(pady=20)
    
    tk.Button(botoes_bingo_frame, 
             text="Continuar Rodada", 
             font=tamanhos.FONTE_BOTAO, 
             command=continuar_rodada,
             bg=CORES['botao'], 
             fg='white',
             width=20).pack(side=tk.LEFT, padx=10)
    
    tk.Button(botoes_bingo_frame, 
             text="Terminar Rodada", 
             font=tamanhos.FONTE_BOTAO, 
             command=terminar_rodada,
             bg='#8B0000', 
             fg='white',
             width=20).pack(side=tk.LEFT, padx=10)

def continuar_rodada():
    global botoes_bingo_frame
    
    if botoes_bingo_frame is not None:
        botoes_bingo_frame.destroy()
        botoes_bingo_frame = None
    
    if any(colunas_bingo.values()):
        ultimo_numero = max(num for sublist in colunas_bingo.values() for num in sublist)
        numero_label.config(text=str(ultimo_numero), font=tamanhos.FONTE_NUMERO_SORTEADO, fg=CORES['numero_sorteado'])
    else:
        numero_label.config(text="--", font=tamanhos.FONTE_NUMERO_SORTEADO, fg=CORES['texto'])

def terminar_rodada():
    global botoes_bingo_frame
    
    if botoes_bingo_frame is not None:
        botoes_bingo_frame.destroy()
        botoes_bingo_frame = None
    
    nova_rodada()

# Funções de histórico
def mostrar_historico():
    historico_window = tk.Toplevel(root)
    historico_window.title("Histórico de Rodadas")
    historico_window.state('zoomed')
    
    main_frame = tk.Frame(historico_window, bg=CORES['fundo'])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    header_frame = tk.Frame(main_frame, bg=CORES['cabecalho'], height=120)
    header_frame.pack(fill=tk.X)
    
    tk.Label(header_frame, 
            text="HISTÓRICO DE RODADAS", 
            font=tamanhos.FONTE_TITULO, 
            fg='white', 
            bg=CORES['cabecalho']).pack(pady=20)
    
    tree_frame = tk.Frame(main_frame, bg=CORES['fundo'])
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    vsb = ttk.Scrollbar(tree_frame, orient="vertical")
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
    
    tree = ttk.Treeview(tree_frame, 
                       columns=("ID", "Data/Hora", "Números Sorteados"),
                       show='headings',
                       yscrollcommand=vsb.set,
                       xscrollcommand=hsb.set)
    
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    tree.column("ID", width=100, anchor='center')
    tree.column("Data/Hora", width=300, anchor='center')
    tree.column("Números Sorteados", width=1000, anchor='w')
    
    tree.heading("ID", text="ID")
    tree.heading("Data/Hora", text="Data/Hora")
    tree.heading("Números Sorteados", text="Números Sorteados")
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    
    btn_frame = tk.Frame(main_frame, bg=CORES['fundo'])
    btn_frame.pack(fill=tk.X, pady=20)
    
    tk.Button(btn_frame, 
             text="Limpar Histórico", 
             font=tamanhos.FONTE_BOTAO, 
             command=lambda: [limpar_historico(), carregar_dados_historico(tree)],
             bg='#8B0000', 
             fg='white',
             width=20).pack(side=tk.RIGHT, padx=10)
    
    tk.Button(btn_frame, 
             text="Exportar para CSV", 
             font=tamanhos.FONTE_BOTAO, 
             command=lambda: exportar_historico(historico_window),
             bg=CORES['botao'], 
             fg='white',
             width=20).pack(side=tk.RIGHT, padx=10)
    
    tk.Button(btn_frame, 
             text="Fechar", 
             font=tamanhos.FONTE_BOTAO, 
             command=historico_window.destroy,
             bg=CORES['botao'], 
             fg='white',
             width=20).pack(side=tk.RIGHT, padx=10)
    
    carregar_dados_historico(tree)

def carregar_dados_historico(tree):
    try:
        for item in tree.get_children():
            tree.delete(item)
        
        cursor.execute("""
        SELECT r.id, r.data, GROUP_CONCAT(n.letra || '-' || n.numero, ', ')
        FROM rodadas r
        JOIN numeros n ON r.id = n.rodada_id
        GROUP BY r.id
        ORDER BY r.id DESC
        """)
        
        for rodada in cursor.fetchall():
            tree.insert("", tk.END, values=rodada)
            
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar histórico:\n{str(e)}")

def exportar_historico(parent_window=None):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Salvar Histórico Como"
    )
    
    if not file_path:
        return
    
    try:
        cursor.execute("""
        SELECT r.id, r.data, GROUP_CONCAT(n.letra || '-' || n.numero, ', ')
        FROM rodadas r
        JOIN numeros n ON r.id = n.rodada_id
        GROUP BY r.id
        ORDER BY r.id DESC
        """)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Data/Hora', 'Números Sorteados'])
            writer.writerows(cursor.fetchall())
            
        messagebox.showinfo("Sucesso", f"Histórico exportado para:\n{file_path}", parent=parent_window)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao exportar histórico:\n{str(e)}", parent=parent_window)

def limpar_historico():
    if not messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar todo o histórico?\nEsta ação não pode ser desfeita."):
        return
    
    try:
        cursor.execute("DELETE FROM numeros")
        cursor.execute("DELETE FROM rodadas")
        conn.commit()
        messagebox.showinfo("Sucesso", "Histórico limpo com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao limpar histórico:\n{str(e)}")

# Interface principal
main_frame = tk.Frame(root, bg=CORES['fundo'])
main_frame.pack(fill=tk.BOTH, expand=True)

# Cabeçalho
header_frame = tk.Frame(main_frame, bg=CORES['cabecalho'], height=80)
header_frame.pack(fill=tk.X)

titulo_label = tk.Label(header_frame, 
                      text="BINGO - SHOW DE PRÊMIOS", 
                      font=tamanhos.FONTE_TITULO, 
                      fg='white', 
                      bg=CORES['cabecalho'])
titulo_label.pack(expand=True)

# Corpo principal (2 colunas)
body_frame = tk.Frame(main_frame, bg=CORES['fundo'])
body_frame.pack(fill=tk.BOTH, expand=True)

# Coluna esquerda (controles) - 25% da largura
left_panel = tk.Frame(body_frame, bg=CORES['fundo'], width=int(root.winfo_screenwidth()*0.25))
left_panel.pack(side=tk.LEFT, fill=tk.BOTH)
left_panel.pack_propagate(False)

# Painel de controle
controle_frame = tk.Frame(left_panel, bg=CORES['fundo'])
controle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Display do número sorteado
numero_frame = tk.Frame(controle_frame, bg=CORES['fundo'])
numero_frame.pack(fill=tk.X, pady=(0, 10))

tk.Label(numero_frame, 
        text="ÚLTIMO NÚMERO SORTEADO", 
        font=tamanhos.FONTE_CABECALHO, 
        bg=CORES['fundo']).pack()

numero_label = tk.Label(numero_frame, 
                       text="--", 
                       font=tamanhos.FONTE_NUMERO_SORTEADO,
                       fg=CORES['texto'], 
                       bg=CORES['fundo'])
numero_label.pack(pady=5)

# Frame para entrada de número
entrada_frame = tk.Frame(controle_frame, bg=CORES['fundo'])
entrada_frame.pack(fill=tk.X, pady=10)

tk.Label(entrada_frame, 
        text="Adicionar Número:", 
        font=tamanhos.FONTE_TEXTO, 
        bg=CORES['fundo']).pack()

entrada_btn_frame = tk.Frame(entrada_frame, bg=CORES['fundo'])
entrada_btn_frame.pack()

numero_entry = tk.Entry(entrada_btn_frame, 
                       font=tamanhos.FONTE_TEXTO, 
                       width=8)
numero_entry.pack(side=tk.LEFT, padx=5)

adicionar_btn = tk.Button(entrada_btn_frame, 
                         text="Adicionar", 
                         font=tamanhos.FONTE_BOTAO, 
                         command=adicionar_numero,
                         bg=CORES['botao'], 
                         fg='white')
adicionar_btn.pack(side=tk.LEFT, padx=5)

# Botões principais
botoes_frame = tk.Frame(controle_frame, bg=CORES['fundo'])
botoes_frame.pack(fill=tk.X, pady=10)

bingo_btn = tk.Button(botoes_frame, 
                     text="BINGO!", 
                     font=tamanhos.FONTE_BOTAO, 
                     command=finalizar_rodada,
                     bg=CORES['destaque'], 
                     fg='black')
bingo_btn.pack(fill=tk.X, pady=5)

historico_btn = tk.Button(botoes_frame, 
                        text="Ver Histórico", 
                        font=tamanhos.FONTE_BOTAO, 
                        command=mostrar_historico,
                        bg=CORES['botao'], 
                        fg='white')
historico_btn.pack(fill=tk.X, pady=5)

# Coluna direita (cartela) - 75% da largura
right_panel = tk.Frame(body_frame, bg=CORES['fundo'])
right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Frame para a tabela (sem scroll)
tabela_frame = tk.Frame(right_panel, bg=CORES['cartela'])
tabela_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Iniciar o jogo
nova_rodada()
root.mainloop()