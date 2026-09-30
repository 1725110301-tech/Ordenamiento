"""
3er sistema - Sistema de atención de tickets (Flask)
Estructura de datos: Fila (cola) FIFO con deque.
Dos filas: prioritaria y normal. La prioritaria se atiende primero.
"""
from collections import deque
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "tickets-secret"


class Ticket:
    def __init__(self, numero, cliente, problema, prioridad, tiempo):
        self.numero = numero
        self.cliente = cliente
        self.problema = problema
        self.prioridad = prioridad
        self.tiempo = tiempo

    def __str__(self):
        return (f"#{self.numero} | {self.cliente} | {self.problema} | "
                f"{self.prioridad} | {self.tiempo} min")


class SistemaTickets:
    def __init__(self):
        self.fila_normal = deque()
        self.fila_prioritaria = deque()
        self.atendidos = []
        self.contador = 0

    def registrar(self, cliente, problema, prioridad, tiempo):
        self.contador += 1
        t = Ticket(self.contador, cliente, problema, prioridad, tiempo)
        (self.fila_prioritaria if prioridad == "prioritaria"
         else self.fila_normal).append(t)  # enqueue
        return t

    def _siguiente(self):
        if self.fila_prioritaria:
            return self.fila_prioritaria, self.fila_prioritaria[0]
        if self.fila_normal:
            return self.fila_normal, self.fila_normal[0]
        return None, None

    def atender(self):
        fila, t = self._siguiente()
        if t is None:
            return None
        fila.popleft()  # dequeue (FIFO)
        self.atendidos.append(t)
        return t

    def consultar(self):
        return self._siguiente()[1]

    def estadisticas(self):
        total = len(self.atendidos)
        minutos = sum(t.tiempo for t in self.atendidos)
        pri = sum(1 for t in self.atendidos if t.prioridad == "prioritaria")
        mayor = max(self.atendidos, key=lambda t: t.tiempo) if total else None
        return {
            "atendidos": total,
            "pendientes": len(self.fila_normal) + len(self.fila_prioritaria),
            "pend_pri": len(self.fila_prioritaria),
            "pend_nor": len(self.fila_normal),
            "total_min": minutos,
            "promedio": f"{minutos / total:.2f}" if total else "0.00",
            "at_pri": pri,
            "at_nor": total - pri,
            "mayor": f"#{mayor.numero} ({mayor.tiempo} min)" if mayor else "—",
        }


sistema = SistemaTickets()


@app.route("/")
def index():
    return render_template("index.html",
                           prioritaria=sistema.fila_prioritaria,
                           normal=sistema.fila_normal,
                           sig=sistema.consultar(),
                           e=sistema.estadisticas())


@app.route("/registrar", methods=["POST"])
def registrar():
    cliente = request.form.get("cliente", "").strip()
    problema = request.form.get("problema", "").strip()
    prioridad = request.form.get("prioridad", "normal")
    try:
        tiempo = int(request.form.get("tiempo", ""))
        if tiempo <= 0:
            raise ValueError
    except ValueError:
        flash("El tiempo debe ser un entero mayor que 0.", "error")
        return redirect(url_for("index"))
    if not cliente or not problema:
        flash("Completa cliente y problema.", "error")
        return redirect(url_for("index"))
    t = sistema.registrar(cliente, problema, prioridad, tiempo)
    flash(f"Ticket registrado: {t}", "ok")
    return redirect(url_for("index"))


@app.route("/atender", methods=["POST"])
def atender():
    t = sistema.atender()
    if t:
        flash(f"Atendiendo: {t}", "ok")
    else:
        flash("No hay tickets en espera.", "error")
    return redirect(url_for("index"))


@app.route("/consultar", methods=["POST"])
def consultar():
    t = sistema.consultar()
    flash(f"Siguiente: {t}" if t else "No hay tickets en espera.",
          "ok" if t else "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)