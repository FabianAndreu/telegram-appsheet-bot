import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# 🔐 TOKEN
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN no encontrado en variables de entorno")

# 📊 CSV DE VENTAS
URL = "https://docs.google.com/spreadsheets/d/1dBOYaPLZEreVe6gmGonHIGu4_sMD0nye/export?format=csv"

# 📦 USUARIOS REGISTRADOS
usuarios = {}  # chat_id : { "empleado": "1", "ventas_vistas": 0 }

def leer_ventas():
    df = pd.read_csv(URL)

    df["Empleado"] = df["Empleado"].astype(str).str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

    # ✅ Especificamos formato de fecha (DD/MM/YYYY)
    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    return df

async def registrar_empleado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    chat_id = update.message.chat_id

    if not texto.isdigit():
        await update.message.reply_text("❌ Envía solo tu ID de empleado (ej: 1)")
        return

    df = leer_ventas()
    ventas = df[df["Empleado"] == texto]

    usuarios[chat_id] = {
        "empleado": texto,
        "ventas_vistas": len(ventas)
    }

    await update.message.reply_text(
        f"✅ Empleado {texto} registrado\n"
        f"👀 A partir de ahora recibirás notificaciones automáticas"
    )

async def monitor_ventas(application):
    df = leer_ventas()

    for chat_id, info in usuarios.items():
        emp = info["empleado"]
        ventas_emp = df[df["Empleado"] == emp]

        if len(ventas_emp) > info["ventas_vistas"]:
            nuevas = ventas_emp.iloc[info["ventas_vistas"]:]
            for _, v in nuevas.iterrows():
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "🆕 NUEVA VENTA REGISTRADA\n\n"
                        f"👤 Empleado: {emp}\n"
                        f"📅 Fecha: {v['Fecha'].strftime('%d/%m/%Y') if pd.notna(v['Fecha']) else 'Sin fecha'}\n"
                        f"💰 Total: ${int(v['Total']):,} COP"
                    )
                )
            usuarios[chat_id]["ventas_vistas"] = len(ventas_emp)

async def job_periodico(application):
    import asyncio
    while True:
        await monitor_ventas(application)
        await asyncio.sleep(5)  # revisa cada 5 segundos

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler para registrar empleados
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), registrar_empleado))

    # Ejecutar job periódico en paralelo
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(job_periodico(app))

    print("🤖 Bot activo y monitoreando ventas...")
    app.run_polling()

