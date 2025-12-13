import os
import pandas as pd
from fastapi import FastAPI, Request
from telegram import Bot
import uvicorn

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN no encontrado en variables de entorno")

bot = Bot(token=TOKEN)
app = FastAPI()

# Mapeo de ID empleado a chat_id (modifica según tus chats)
empleado_chat = {
    "1001": 123456789,  # ID empleado : chat_id de Telegram
    "1002": 987654321,
    # agrega todos tus empleados
}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    empleado = str(data.get("empleado"))
    total = float(data.get("total", 0))
    fecha = data.get("fecha", "Desconocida")

    chat_id = empleado_chat.get(empleado)
    if chat_id:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"🆕 Nueva venta registrada!\n\n"
                f"🧾 Total de la venta: ${int(total):,} COP\n"
                f"📅 Fecha: {fecha}"
            )
        )
    return {"status": "ok"}
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
