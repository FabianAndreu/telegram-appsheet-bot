import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# 🔐 TOKEN DESDE VARIABLE DE ENTORNO
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN no encontrado en variables de entorno")

# 📊 CSV DE GOOGLE SHEETS (VENTAS PRIMERA HOJA)
URL = "https://docs.google.com/spreadsheets/d/1dBOYaPLZEreVe6gmGonHIGu4_sMD0nye/export?format=csv"

def obtener_ventas(id_empleado):
    df = pd.read_csv(URL)

    df["Empleado"] = df["Empleado"].astype(str).str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

    ventas = df[df["Empleado"] == str(id_empleado)]

    cantidad = len(ventas)
    total = int(ventas["Total"].sum())

    return cantidad, total

# 📩 RESPUESTA DEL BOT
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()

    if not texto.isdigit():
        await update.message.reply_text("❌ Envia solo tu ID de empleado (ej: 1)")
        return

    cantidad, total = obtener_ventas(texto)

    await update.message.reply_text(
        f"📊 Ventas del empleado {texto}\n\n"
        f"🧾 Ventas realizadas: {cantidad}\n"
        f"💰 Total vendido: ${total:,} COP"
    )

# 🚀 ARRANQUE
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("🤖 Bot activo 24/7 en Railway")
    app.run_polling()
