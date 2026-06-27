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
    state.running = True
    state.paused = False
    state.add_log("Bot iniciado")
    return redirect("/")

@app.route("/stop")
def stop():
    state.running = False
    state.add_log("Bot parado")
    return redirect("/")

@app.route("/pause")
def pause():
    state.paused = not state.paused
    state.add_log("Bot pausado/retomado")
    return redirect("/")

def start_bot():
    asyncio.run(bot_loop())

threading.Thread(target=start_bot, daemon=True).start()

app.run(host="0.0.0.0", port=8080)
