import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from modulos.db.requisicoes import db

class BaseToplevel(ctk.CTkToplevel):
    """
    Classe Base para subjanelas. Ela estabelece o padrão geral e conexão com o banco de dados.
    
    Args:
    - master: janela mestre.
    - title (str): título da subjanela.
    - label_text (str): texto do rótulo principal.
    """
    # Classe Pai, para todas as outras subjanelas herdarem o mesmo padrão

    def __init__(self, master, title, label_text, *args, **kwargs):

        # Estabelecendo o banco de dados.
        self.database = db('tarefas.db')
        self.database.connect_db()
        self.database.create_table()

        # Definindo a Classe principal.
        super().__init__(master, *args, **kwargs)

        # Configurando o padrão das subjanelas.
        self.geometry("600x400")
        self.title(title)
        self.label = ctk.CTkLabel(self, text=label_text)
        self.label.pack(padx=20, pady=20)
    
    def limpar_entry(self, entry):
        entry.delete(0, tk.END)  

class AddContactToplevel(BaseToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, "Adicionar Tarefa", "Descrição da Tarefa", *args, **kwargs)
         # Lista de placeholders para os Entry widgets
        placeholders = ["Titulo da Tarefa", "Descrição da Tarefa"]

        # Criando e posicionando cada Entry
        self.entries = []  # Uma lista para guardar referências aos Entry widgets
        for placeholder in placeholders:
            entry = ctk.CTkEntry(self, placeholder_text=placeholder)
            entry.pack(padx=20, pady=20)
            self.entries.append(entry)

        status_tarefa = ctk.CTkComboBox(self, values=["Concluida", "Pendente"])
        status_tarefa.pack(padx=20, pady=20)
        status_tarefa.set("Pendente")
        self.status_default = "Pendente"

        self.entries.append(status_tarefa)     

        # Botão de ação (Adicionar)
        button = ctk.CTkButton(self, text="Adicionar", command=self.add_task)
        button.pack(padx=20, pady=20)

    def add_task(self):
        """
        Adiciona um novo tarefa ao banco de dados usando os valores dos Entry widgets.
        """
        # Pegando cada uma das entrys na lista.
        tarefa = self.entries[0].get()
        descTarefa = self.entries[1].get()
        concluida = self.entries[2].get()
        
        try:
            # Verificando se os 3 campos foram preenchidos.
            if tarefa and descTarefa:
                # Adicionando ao db os 3 valores.
                self.database.add_task((tarefa, descTarefa, concluida))

                messagebox.showwarning("Cadastro Concluido", "Tarefa adicionada com sucesso!")
                App.uptade_tree(app)

                # Limpa as entradas após a adição
                self.limpar_entry(self.entries[0])
                self.limpar_entry(self.entries[1])

                # Finalizando a Janela.
                self.destroy()  
                
            else:
                # Erro por falta de preenchimento de algum dos campos.
                raise ValueError("Preencha todos os campos corretamente!")       
                
        except Exception as e:
            messagebox.showwarning("Erro no cadastro", str(e))
            # Limpa as entradas 
            self.limpar_entry(self.entries[0])
            self.limpar_entry(self.entries[1])
            
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        # Estabelecendo o banco de dados.
        self.database = db('tarefas.db')
        self.database.connect_db()
        self.database.create_table()

        super().__init__(*args, **kwargs)
        self.geometry("900x450")
        self.maxsize(900, 450)
        self.minsize(800, 450)

        App.title(self, "To-Do-App")
        search_frame = ctk.CTkFrame(self, fg_color='transparent') # Frame de pesquisa
        search_frame.grid(row=0, column=2, padx=20, pady=20, sticky='EW')

        self.valor_entry = ctk.CTkEntry(search_frame, placeholder_text="Valor") # Entry de pesquisa
        self.valor_entry.grid(row=0, column= 1, padx=20, pady=20, sticky='EW')

        self.search_button = ctk.CTkButton(search_frame, text="🔍", width=10, command=self.filter_task) # Botão de ação (Pesquisa)
        self.search_button.grid(row=0, column= 2, sticky='EW', padx=5)

        self.filter_select = ctk.CTkComboBox(self, values=["Filtro", "Concluida", "Pendente"])
        self.filter_select.set('Filtro')
        self.filter_select.grid(row=0, column=3, sticky='EW', padx=5)

        self.columns = ["tarefa", "descTarefa", "concluida"]
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings") # Definindo as Colunas do TreeView
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')

        self.tree.grid(row=1, column=0, pady=20, padx=20, columnspan=4, sticky='EW')
        
        self.populate_tasks() # Chamada da função para preencher a treeview

        theme = ctk.CTkOptionMenu(master=self,
                                       values=["Dark", "Light", "Default"],
                                       command= self.theme_selector,
                                       width=30,
                                       height=30) # Menu Seletor de Temas.
        
        theme.grid(row=3, column=0, pady=20, padx=20, sticky='EW')
        theme.set('Tema')

        add_button = ctk.CTkButton(self, text="Nova tarefa", command=self.open_add_tasks)
        add_button.grid(row=0, column=0, pady=20, padx=20)

        remove_button = ctk.CTkButton(self, text="Remover", command=self.remove_task)
        remove_button.grid(row=0, column=1, pady=20, padx=20)
        self.toplevel_window = None

        toggle_task_button = ctk.CTkButton(self, text="Atualizar Status Tarefa", command=self.toggle_task_status)
        toggle_task_button.grid(row=3, column=3, pady=20, padx=20, sticky='EW')

    def open_add_tasks(self):
        self.add_contact_top_level = AddContactToplevel(self) # Instanciando a Tela de Adicionar tarefa.
        
    def populate_tasks(self, search_query=None, filter=None):
        """
        Preenche a Treeview com tarefas pesquisadas no banco de dados.
        Se um termo de pesquisa e/ou um filtro forem fornecidos, filtra os resultados.
        """
        # Limpa o Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Pega todas as tarefas ou apenas as filtradas
        tasks = self.database.search_task(search_query, filter)
        
        # Inserindo as tarefas na Treeview
        for task in tasks:
            self.tree.insert("", tk.END, values=(task[0], task[1], task[2]))


    def filter_task(self):
        search_query = self.valor_entry.get()  # Buscando o resultado do que foi digitado.
        filter_result = self.filter_select.get()

        # Chama populate_tasks com os valores obtidos
        self.populate_tasks(search_query, filter_result if filter_result != 'Filtro' else None)

    def toggle_task_status(self):
        
        if self.tree.selection():
            selected = self.tree.selection()[0]  # Pegando a seleção do usuário.

            item_values = self.tree.item(selected, "values")  # Pegando os valores do item selecionado.

            # Determina o novo status com base no status atual
            new_status = "Concluida" if item_values[-1] == "Pendente" else "Pendente"

            confirm = messagebox.askyesno("Alterar Status", f"Deseja alterar o status da tarefa: {item_values} para {new_status}?")
            try:
                if confirm:
                    self.database.update_task_status(task_details=item_values, new_status=new_status)
                    messagebox.showinfo("Atualizado", f"Status da tarefa {item_values[0]} alterado para {new_status} com sucesso!")
                    self.uptade_tree() # Certifique-se de que o nome deste método está correto
                else:
                    raise ValueError("Confirmação Recusada.")
            except Exception as e:
                return messagebox.showerror("Erro!", str(e))

    def remove_task(self):
        """
        Remove um tarefa baseado em uma coluna e valor.
        Args:
            valor (str): Recebe a Tupla com os valores a serem removidos.
        """
        if self.tree.selection():
            selected = self.tree.selection()[0] # Pegando a seleção do usuario, na posição 0.
       
            item_values = self.tree.item(selected, "values") # Pegando os valores do item selecionado para enviar a função de remover.
            confirm  = messagebox.askyesno("Remover", f"Confirme a remoção da tarefa: \n Titulo: {item_values[0]} \n Descrição: {item_values[1]} \n Status: {item_values[2]}")

            try:
                if confirm:
                    self.database.remove_task(item_values) # Chamada para função de remover.
                    messagebox.showwarning("Removido", f"tarefa {item_values[0]} Removido com Sucesso!")
                    self.uptade_tree()

                else:
                    raise ValueError("Confirmação recusada.")
                
            except Exception as e:
                return messagebox.showerror("Erro!", str(e))     
           
    def uptade_tree(self):
        self.populate_tasks()

    def theme_selector(self, choice):
        """
        param choice: Escolha de tema selecionada pelo usuario.

        returns:
            define pela função set_appearence_mode o tema da interface.
        """
        if choice == 'Dark':
            ctk.set_appearance_mode("dark")
        elif choice == 'Light':
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")

if __name__ == "__main__":
    app = App()
    app.mainloop()