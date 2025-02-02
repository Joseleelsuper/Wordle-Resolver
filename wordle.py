import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

FILE = "palabras.txt"
WORD_LENGTH = 5
FEEDBACK = ["B", "C", "M"]


def load_words(file: str = FILE, word_length: int = WORD_LENGTH) -> list:
    """Carga un archivo de palabras y devuelve las de longitud n.

    Args:
        archivo (str, optional): Fichero a ser cargado. Defaults to FILE.
        n (int, optional): Longitud de las palabras a filtrar. Defaults to WORD_LENGTH.

    Returns:
        list: Lista de palabras filtradas.
    """
    with open(file, "r", encoding="utf-8") as f:
        return [p.strip().lower() for p in f if len(p.strip()) == word_length]


def simulate_feedback(candidate: str, attempt: str) -> str:
    """Simula el feedback comparando la palabra candidata con el intento,
    siguiendo la mecánica de Wordle para letras repetidas.

    'B' = Bien (letra en la posición correcta).\n
    'C' = Cambio (letra correcta en posición incorrecta).\n
    'M' = Mal (letra incorrecta).

    Args:
        lista (list): Lista de palabras a filtrar.
        attempt (int): Número de intento.
        feedback (str): Feedback del intento.

    Returns:
        list: Lista de palabras que cumplen con el feedback.
    """
    feedback_result = [""] * len(candidate)
    candidate_list = list(candidate)

    # Primer pase: marcar 'B' en coincidencias exactas.
    for i in range(len(attempt)):
        if attempt[i] == candidate_list[i]:
            feedback_result[i] = FEEDBACK[0]
            candidate_list[i] = None  # Marcar letra usada.

    # Segundo pase: marcar 'C' o 'M' en función de las letras restantes.
    for i in range(len(attempt)):
        if feedback_result[i] == "":
            if attempt[i] in candidate_list:
                feedback_result[i] = FEEDBACK[1]
                candidate_list[candidate_list.index(attempt[i])] = None
            else:
                feedback_result[i] = FEEDBACK[2]
    return "".join(feedback_result)


def filter_words(words_list: list, attempt: str, feedback: str) -> list:
    """
    Filtra la lista de palabras conservando solo aquellas que,
    al simular el feedback con el attempt, coinciden exactamente con
    el feedback proporcionado.

    Args:
        lista (list): Lista de palabras a filtrar.
        attempt (int): Número de attempt.
        feedback (str): Feedback del attempt.

    Returns:
        list: Lista de palabras filtradas.
    """
    new_words = []
    for word in words_list:
        if simulate_feedback(word, attempt) == feedback:
            new_words.append(word)
    return new_words


def best_try(words_list: list) -> str:
    """
    Selecciona la palabra con mayor puntaje basado en la frecuencia de letras
    únicas en la lista de palabras candidatas.

    Args:
        lista (list): Lista de palabras a evaluar.

    Returns:
        str: Palabra con mejor puntaje.
    """
    freq = {}
    for word in words_list:
        for letter in set(word):
            freq[letter] = freq.get(letter, 0) + 1
    best = None
    best_score = -1
    for word in words_list:
        score = sum(freq[letter] for letter in set(word))
        if score > best_score:
            best_score = score
            best = word
    return best


def main_cli():
    """Función principal del resolverdor de Wordle en modo consola."""
    word_length_input = input("Ingresa la cantidad de letras (default 5): ").strip()
    word_length = int(word_length_input) if word_length_input.isdigit() else WORD_LENGTH

    words = load_words(FILE, word_length)
    if not words:
        print("No se encontraron palabras de longitud", word_length)
        sys.exit()

    attempt = input("Ingresa la primera palabra: ").lower()
    if attempt not in words:
        print(
            "La palabra no está en la lista. Prueba a añadirla manualmente al diccionario y vuelve a ejecutar el programa."
        )
        sys.exit()

    while True:
        print("\nIntento:", attempt)
        feedback = (
            input(
                "Ingresa feedback (usa 'B' para bien, 'C' para cambiar, 'M' para mal, o 'T'/'esc' para terminar): "
            )
            .upper()
            .strip()
        )
        if feedback in ["T", "ESC"]:
            print("Terminado.")
            break
        if len(feedback) != word_length:
            print("El feedback debe tener", word_length, "letras.")
            continue

        words = filter_words(words, attempt, feedback)
        if not words:
            print("No hay palabras posibles. Revisa el feedback.")
            break
        attempt = best_try(words)
        print("Siguiente sugerencia:", attempt)


class WordleSolverGUI:
    """Clase principal del resolverdor de Wordle en modo gráfico."""

    def __init__(self):
        """Inicializa la interfaz gráfica y los elementos necesarios."""
        self.root = tk.Tk()
        self.root.title("Wordle Solver - Modo Gráfico")
        self.word_length = WORD_LENGTH
        self.words_list = []
        self.current_attempt = ""
        self.attempts_data = []  # Lista de tuplas (attempt, feedback)

        # Solicitar configuración inicial
        length = simpledialog.askinteger(
            "Configuración",
            "Ingresa la cantidad de letras (default 5):",
            initialvalue=WORD_LENGTH,
        )
        self.word_length = length if length else WORD_LENGTH
        self.words_list = load_words(FILE, self.word_length)
        if not self.words_list:
            messagebox.showerror(
                "Error", f"No se encontraron palabras de longitud {self.word_length}"
            )
            self.root.destroy()
            return

        # Solicitar la primera palabra
        while True:
            attempt = simpledialog.askstring(
                "Configuración", "Ingresa la primera palabra:"
            )
            if not attempt:
                self.root.destroy()
                return
            attempt = attempt.lower().strip()
            if attempt in self.words_list:
                self.current_attempt = attempt
                break
            else:
                messagebox.showerror(
                    "Error",
                    "La palabra no está en la lista. Prueba a añadirla manualmente al diccionario y vuelve a ejecutar el programa.",
                )

        # Crear elementos gráficos
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(padx=10, pady=10)

        self.suggestion_label = tk.Label(
            self.root,
            text=f"Siguiente sugerencia: {self.current_attempt}",
            font=("Arial", 14),
        )
        self.suggestion_label.pack(pady=5)

        feedback_frame = tk.Frame(self.root)
        feedback_frame.pack(pady=5)

        tk.Label(feedback_frame, text="Ingresa feedback: ").pack(side=tk.LEFT)
        self.feedback_entry = tk.Entry(feedback_frame, width=10)
        self.feedback_entry.pack(side=tk.LEFT)

        submit_button = tk.Button(
            feedback_frame, text="Submit", command=self.process_feedback
        )
        submit_button.pack(side=tk.LEFT, padx=5)

        exit_button = tk.Button(self.root, text="Exit", command=self.root.destroy)
        exit_button.pack(pady=5)

    def process_feedback(self):
        """Procesa el feedback ingresado por el usuario y actualiza la tabla de intentos."""
        feedback = self.feedback_entry.get().upper().strip()
        if feedback in ["T", "ESC"]:
            self.root.destroy()
            return
        if len(feedback) != self.word_length:
            messagebox.showerror(
                "Error", f"El feedback debe tener {self.word_length} letras."
            )
            return

        # Agregar el intento y feedback a la tabla
        self.attempts_data.append((self.current_attempt, feedback))
        self.add_attempt_row(self.current_attempt, feedback)

        # Filtrar la lista de palabras y calcular el siguiente intento
        self.words_list = filter_words(self.words_list, self.current_attempt, feedback)
        if not self.words_list:
            messagebox.showerror(
                "Error", "No hay palabras posibles. Revisa el feedback."
            )
            return
        self.current_attempt = best_try(self.words_list)
        self.suggestion_label.config(
            text=f"Siguiente sugerencia: {self.current_attempt}"
        )
        self.feedback_entry.delete(0, tk.END)

    def add_attempt_row(self, attempt: str, feedback: str):
        """Agrega una fila a la tabla de intentos con el intento y feedback proporcionados.

        Args:
            attempt (str): Intento de palabra.
            feedback (str): Feedback del intento.
        """
        row = len(self.attempts_data) - 1  # índice de la fila
        for col, (letter, fb) in enumerate(zip(attempt, feedback)):
            if fb == "B":
                bg_color = "green"
            elif fb == "C":
                bg_color = "yellow"
            elif fb == "M":
                bg_color = "red"
            else:
                bg_color = "gray"
            lbl = tk.Label(
                self.table_frame,
                text=letter.upper(),
                width=4,
                height=2,
                bg=bg_color,
                font=("Arial", 16),
                relief="ridge",
                borderwidth=2,
            )
            lbl.grid(row=row, column=col, padx=2, pady=2)


def run_gui():
    """Función principal para ejecutar el modo gráfico del resolverdor de Wordle."""
    app = WordleSolverGUI()
    app.root.mainloop()


if __name__ == "__main__":
    mode = input("¿Desea usar modo gráfico? (s/n): ").strip().lower()
    if mode == "s":
        run_gui()
    else:
        main_cli()
