import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from tkinter.scrolledtext import ScrolledText
import re
from datetime import datetime
import json
import os

class PapiwebEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Papiweb Editor Pro - Desarrollos Informáticos")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        # Variables
        self.current_file = None
        self.is_modified = False
        self.writing_style = "secundaria"  # por defecto
        
        # Diccionarios de palabras mal escritas comunes
        self.spelling_errors = {
            "aver": "a ver",
            "haber": "a ver",  # contexto dependiente
            "ay": "ahí/hay/¡ay!",
            "ahi": "ahí",
            "ahy": "ahí",
            "haver": "a ver",
            "echo": "hecho",  # contexto dependiente
            "asta": "hasta",
            "ace": "hace",
            "ase": "hace",
            "asia": "hacia",
            "porke": "porque",
            "xq": "porque",
            "q": "que",
            "k": "que",
            "bn": "bien",
            "tbn": "también",
            "tmb": "también",
            "x": "por",
            "xfa": "por favor",
            "plis": "por favor",
            "salu2": "saludos",
            "grax": "gracias",
            "gracias": "gracias",
            "deveria": "debería",
            "tendria": "tendría",
            "podria": "podría",
            "sabria": "sabría",
            "estaria": "estaría"
        }
        
        # Estilos de redacción
        self.writing_styles = {
            "secundaria": {
                "name": "Estudiante Secundario BA",
                "suggestions": {
                    "palabras_formales": {
                        "utilizar": "usar",
                        "efectuar": "hacer",
                        "realizar": "hacer",
                        "obstante": "pero",
                        "por consiguiente": "entonces",
                        "por ende": "entonces"
                    },
                    "conectores": ["entonces", "después", "también", "pero", "y", "o", "porque"],
                    "tone": "informal_juvenil"
                }
            },
            "tecnico": {
                "name": "Desarrollador Técnico",
                "suggestions": {
                    "palabras_tecnicas": {
                        "programa": "aplicación/software",
                        "hacer": "implementar/desarrollar",
                        "arreglar": "debuggear/resolver",
                        "cosa": "componente/módulo",
                        "problema": "bug/issue"
                    },
                    "conectores": ["por lo tanto", "además", "sin embargo", "en consecuencia", "dado que"],
                    "tone": "tecnico_preciso"
                }
            },
            "universitario": {
                "name": "Nivel Universitario",
                "suggestions": {
                    "palabras_academicas": {
                        "muy bueno": "excelente",
                        "malo": "deficiente",
                        "pensar": "considerar/analizar",
                        "decir": "expresar/manifestar",
                        "ver": "observar/analizar"
                    },
                    "conectores": ["no obstante", "por consiguiente", "asimismo", "en virtud de", "en este sentido"],
                    "tone": "academico_formal"
                }
            }
        }
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        # Barra de menú
        self.create_menu()
        
        # Toolbar principal
        self.create_toolbar()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Panel izquierdo - Herramientas
        left_panel = tk.Frame(main_frame, bg="#34495e", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Logo y título
        title_frame = tk.Frame(left_panel, bg="#34495e")
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(title_frame, text="PAPIWEB", font=("Arial", 16, "bold"), 
                fg="#e74c3c", bg="#34495e").pack()
        tk.Label(title_frame, text="Desarrollos Informáticos", font=("Arial", 8), 
                fg="#bdc3c7", bg="#34495e").pack()
        
        # Selección de estilo de redacción
        style_frame = tk.LabelFrame(left_panel, text="Estilo de Redacción", 
                                   fg="#ecf0f1", bg="#34495e", font=("Arial", 10, "bold"))
        style_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.style_var = tk.StringVar(value="secundaria")
        for key, style in self.writing_styles.items():
            rb = tk.Radiobutton(style_frame, text=style["name"], variable=self.style_var,
                               value=key, fg="#ecf0f1", bg="#34495e", selectcolor="#2c3e50",
                               font=("Arial", 9), command=self.change_writing_style)
            rb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Panel de estadísticas
        stats_frame = tk.LabelFrame(left_panel, text="Estadísticas del Texto", 
                                   fg="#ecf0f1", bg="#34495e", font=("Arial", 10, "bold"))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_labels = {}
        stats = ["Palabras:", "Caracteres:", "Párrafos:", "Errores:"]
        for stat in stats:
            frame = tk.Frame(stats_frame, bg="#34495e")
            frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=stat, fg="#bdc3c7", bg="#34495e", 
                    font=("Arial", 9)).pack(side=tk.LEFT)
            label = tk.Label(frame, text="0", fg="#e74c3c", bg="#34495e", 
                           font=("Arial", 9, "bold"))
            label.pack(side=tk.RIGHT)
            self.stats_labels[stat] = label
        
        # Panel de sugerencias
        self.suggestions_frame = tk.LabelFrame(left_panel, text="Sugerencias de Mejora", 
                                              fg="#ecf0f1", bg="#34495e", font=("Arial", 10, "bold"))
        self.suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.suggestions_text = tk.Text(self.suggestions_frame, height=8, wrap=tk.WORD,
                                       font=("Arial", 9), bg="#2c3e50", fg="#ecf0f1",
                                       insertbackground="#ecf0f1")
        self.suggestions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel principal - Editor
        editor_frame = tk.Frame(main_frame, bg="#2c3e50")
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Barra de formato
        format_frame = tk.Frame(editor_frame, bg="#34495e", height=40)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        format_frame.pack_propagate(False)
        
        # Botones de formato
        self.create_format_buttons(format_frame)
        
        # Editor de texto principal
        self.text_editor = ScrolledText(editor_frame, wrap=tk.WORD, font=("Arial", 12),
                                       bg="#ecf0f1", fg="#2c3e50", insertbackground="#2c3e50",
                                       selectbackground="#3498db", selectforeground="#ecf0f1")
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para resaltado
        self.text_editor.tag_configure("error", background="#e74c3c", foreground="white")
        self.text_editor.tag_configure("suggestion", background="#f39c12", foreground="white")
        
        # Barra de estado
        self.create_status_bar()
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#34495e", fg="#ecf0f1")
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0, bg="#34495e", fg="#ecf0f1")
        menubar.add_cascade(label="Archivo", menu=file_menu)
    file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
    file_menu.add_command(label="Guardar como", command=self.save_as_file)
    file_menu.add_separator()
    file_menu.add_command(label="Importar desde PDF", command=self.import_from_pdf)
    file_menu.add_command(label="Exportar a PDF", command=self.export_to_pdf)
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=self.root.quit)
    def import_from_pdf(self):
        import pdfplumber
        file_path = filedialog.askopenfilename(
            title="Importar desde PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if file_path:
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", text)
                self.current_file = None
                self.is_modified = True
                self.update_title()
                self.status_label.config(text=f"PDF importado: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo importar el PDF:\n{str(e)}")

    def export_to_pdf(self):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        file_path = filedialog.asksaveasfilename(
            title="Exportar a PDF",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if file_path:
            try:
                content = self.text_editor.get("1.0", tk.END).strip()
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                margin = 40
                y = height - margin
                for line in content.split('\n'):
                    c.drawString(margin, y, line)
                    y -= 15
                    if y < margin:
                        c.showPage()
                        y = height - margin
                c.save()
                self.status_label.config(text=f"PDF exportado: {os.path.basename(file_path)}")
                messagebox.showinfo("Exportar a PDF", "El archivo PDF se ha guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{str(e)}")
        
        # Menú Editar
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#34495e", fg="#ecf0f1")
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Deshacer", command=lambda: self.text_editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rehacer", command=lambda: self.text_editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cortar", command=lambda: self.text_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", command=lambda: self.text_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Pegar", command=lambda: self.text_editor.event_generate("<<Paste>>"))
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#34495e", fg="#ecf0f1")
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Verificar Ortografía", command=self.check_spelling)
        tools_menu.add_command(label="Análisis de Estilo", command=self.analyze_style)
        tools_menu.add_command(label="Contar Palabras", command=self.update_stats)
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#34495e", height=35)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        toolbar.pack_propagate(False)
        
        # Botones principales
        buttons = [
            ("Nuevo", "📄", self.new_file),
            ("Abrir", "📁", self.open_file),
            ("Guardar", "💾", self.save_file),
            ("", "", None),  # Separador
            ("Ortografía", "📝", self.check_spelling),
            ("Estilo", "🎨", self.analyze_style),
        ]
        
        for text, emoji, command in buttons:
            if text == "":
                tk.Frame(toolbar, width=2, bg="#2c3e50").pack(side=tk.LEFT, fill=tk.Y, padx=5)
            else:
                btn = tk.Button(toolbar, text=f"{emoji} {text}", command=command,
                               bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                               relief=tk.FLAT, padx=10)
                btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def create_format_buttons(self, parent):
        # Selector de fuente
        tk.Label(parent, text="Fuente:", bg="#34495e", fg="#ecf0f1", 
                font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.font_var = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(parent, textvariable=self.font_var, width=10,
                                 values=["Arial", "Times New Roman", "Courier New", "Verdana"])
        font_combo.pack(side=tk.LEFT, padx=5)
        font_combo.bind("<<ComboboxSelected>>", self.change_font)
        
        # Tamaño de fuente
        tk.Label(parent, text="Tamaño:", bg="#34495e", fg="#ecf0f1", 
                font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.size_var = tk.StringVar(value="12")
        size_combo = ttk.Combobox(parent, textvariable=self.size_var, width=5,
                                 values=["8", "10", "12", "14", "16", "18", "20", "24"])
        size_combo.pack(side=tk.LEFT, padx=5)
        size_combo.bind("<<ComboboxSelected>>", self.change_font)
        
        # Botones de formato
        tk.Button(parent, text="B", command=self.toggle_bold, bg="#e74c3c", fg="white",
                 font=("Arial", 10, "bold"), width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(parent, text="I", command=self.toggle_italic, bg="#e67e22", fg="white",
                 font=("Arial", 10, "italic"), width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(parent, text="U", command=self.toggle_underline, bg="#f39c12", fg="white",
                 font=("Arial", 10, "underline"), width=3).pack(side=tk.LEFT, padx=2)
        
    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg="#34495e", height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Listo", 
                                    bg="#34495e", fg="#ecf0f1", font=("Arial", 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Información de posición del cursor
        self.cursor_label = tk.Label(self.status_bar, text="Línea: 1, Columna: 1", 
                                    bg="#34495e", fg="#ecf0f1", font=("Arial", 9))
        self.cursor_label.pack(side=tk.RIGHT, padx=10)
        
    def setup_bindings(self):
        # Atajos de teclado
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<F7>", lambda e: self.check_spelling())
        
        # Eventos del editor
        self.text_editor.bind("<KeyRelease>", self.on_text_change)
        self.text_editor.bind("<ButtonRelease-1>", self.update_cursor_position)
        self.text_editor.bind("<KeyRelease>", self.update_cursor_position, add="+")
        
    def on_text_change(self, event=None):
        self.is_modified = True
        self.update_title()
        self.update_stats()
        # Auto-corrección en tiempo real
        self.root.after(500, self.auto_check_spelling)
        
    def update_title(self):
        title = "Papiweb Editor Pro"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_modified:
            title += " *"
        self.root.title(title)
        
    def update_cursor_position(self, event=None):
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.cursor_label.config(text=f"Línea: {line}, Columna: {int(col)+1}")
        
    def update_stats(self):
        content = self.text_editor.get("1.0", tk.END)
        
        # Contar palabras
        words = len(content.split())
        
        # Contar caracteres
        chars = len(content) - 1  # -1 para excluir el último \n
        
        # Contar párrafos
        paragraphs = len([p for p in content.split('\n') if p.strip()])
        
        # Contar errores ortográficos
        errors = self.count_spelling_errors(content)
        
        self.stats_labels["Palabras:"].config(text=str(words))
        self.stats_labels["Caracteres:"].config(text=str(chars))
        self.stats_labels["Párrafos:"].config(text=str(paragraphs))
        self.stats_labels["Errores:"].config(text=str(errors))
        
    def count_spelling_errors(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        error_count = 0
        for word in words:
            if word in self.spelling_errors:
                error_count += 1
        return error_count
        
    def new_file(self):
        if self.is_modified:
            if not messagebox.askyesno("Papiweb Editor", "¿Desea guardar los cambios?"):
                return
            self.save_file()
        
        self.text_editor.delete("1.0", tk.END)
        self.current_file = None
        self.is_modified = False
        self.update_title()
        self.status_label.config(text="Nuevo documento creado")
        
    def open_file(self):
        if self.is_modified:
            if messagebox.askyesno("Papiweb Editor", "¿Desea guardar los cambios?"):
                self.save_file()
        
        file_path = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert("1.0", content)
                
                self.current_file = file_path
                self.is_modified = False
                self.update_title()
                self.status_label.config(text=f"Archivo abierto: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
                
    def save_file(self):
        if not self.current_file:
            return self.save_as_file()
        
        try:
            content = self.text_editor.get("1.0", tk.END + "-1c")
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.is_modified = False
            self.update_title()
            self.status_label.config(text=f"Archivo guardado: {os.path.basename(self.current_file)}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
            return False
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            return self.save_file()
        return False
        
    def change_font(self, event=None):
        font_family = self.font_var.get()
        font_size = int(self.size_var.get())
        new_font = font.Font(family=font_family, size=font_size)
        self.text_editor.config(font=new_font)
        
    def toggle_bold(self):
        current_font = font.Font(font=self.text_editor['font'])
        if current_font['weight'] == 'normal':
            current_font.config(weight='bold')
        else:
            current_font.config(weight='normal')
        self.text_editor.config(font=current_font)
        
    def toggle_italic(self):
        current_font = font.Font(font=self.text_editor['font'])
        if current_font['slant'] == 'roman':
            current_font.config(slant='italic')
        else:
            current_font.config(slant='roman')
        self.text_editor.config(font=current_font)
        
    def toggle_underline(self):
        current_font = font.Font(font=self.text_editor['font'])
        if current_font['underline'] == 0:
            current_font.config(underline=1)
        else:
            current_font.config(underline=0)
        self.text_editor.config(font=current_font)
        
    def check_spelling(self):
        self.text_editor.tag_remove("error", "1.0", tk.END)
        content = self.text_editor.get("1.0", tk.END)
        
        suggestions = []
        words = re.finditer(r'\b\w+\b', content)
        
        for match in words:
            word = match.group().lower()
            if word in self.spelling_errors:
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_editor.tag_add("error", start_pos, end_pos)
                suggestions.append(f"'{word}' → {self.spelling_errors[word]}")
        
        if suggestions:
            suggestion_text = "Errores encontrados:\n\n" + "\n".join(suggestions[:10])
            if len(suggestions) > 10:
                suggestion_text += f"\n\n...y {len(suggestions)-10} errores más"
        else:
            suggestion_text = "✓ No se encontraron errores ortográficos"
        
        self.suggestions_text.delete("1.0", tk.END)
        self.suggestions_text.insert("1.0", suggestion_text)
        self.status_label.config(text=f"Revisión completada. {len(suggestions)} errores encontrados")
        
    def auto_check_spelling(self):
        # Versión ligera para tiempo real
        self.text_editor.tag_remove("error", "1.0", tk.END)
        content = self.text_editor.get("1.0", tk.END)
        words = re.finditer(r'\b\w+\b', content)
        
        for match in words:
            word = match.group().lower()
            if word in self.spelling_errors:
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_editor.tag_add("error", start_pos, end_pos)
                
    def change_writing_style(self):
        self.writing_style = self.style_var.get()
        self.analyze_style()
        
    def analyze_style(self):
        content = self.text_editor.get("1.0", tk.END)
        current_style = self.writing_styles[self.writing_style]
        
        suggestions = [f"Análisis para: {current_style['name']}\n"]
        
        # Analizar según el estilo seleccionado
        if self.writing_style == "secundaria":
            # Buscar palabras muy formales
            formal_words = ["utilizar", "efectuar", "realizar", "obstante", "por consiguiente"]
            for word in formal_words:
                if word in content.lower():
                    suggestions.append(f"• Considera cambiar '{word}' por algo más simple")
                    
        elif self.writing_style == "tecnico":
            # Buscar términos poco técnicos
            informal_words = ["cosa", "hacer", "arreglar"]
            for word in informal_words:
                if word in content.lower():
                    suggestions.append(f"• '{word}' podría ser más específico técnicamente")
                    
        elif self.writing_style == "universitario":
            # Buscar expresiones informales
            informal_phrases = ["muy bueno", "malo", "está bien"]
            for phrase in informal_phrases:
                if phrase in content.lower():
                    suggestions.append(f"• '{phrase}' podría expresarse de forma más académica")
        
        # Análisis de conectores
        connectors = current_style["suggestions"]["conectores"]
        suggestions.append(f"\nConectores sugeridos para este estilo:")
        for connector in connectors[:5]:
            suggestions.append(f"• {connector}")
            
        # Análisis general
        sentences = content.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if self.writing_style == "secundaria" and avg_length > 20:
            suggestions.append("\n• Las oraciones son muy largas. Intenta hacerlas más cortas y simples.")
        elif self.writing_style == "universitario" and avg_length < 10:
            suggestions.append("\n• Las oraciones son muy cortas. Intenta desarrollar más las ideas.")
            
        suggestion_text = "\n".join(suggestions)
        self.suggestions_text.delete("1.0", tk.END)
        self.suggestions_text.insert("1.0", suggestion_text)
        
        self.status_label.config(text=f"Análisis de estilo completado - {current_style['name']}")

def main():
    root = tk.Tk()
    
    # Configurar el ícono y tema
    root.configure(bg="#2c3e50")
    
    # Crear la aplicación
    app = PapiwebEditor(root)
    
    # Mensaje de bienvenida
    welcome_text = """¡Bienvenido a Papiweb Editor Pro!

Este editor de texto profesional incluye:
• Corrector ortográfico en tiempo real
• 3 estilos de redacción personalizables
• Estadísticas detalladas del texto
• Herramientas de formato avanzadas

Selecciona tu estilo de redacción en el panel izquierdo y comienza a escribir.

Desarrollado por Papiweb - Desarrollos Informáticos
"""
    
    app.text_editor.insert("1.0", welcome_text)
    app.text_editor.mark_set("insert", "1.0")
    app.is_modified = False
    
    # Ejecutar la aplicación
    root.mainloop()

if __name__ == "__main__":
    main()