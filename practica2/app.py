from flask import Flask, render_template, request, redirect, flash
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cualquier-texto-secreto"

ARCHIVO = "shows.json"

# Lista de shows con los que arranca el programa
DATOS_INICIALES = [
    {"id": "ESC1-01", "escenario": "Escenario Principal", "artista": "Los Rockeros del Norte", "inicio": "16:00", "duracion": 90},
    {"id": "ESC2-01", "escenario": "Escenario Indie",     "artista": "Banda de Garaje",         "inicio": "16:00", "duracion": 45},
    {"id": "ESC1-02", "escenario": "Escenario Principal", "artista": "DJ Tormenta",              "inicio": "18:00", "duracion": 60},
    {"id": "ESC2-02", "escenario": "Escenario Indie",     "artista": "Cantautor Solitario",      "inicio": "18:30", "duracion": 45},
    {"id": "ESC1-03", "escenario": "Escenario Principal", "artista": "Leyendas del Pop",         "inicio": "21:00", "duracion": 120},
]

# ── Leer y guardar el archivo JSON ───────────────────────────────

def cargar():
    # Si ya existe el archivo, lo lee y regresa la lista
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, encoding="utf-8") as f:
            return json.load(f)
    # Si no existe el archivo, usa los datos iniciales de arriba
    return DATOS_INICIALES[:]

def guardar(shows):
    # Escribe la lista de shows en el archivo JSON
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(shows, f, ensure_ascii=False, indent=4)

# ── Ordenar por hora de inicio ───────────────────────────────────

def generar_id(shows):
    # Cuenta cuántos shows hay y le suma 1 para el nuevo
    # Ejemplo: si hay 5 shows, el nuevo será SHOW-06
    numero = len(shows) + 1
    return f"SHOW-{numero:02d}"   # :02d = siempre 2 dígitos (01, 02, 03...)

def ordenar(shows):
    # sorted() ordena la lista
    # key= le dice por qué campo ordenar (la hora de inicio)
    return sorted(shows, key=lambda x: datetime.strptime(x["inicio"], "%H:%M"))

# ── Rutas (páginas) ──────────────────────────────────────────────

# Página principal: muestra el formulario y la tabla
@app.route("/")
def index():
    shows = cargar()          # carga los shows del JSON
    shows = ordenar(shows)    # los ordena por hora
    return render_template("index.html", shows=shows)

# Agregar un show nuevo (el formulario manda los datos aquí)
@app.route("/agregar", methods=["POST"])
def agregar():
    # request.form.get() lee lo que el usuario escribió en el formulario
    escenario = request.form.get("escenario", "").strip()
    artista   = request.form.get("artista", "").strip()
    inicio    = request.form.get("inicio", "").strip()
    duracion  = request.form.get("duracion", "").strip()

    # Validar que no haya campos vacíos
    if not escenario or not artista or not inicio or not duracion:
        flash("Llena todos los campos.", "error")
        return redirect("/")

    # Validar que la duración sea un número
    if not duracion.isdigit():
        flash("La duración debe ser un número.", "error")
        return redirect("/")

    shows = cargar()

    # El ID se genera solo, el usuario no lo escribe
    id_show = generar_id(shows)

    # Crear el show como diccionario y agregarlo a la lista
    nuevo_show = {
        "id": id_show,
        "escenario": escenario,
        "artista": artista,
        "inicio": inicio,
        "duracion": int(duracion)   # convertir a número entero
    }

    shows.append(nuevo_show)   # lo agrega al final de la lista
    guardar(shows)             # guarda la lista actualizada en el JSON

    flash(f"Show '{artista}' agregado correctamente.", "ok")
    return redirect("/")

# Editar un show: carga sus datos en el formulario
@app.route("/editar/<id_show>")
def editar(id_show):
    shows = cargar()

    # Busca el show que tenga ese ID
    show = None
    for s in shows:
        if s["id"] == id_show:
            show = s
            break

    if show is None:
        flash("No se encontró ese show.", "error")
        return redirect("/")

    # Manda el show encontrado al HTML para llenar el formulario
    return render_template("index.html", shows=ordenar(shows), editando=show)

# Guardar los cambios de edición
@app.route("/guardar_edicion/<id_show>", methods=["POST"])
def guardar_edicion(id_show):
    escenario = request.form.get("escenario", "").strip()
    artista   = request.form.get("artista", "").strip()
    inicio    = request.form.get("inicio", "").strip()
    duracion  = request.form.get("duracion", "").strip()

    if not duracion.isdigit():
        flash("La duración debe ser un número.", "error")
        return redirect(f"/editar/{id_show}")

    shows = cargar()

    # Busca el show por ID y actualiza sus datos
    for s in shows:
        if s["id"] == id_show:
            s["escenario"] = escenario
            s["artista"]   = artista
            s["inicio"]    = inicio
            s["duracion"]  = int(duracion)
            break

    guardar(shows)
    flash("Show actualizado correctamente.", "ok")
    return redirect("/")

# Eliminar un show por su ID
@app.route("/eliminar/<id_show>", methods=["POST"])
def eliminar(id_show):
    shows = cargar()

    # Filtra la lista quitando el show con ese ID
    shows = [s for s in shows if s["id"] != id_show]

    guardar(shows)
    flash(f"Show {id_show} eliminado.", "ok")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)