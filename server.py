
from flask import Flask, render_template, redirect
import threading
import asyncio
from bot_core import state, bot_loop

app = Flask(__name__)

@app.route("/")
def painel():
    return render_template("painel.html", state=state)

@app.route("/start")
def start():
    if not state.running:
        state.running = True
        state.paused = False
        state.add_log("Bot iniciado")

        # Inicia o bot numa thread separada
        threading.Thread(target=lambda: asyncio.run(bot_loop()), daemon=True).start()

    return redirect("/")

@app.route("/stop")
def stop():
    state.running = False
    state.paused = False
    state.add_log("Bot parado")
    return redirect("/")

@app.route("/pause")
def pause():
    state.paused = not state.paused
    state.add_log("Bot pausado/retomado")
    return redirect("/")

# IMPORTANTE: NÃO iniciar o bot automaticamente no Render
# Apenas iniciar o Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
