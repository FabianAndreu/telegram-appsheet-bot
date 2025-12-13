import os
import pandas as pd
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN no encontrado en variables de entorno")

URL = "https://docs.google.com/spreadsheets/d/1dBOYaPLZEreVe6gmGonHIGu4_sMD0nye/export?format=csv"

# Guardaremos la última cantidad de ventas por empleado para detectar nuevas
ultimo_registro = {}

def obtener_ventas(id_empleado):
    df = pd.read_csv(URL)
    df["Empleado"] = df["Empleado"].astype(str).str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    ventas = df[df["Empleado"] == str(id_empleado)]
    return len(ventas), int(ventas["Total"].sum())

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit():
        await update.message.reply_text("❌ Envía solo tu ID de empleado")
        return

    cantidad, total = obtener_ventas(texto)

    await update.message.reply_text(
        f"📊 Ventas del empleado {texto}\n\n"
        f"🧾 Ventas realizadas: {cantidad}\n"
        f"💰 Total vendido: ${total:,} COP"
    )

# ✅ Función de automatización
async def verificar_nuevas_ventas(bot: Bot):
    global ultimo_registro
    df = pd.read_csv(URL)
    df["Empleado"] = df["Empleado"].astype(str).str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

    empleados = df["Empleado"].unique()
    for emp in empleados:
        ventas_emp = df[df["Empleado"] == emp]
        cantidad_actual = len(ventas_emp)
        total_actual = int(ventas_emp["Total"].sum())

        # Si hay registro previo
        if emp in ultimo_registro:
            cantidad_prev, total_prev = ultimo_registro[emp]
            if cantidad_actual > cantidad_prev:  # Nueva venta detectada
                nuevas_ventas = cantidad_actual - cantidad_prev
                total_nuevo = total_actual - total_prev
                await bot.send_message(
                    chat_id=emp,  # Aquí suponemos que el chat_id es el mismo que ID empleado
                    text=(
                        f"🆕 Nueva venta registrada!\n\n"
                        f"🧾 Cantidad nueva: {nuevas_ventas}\n"
                        f"💰 Total de esta venta: ${total_nuevo:,} COP\n"
                        f"📊 Ventas totales: {cantidad_actual}\n"
                        f"💰 Total vendido: ${total_actual:,} COP"
                    )
                )

        # Actualizamos el registro
        ultimo_registro[emp] = (cantidad_actual, total_actual)

async def job_periodico(app):
    while True:
        await verificar_nuevas_ventas(app.bot)
        await asyncio.sleep(60)  # Cada 60 segundos revisa nuevas ventas

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # Ejecutamos la tarea de manera paralela
    loop = asyncio.get_event_loop()
    loop.create_task(job_periodico(app))

    print("🤖 Bot activo 24/7 con automatización de ventas")
    app.run_polling()

