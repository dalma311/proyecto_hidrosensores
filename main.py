import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB = "hidro_sensores.db"

# ---------------- BASE DE DATOS ----------------
conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS mediciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor TEXT NOT NULL,
    nivel REAL NOT NULL,
    estado TEXT NOT NULL,
    fecha TEXT NOT NULL
)
""")
conn.commit()


# ---------------- FUNCIONES ----------------
def obtener_estado(nivel):
    if nivel < 30:
        return "BAJO"
    elif nivel <= 70:
        return "NORMAL"
    else:
        return "ALTO"


def limpiar():
    sensor.set("")
    nivel.set("")
    estado.set("")
    area.delete("1.0", tk.END)
    tabla.selection_remove(tabla.selection())


def actualizar_tabla():
    for item in tabla.get_children():
        tabla.delete(item)

    cursor.execute("""
        SELECT id, sensor, nivel, estado, fecha
        FROM mediciones
        ORDER BY id DESC
    """)

    for fila in cursor.fetchall():
        tabla.insert("", tk.END, values=fila)


def agregar():
    if not sensor.get().strip() or not nivel.get().strip():
        messagebox.showwarning(
            "Datos incompletos",
            "Ingresá el sensor y el nivel de agua."
        )
        return

    try:
        valor = float(nivel.get())
    except ValueError:
        messagebox.showerror(
            "Error",
            "El nivel debe ser un número."
        )
        return

    if valor < 0:
        messagebox.showerror(
            "Error",
            "El nivel no puede ser negativo."
        )
        return

    estado_actual = obtener_estado(valor)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO mediciones (sensor, nivel, estado, fecha)
        VALUES (?, ?, ?, ?)
    """, (sensor.get().strip(), valor, estado_actual, fecha))

    conn.commit()

    estado.set(estado_actual)

    area.insert(
        tk.END,
        f"Medición registrada: {valor}% - Estado: {estado_actual}\n"
    )

    actualizar_tabla()


def seleccionar(event=None):
    seleccionado = tabla.selection()

    if not seleccionado:
        return

    datos = tabla.item(seleccionado[0], "values")

    id_medicion.set(datos[0])
    sensor.set(datos[1])
    nivel.set(datos[2])
    estado.set(datos[3])

    area.delete("1.0", tk.END)
    area.insert(
        tk.END,
        f"ID: {datos[0]}\n"
        f"Sensor: {datos[1]}\n"
        f"Nivel: {datos[2]}%\n"
        f"Estado: {datos[3]}\n"
        f"Fecha: {datos[4]}\n"
    )


def buscar():
    termino = sensor.get().strip()

    if not termino:
        messagebox.showwarning(
            "Buscar",
            "Ingresá el nombre del sensor."
        )
        return

    for item in tabla.get_children():
        tabla.delete(item)

    cursor.execute("""
        SELECT id, sensor, nivel, estado, fecha
        FROM mediciones
        WHERE sensor LIKE ?
        ORDER BY id DESC
    """, (f"%{termino}%",))

    resultados = cursor.fetchall()

    for fila in resultados:
        tabla.insert("", tk.END, values=fila)

    if not resultados:
        messagebox.showinfo(
            "Buscar",
            "No se encontraron mediciones."
        )
    else:
        area.delete("1.0", tk.END)
        area.insert(
            tk.END,
            f"Se encontraron {len(resultados)} medición(es).\n"
        )


def eliminar():
    if not id_medicion.get():
        messagebox.showwarning(
            "Eliminar",
            "Seleccioná una medición de la tabla."
        )
        return

    confirmar = messagebox.askyesno(
        "Eliminar",
        "¿Querés eliminar la medición seleccionada?"
    )

    if confirmar:
        cursor.execute(
            "DELETE FROM mediciones WHERE id = ?",
            (int(id_medicion.get()),)
        )
        conn.commit()

        area.insert(tk.END, "Medición eliminada correctamente.\n")

        actualizar_tabla()
        limpiar()


def actualizar():
    if not id_medicion.get():
        messagebox.showwarning(
            "Actualizar",
            "Seleccioná una medición de la tabla."
        )
        return

    try:
        valor = float(nivel.get())
    except ValueError:
        messagebox.showerror(
            "Error",
            "El nivel debe ser un número."
        )
        return

    estado_actual = obtener_estado(valor)

    cursor.execute("""
        UPDATE mediciones
        SET sensor = ?, nivel = ?, estado = ?
        WHERE id = ?
    """, (
        sensor.get().strip(),
        valor,
        estado_actual,
        int(id_medicion.get())
    ))

    conn.commit()

    estado.set(estado_actual)
    area.insert(tk.END, "Medición actualizada correctamente.\n")
    actualizar_tabla()


def mostrar_todas():
    actualizar_tabla()
    area.delete("1.0", tk.END)
    area.insert(tk.END, "Mostrando todas las mediciones.\n")


def salir():
    conn.close()
    aplicacion.destroy()


# ---------------- VENTANA ----------------
aplicacion = tk.Tk()
aplicacion.title("Hidro-Sensores - Sistema de Monitoreo")
aplicacion.geometry("1100x650")
aplicacion.minsize(1000, 600)
aplicacion.configure(bg="#024A86")

titulo = tk.Label(
    aplicacion,
    text="💧 HIDRO-SENSORES - SISTEMA DE MONITOREO",
    bd=10,
    relief=tk.RIDGE,
    font=("Arial Black", 19),
    bg="#3891C8",
    fg="white"
)
titulo.pack(fill=tk.X, padx=5, pady=5)

# ---------------- VARIABLES ----------------
id_medicion = tk.StringVar()
sensor = tk.StringVar()
nivel = tk.StringVar()
estado = tk.StringVar()

# ---------------- DATOS DE MEDICIÓN ----------------
informacion = tk.LabelFrame(
    aplicacion,
    text="Datos del Sensor",
    font=("Arial Black", 12),
    bg="#3891C8",
    fg="white",
    relief=tk.GROOVE,
    bd=8
)
informacion.place(x=10, y=75, width=480, height=310)

campos = [
    ("ID:", id_medicion),
    ("Sensor:", sensor),
    ("Nivel de agua (%):", nivel),
    ("Estado:", estado)
]

for fila, (texto, variable) in enumerate(campos):
    tk.Label(
        informacion,
        text=texto,
        font=("Arial Black", 12),
        bg="#3891C8",
        fg="white"
    ).grid(row=fila, column=0, padx=10, pady=12, sticky="w")

    entrada = tk.Entry(
        informacion,
        textvariable=variable,
        width=22,
        font=("Arial", 11),
        bd=3
    )
    entrada.grid(row=fila, column=1, padx=5, pady=12)

# ---------------- INFORMACIÓN DEL SISTEMA ----------------
info = tk.LabelFrame(
    aplicacion,
    text="Información",
    font=("Arial Black", 12),
    bg="#3891C8",
    fg="white",
    relief=tk.GROOVE,
    bd=8
)
info.place(x=10, y=400, width=480, height=90)

tk.Label(
    info,
    text="BAJO: < 30%     NORMAL: 30% - 70%     ALTO: > 70%",
    font=("Arial", 11, "bold"),
    bg="#3891C8",
    fg="white"
).pack(pady=12)

# ---------------- ÁREA DE IMPRESIÓN ----------------
frame_impresion = tk.Frame(
    aplicacion,
    bd=8,
    relief=tk.GROOVE,
    bg="#3891C8"
)
frame_impresion.place(x=510, y=75, width=575, height=150)

tk.Label(
    frame_impresion,
    text="Área de Impresión",
    font=("Arial Black", 14),
    bg="#3891C8",
    fg="white"
).pack(fill=tk.X)

scroll = tk.Scrollbar(frame_impresion)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

area = tk.Text(
    frame_impresion,
    font=("Arial", 10),
    yscrollcommand=scroll.set
)
area.pack(fill=tk.BOTH, expand=True)
scroll.config(command=area.yview)

# ---------------- TABLA ----------------
frame_tabla = tk.Frame(
    aplicacion,
    bg="#3891C8",
    bd=6,
    relief=tk.GROOVE
)
frame_tabla.place(x=510, y=235, width=575, height=255)

columnas = ("ID", "Sensor", "Nivel %", "Estado", "Fecha")

tabla = ttk.Treeview(
    frame_tabla,
    columns=columnas,
    show="headings"
)

anchos = (45, 100, 80, 90, 210)

for columna, ancho in zip(columnas, anchos):
    tabla.heading(columna, text=columna)
    tabla.column(columna, width=ancho, anchor="center")

scroll_tabla = ttk.Scrollbar(
    frame_tabla,
    orient=tk.VERTICAL,
    command=tabla.yview
)

tabla.configure(yscrollcommand=scroll_tabla.set)

tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_tabla.pack(side=tk.RIGHT, fill=tk.Y)

tabla.bind("<<TreeviewSelect>>", seleccionar)

# ---------------- BOTONES ----------------
botones = tk.LabelFrame(
    aplicacion,
    text="Operaciones",
    font=("Arial Black", 12),
    relief=tk.GROOVE,
    bd=8,
    bg="#3891C8",
    fg="white"
)
botones.place(x=10, y=510, width=1075, height=90)

frame_botones = tk.Frame(
    botones,
    bg="#024A86",
    bd=5,
    relief=tk.GROOVE
)
frame_botones.pack(fill=tk.BOTH, expand=True)

estilo_boton = {
    "font": ("Arial Black", 10),
    "width": 11,
    "bg": "#3891C8",
    "fg": "white",
    "activebackground": "#2678A8",
    "activeforeground": "white"
}

tk.Button(
    frame_botones, text="Agregar",
    command=agregar, **estilo_boton
).grid(row=0, column=0, padx=7, pady=10)

tk.Button(
    frame_botones, text="Buscar",
    command=buscar, **estilo_boton
).grid(row=0, column=1, padx=7, pady=10)

tk.Button(
    frame_botones, text="Mostrar Todo",
    command=mostrar_todas, **estilo_boton
).grid(row=0, column=2, padx=7, pady=10)

tk.Button(
    frame_botones, text="Limpiar",
    command=limpiar, **estilo_boton
).grid(row=0, column=3, padx=7, pady=10)

tk.Button(
    frame_botones, text="Eliminar",
    command=eliminar, **estilo_boton
).grid(row=0, column=4, padx=7, pady=10)

tk.Button(
    frame_botones, text="Actualizar",
    command=actualizar, **estilo_boton
).grid(row=0, column=5, padx=7, pady=10)

tk.Button(
    frame_botones, text="Salir",
    command=salir, **estilo_boton
).grid(row=0, column=6, padx=7, pady=10)

actualizar_tabla()
aplicacion.protocol("WM_DELETE_WINDOW", salir)

aplicacion.mainloop()
