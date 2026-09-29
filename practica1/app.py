from flask import Flask, render_template, request, redirect, url_for, flash
import json, os

app = Flask(__name__)
app.secret_key = "clave-secreta"

ARCHIVO = "fila.json"

# Lee el archivo JSON y regresa la lista de estudiantes
def cargar_fila():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, encoding="utf-8") as f:
            return json.load(f)
    return []  # si no existe el archivo, regresa lista vacía

# Guarda la lista de estudiantes en el archivo JSON
def guardar_fila(fila):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(fila, f, ensure_ascii=False, indent=2)


# Página principal: muestra el formulario y la fila
@app.route("/")
def index():
    fila = cargar_fila()
    return render_template("index.html", fila=fila)


# Agrega un estudiante al FINAL de la fila (encolar)
@app.route("/agregar", methods=["POST"])
def agregar():
    matricula = request.form.get("matricula", "").strip()
    nombre    = request.form.get("nombre", "").strip()
    carrera   = request.form.get("carrera", "").strip()
    tramite   = request.form.get("tramite", "").strip()

    # Validar que no haya campos vacíos
    if not matricula or not nombre or not carrera or not tramite:
        flash("Por favor llena todos los campos.", "error")
        return redirect(url_for("index"))

    # Crear el estudiante como diccionario y agregarlo a la lista
    estudiante = {
        "matricula": matricula,
        "nombre": nombre,
        "carrera": carrera,
        "tramite": tramite
    }

    fila = cargar_fila()
    fila.append(estudiante)   # lo manda al final de la fila
    guardar_fila(fila)

    flash(f"{nombre} fue agregado a la fila.", "ok")
    return redirect(url_for("index"))


# Atiende al estudiante del FRENTE de la fila (desencolar)
@app.route("/atender", methods=["POST"])
def atender():
    fila = cargar_fila()

    if len(fila) == 0:
        flash("La fila está vacía, no hay nadie que atender.", "error")
        return redirect(url_for("index"))

    # pop(0) saca al primero de la lista (el que lleva más tiempo esperando)
    estudiante = fila.pop(0)
    guardar_fila(fila)

    flash(f"Atendiendo a {estudiante['nombre']} — Trámite: {estudiante['tramite']}", "ok")
    return redirect(url_for("index"))


# Borra toda la fila
@app.route("/limpiar", methods=["POST"])
def limpiar():
    guardar_fila([])
    flash("La fila fue limpiada.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
