import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN no encontrado en variables de entorno")

app = ApplicationBuilder().token(TOKEN).build()

URL = "https://docs.google.com/spreadsheets/d/1dBOYaPLZEreVe6gmGonHIGu4_sMD0nye/export?format=csv"

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()

    if not texto.isdigit():
        await update.message.reply_text("❌ Envia solo tu ID de empleado (ej: 1)")
        return

    df = pd.read_csv(URL)
    df["Empleado"] = df["Empleado"].astype(str).str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

    ventas = df[df["Empleado"] == texto]

    cantidad = len(ventas)
    total = int(ventas["Total"].sum())

    await update.message.reply_text(
        f"📊 Ventas del empleado {texto}\n\n"
        f"🧾 Ventas realizadas: {cantidad}\n"
        f"💰 Total vendido: ${total:,} COP"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("🤖 Bot activo 24/7 en Railway")
app.run_polling()

