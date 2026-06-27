from flask import Flask, render_template
import asyncio
import threading
from bot_core import state, bot_loop

app = Flask(__name__)

# ============================================================
# ROTAS DO PAINEL
# ============================================================

@app.route("/")
def painel():
    return render_template("painel.html", state=state, logs="\n".join(state.log))


@app.route("/start")
def start_bot():
    state.running = True
    state.paused = False
    state.last_action = "Bot iniciado"
    state.add_log(state.last_action)
    return "Bot iniciado"


@app.route("/pause")
def pause_bot():
    if state.running:
        state.paused = not state.paused
        if state.paused:
            state.last_action = "Bot pausado"
        else:
            state.last_action = "Bot retomado"
        state.add_log(state.last_action)
        return state.last_action
    return "Bot não está ativo"


@app.route("/stop")
def stop_bot():
    state.running = False
    state.paused = False
    state.last_action = "Bot parado"
    state.add_log(state.last_action)
    return "Bot parado"


# ============================================================
# LOOP DO BOT EM BACKGROUND
# ============================================================

def start_background_loop():
    asyncio.run(bot_loop())

# Inicia o loop numa thread separada
threading.Thread(target=start_background_loop, daemon=True).start()


# ============================================================
# INÍCIO DO FLASK (LOCAL)
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
