import os
import re
import json
from datetime import datetime
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PapiwebEditorConsole:
    def __init__(self):
        self.current_file = None
        self.content = ""
        self.spelling_errors = {
            "aver": "a ver",
            "haber": "a ver",
            "ay": "ahí/hay/¡ay!",
            "ahi": "ahí",
            "ahy": "ahí",
            "haver": "a ver",
            "echo": "hecho",
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
        self.writing_style = "secundaria"

    def menu(self):
        self.show_banner()
        while True:
            print("\n--- Papiweb Editor Console ---")
            print("1. Nuevo documento")
            print("2. Abrir archivo de texto")
            print("3. Importar desde PDF")
            print("4. Guardar documento")
            print("5. Exportar a PDF")
            print("6. Ver estadísticas")
            print("7. Verificar ortografía")
            print("8. Análisis de estilo")
            print("9. Cambiar estilo de redacción (actual: {} )".format(self.writing_styles[self.writing_style]["name"]))
            print("0. Salir")
            choice = input("Seleccione una opción: ")
            if choice == "1":
                self.new_document()
            elif choice == "2":
                self.open_text_file()
            elif choice == "3":
                self.import_from_pdf()
            elif choice == "4":
                self.save_text_file()
            elif choice == "5":
                self.export_to_pdf()
            elif choice == "6":
                self.show_stats()
            elif choice == "7":
                self.check_spelling()
            elif choice == "8":
                self.analyze_style()
            elif choice == "9":
                self.change_writing_style()
            elif choice == "0":
                print("¡Hasta luego!")
                break
            else:
                print("Opción inválida.")

    def show_banner(self):
        print("""
========================================
   PAPIWEB Editor Console v2
   Desarrollos Informáticos
========================================
Copyright © 2025 Papiweb
""")

    def new_document(self):
        self.content = ""
        self.current_file = None
        print("Documento nuevo creado.")
        self.edit_content()

    def open_text_file(self):
        path = input("Ingrese la ruta del archivo de texto: ")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.content = f.read()
            self.current_file = path
            print(f"Archivo '{path}' abierto.")
        except Exception as e:
            print(f"Error al abrir archivo: {e}")

    def import_from_pdf(self):
        path = input("Ingrese la ruta del archivo PDF: ")
        try:
            with pdfplumber.open(path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            self.content = text
            self.current_file = None
            print(f"PDF '{path}' importado.")
        except Exception as e:
            print(f"Error al importar PDF: {e}")

    def save_text_file(self):
        path = input("Ingrese la ruta para guardar el archivo de texto: ")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.content)
            self.current_file = path
            print(f"Archivo guardado en '{path}'.")
        except Exception as e:
            print(f"Error al guardar archivo: {e}")

    def export_to_pdf(self):
        path = input("Ingrese la ruta para guardar el PDF: ")
        try:
            c = canvas.Canvas(path, pagesize=letter)
            width, height = letter
            margin = 40
            y = height - margin
            for line in self.content.split('\n'):
                c.drawString(margin, y, line)
                y -= 15
                if y < margin:
                    c.showPage()
                    y = height - margin
            c.save()
            print(f"PDF guardado en '{path}'.")
        except Exception as e:
            print(f"Error al exportar PDF: {e}")

    def show_stats(self):
        words = len(self.content.split())
        chars = len(self.content)
        paragraphs = len([p for p in self.content.split('\n') if p.strip()])
        errors = self.count_spelling_errors(self.content)
        print(f"Palabras: {words}")
        print(f"Caracteres: {chars}")
        print(f"Párrafos: {paragraphs}")
        print(f"Errores ortográficos: {errors}")

    def count_spelling_errors(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        error_count = 0
        for word in words:
            if word in self.spelling_errors:
                error_count += 1
        return error_count

    def check_spelling(self):
        words = re.findall(r'\b\w+\b', self.content)
        suggestions = []
        for word in words:
            lw = word.lower()
            if lw in self.spelling_errors:
                suggestions.append(f"'{word}' → {self.spelling_errors[lw]}")
        if suggestions:
            print("Errores encontrados:")
            for s in suggestions:
                print("-", s)
        else:
            print("No se encontraron errores ortográficos.")

    def change_writing_style(self):
        print("Estilos disponibles:")
        for key, style in self.writing_styles.items():
            print(f"{key}: {style['name']}")
        choice = input("Ingrese el estilo deseado: ")
        if choice in self.writing_styles:
            self.writing_style = choice
            print(f"Estilo cambiado a {self.writing_styles[choice]['name']}.")
        else:
            print("Estilo inválido.")

    def analyze_style(self):
        current_style = self.writing_styles[self.writing_style]
        suggestions = [f"Análisis para: {current_style['name']}"]
        content = self.content
        if self.writing_style == "secundaria":
            formal_words = ["utilizar", "efectuar", "realizar", "obstante", "por consiguiente"]
            for word in formal_words:
                if word in content.lower():
                    suggestions.append(f"• Considera cambiar '{word}' por algo más simple")
        elif self.writing_style == "tecnico":
            informal_words = ["cosa", "hacer", "arreglar"]
            for word in informal_words:
                if word in content.lower():
                    suggestions.append(f"• '{word}' podría ser más específico técnicamente")
        elif self.writing_style == "universitario":
            informal_phrases = ["muy bueno", "malo", "está bien"]
            for phrase in informal_phrases:
                if phrase in content.lower():
                    suggestions.append(f"• '{phrase}' podría expresarse de forma más académica")
        connectors = current_style["suggestions"]["conectores"]
        suggestions.append("Conectores sugeridos para este estilo:")
        for connector in connectors[:5]:
            suggestions.append(f"• {connector}")
        sentences = content.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if self.writing_style == "secundaria" and avg_length > 20:
            suggestions.append("Las oraciones son muy largas. Intenta hacerlas más cortas y simples.")
        elif self.writing_style == "universitario" and avg_length < 10:
            suggestions.append("Las oraciones son muy cortas. Intenta desarrollar más las ideas.")
        print("\n".join(suggestions))

    def edit_content(self):
        print("Ingrese el texto (finalice con una línea vacía):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        self.content = "\n".join(lines)

if __name__ == "__main__":
    editor = PapiwebEditorConsole()
    editor.menu()
