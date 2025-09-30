"""
Aplicação de Agenda com Tkinter e SQLite.

Este programa implementa um sistema simples de agenda de contatos
com interface gráfica em Tkinter e banco de dados SQLite.

Funcionalidades principais:
- Inserir contatos (nome e telefone)
- Listar todos os contatos cadastrados
- Deletar contatos selecionados
- Pesquisar contatos por nome
- Exibir dados de um contato selecionado

Estrutura do programa:
- Classe BancoDeDados: responsável por gerenciar a conexão com o banco
  e executar operações (inserir, deletar, listar e pesquisar).
- Classe AgendaApp: responsável pela interface gráfica em Tkinter.
  Possui entradas de texto, botões, treeview para exibir os contatos
  e mecanismos de pesquisa.

Autor: GABRIEL SILVA SANDES
"""

import os
import sqlite3
from sqlite3 import Error
import tkinter as tk
from tkinter import ttk, messagebox


class BancoDeDados:
    def __init__(self, nome_banco="agenda.db"):
        caminho = os.path.dirname(os.path.abspath(__file__))
        self.caminho = os.path.join(caminho, nome_banco)

    def conectar(self):
        try:
            return sqlite3.connect(self.caminho)
        except Error as e:
            print(f"Erro na conexão: {e}")
            return None

    def inserir(self, nome, telefone):
        query = """
        INSERT INTO TB_CONTATOS 
        (T_NOMECONTATO, T_TELEFONECONTATO, T_EMAILCONTATO, T_INFORMACOES) 
        VALUES (?, ?, ?, ?)
        """
        conexao = self.conectar()
        cursor = conexao.cursor()
        cursor.execute(query, (nome, telefone, "", ""))
        conexao.commit()
        conexao.close()

    def deletar(self, id_contato):
        query = "DELETE FROM TB_CONTATOS WHERE N_IDCONTATO=?"
        conexao = self.conectar()
        cursor = conexao.cursor()
        cursor.execute(query, (id_contato,))
        conexao.commit()
        conexao.close()

    def listar(self):
        query = "SELECT N_IDCONTATO, T_NOMECONTATO, T_TELEFONECONTATO FROM TB_CONTATOS"
        conexao = self.conectar()
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        conexao.close()
        return resultado

    def pesquisar(self, nome):
        query = """
        SELECT N_IDCONTATO, T_NOMECONTATO, T_TELEFONECONTATO 
        FROM TB_CONTATOS 
        WHERE T_NOMECONTATO LIKE ?
        """
        conexao = self.conectar()
        cursor = conexao.cursor()
        cursor.execute(query, (f"%{nome}%",))
        resultado = cursor.fetchall()
        conexao.close()
        return resultado


class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meu programa em Tkinter")

        largura = 600
        altura = 450
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        posx = (largura_tela - largura) // 2
        posy = (altura_tela - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{posx}+{posy}")
        self.root.resizable(False, False)

        self.db = BancoDeDados()

        self._criar_widgets()
        self.mostrar_todos()

    def _criar_widgets(self):
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)

        lb_id = tk.Label(self.root, text="ID")
        lb_nome = tk.Label(self.root, text="NOME")
        lb_telefone = tk.Label(self.root, text="TELEFONE")

        lb_id.grid(column=0, row=0, padx=10, pady=5, sticky="ew")
        lb_nome.grid(column=1, row=0, padx=10, pady=5, sticky="ew")
        lb_telefone.grid(column=2, row=0, padx=10, pady=5, sticky="ew")

        self.en_id = tk.Entry(self.root, bd=1, relief="solid")
        self.en_nome = tk.Entry(self.root, bd=1, relief="solid")
        self.en_telefone = tk.Entry(self.root, bd=1, relief="solid")

        self.en_id.grid(column=0, row=1, padx=10, pady=5, sticky="ew")
        self.en_nome.grid(column=1, row=1, padx=10, pady=5, sticky="ew")
        self.en_telefone.grid(column=2, row=1, padx=10, pady=5, sticky="ew")

        self.tv = ttk.Treeview(
            self.root,
            columns=("id", "nome", "telefone"),
            show="headings",
            height=10
        )
        self.tv.column("id", width=50, anchor="center")
        self.tv.column("nome", width=250, anchor="center")
        self.tv.column("telefone", width=150, anchor="center")

        self.tv.heading("id", text="ID")
        self.tv.heading("nome", text="NOME")
        self.tv.heading("telefone", text="TELEFONE")

        self.tv.grid(column=0, row=3, columnspan=3, pady=10, padx=20, sticky="nsew")

        btn_inserir = tk.Button(self.root, text="Inserir", command=self.inserir, width=15)
        btn_deletar = tk.Button(self.root, text="Deletar", command=self.deletar, width=15)
        btn_obter = tk.Button(self.root, text="Obter", command=self.obter, width=15)

        btn_inserir.grid(column=0, row=4, pady=10)
        btn_deletar.grid(column=1, row=4, pady=10)
        btn_obter.grid(column=2, row=4, pady=10)

        frame_pesquisar = tk.LabelFrame(self.root, text="Pesquisar Contatos")
        frame_pesquisar.grid(column=0, row=5, columnspan=3, sticky="ew", padx=20, pady=10)

        tk.Label(frame_pesquisar, text="Nome").grid(row=0, column=0, padx=5, pady=5)
        self.en_pesquisar = tk.Entry(frame_pesquisar, width=30)
        self.en_pesquisar.grid(row=0, column=1, padx=5, pady=5)

        btn_pesquisar = tk.Button(frame_pesquisar, text="Pesquisar", command=self.pesquisar)
        btn_pesquisar.grid(row=0, column=2, padx=5, pady=5)

        btn_mostrar = tk.Button(frame_pesquisar, text="Mostrar Todos", command=self.mostrar_todos)
        btn_mostrar.grid(row=0, column=3, padx=5, pady=5)

    def limpar_treeview(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

    def mostrar_todos(self):
        self.limpar_treeview()
        contatos = self.db.listar()
        for contato in contatos:
            self.tv.insert("", tk.END, values=contato)

    def inserir(self):
        if self.en_nome.get() == "" or self.en_telefone.get() == "":
            messagebox.showinfo("Erro", "Por favor digite todos os dados!")
            return

        self.db.inserir(self.en_nome.get(), self.en_telefone.get())
        self.mostrar_todos()

        self.en_id.delete(0, tk.END)
        self.en_nome.delete(0, tk.END)
        self.en_telefone.delete(0, tk.END)
        self.en_id.focus()

    def deletar(self):
        try:
            item = self.tv.selection()[0]
            valores = self.tv.item(item, "values")
            id_contato = valores[0]

            self.db.deletar(id_contato)
            self.mostrar_todos()
        except IndexError:
            messagebox.showinfo("Erro", "Por favor escolha o elemento a ser deletado!")

    def obter(self):
        try:
            item = self.tv.selection()[0]
            valores = self.tv.item(item, "values")
            print(f"ID......: {valores[0]}")
            print(f"Nome....: {valores[1]}")
            print(f"Telefone: {valores[2]}")
        except IndexError:
            messagebox.showinfo("Erro", "Por favor escolha o elemento a ser mostrado!")

    def pesquisar(self):
        nome = self.en_pesquisar.get().strip()
        if not nome:
            messagebox.showinfo("Erro", "Digite um nome para pesquisar!")
            return

        self.limpar_treeview()
        contatos = self.db.pesquisar(nome)
        for contato in contatos:
            self.tv.insert("", tk.END, values=contato)


if __name__ == "__main__":
    app = tk.Tk()
    AgendaApp(app)
    app.mainloop()
