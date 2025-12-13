import pandas as pd
import time
from telegram.ext import Updater, MessageHandler, Filters

# 🔐 TOKEN
TOKEN = "8372925592:AAEMdRQ4EKgcXol3ac1kItUJFQSiiCveF2s"

# 📊 CSV DE VENTAS (VENTAS EN LA PRIMERA HOJA)
URL = "https://docs.google.com/spreadsheets/d/1dBOYaPLZEreVe6gmGonHIGu4_sMD0nye/export?format=csv"

# 📦 USUARIOS REGISTRADOS
usuarios = {}  
# chat_id : { "empleado": "1", "ventas_vistas": 0 }

def leer_ventas():
    df = pd.read_csv(URL)

    df["Empleado"] = df["Empleado"].astype(str).str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    df["Fecha"] = df["Fecha"].astype(str)

    return df

def registrar_empleado(update, context):
    texto = update.message.text.strip()
    chat_id = update.message.chat_id

    if not texto.isdigit():
        update.message.reply_text("❌ Envía solo tu ID de empleado (ej: 1)")
        return

    df = leer_ventas()
    ventas = df[df["Empleado"] == texto]

    usuarios[chat_id] = {
        "empleado": texto,
        "ventas_vistas": len(ventas)
    }

    update.message.reply_text(
        f"✅ Empleado {texto} registrado\n"
        f"👀 A partir de ahora recibirás notificaciones automáticas"
    )

def monitor_ventas(context):
    df = leer_ventas()

    for chat_id, info in usuarios.items():
        emp = info["empleado"]
        ventas_emp = df[df["Empleado"] == emp]

        if len(ventas_emp) > info["ventas_vistas"]:
            nuevas = ventas_emp.iloc[info["ventas_vistas"]:]

            for _, v in nuevas.iterrows():
                context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "🆕 NUEVA VENTA REGISTRADA\n\n"
                        f"👤 Empleado: {emp}\n"
                        f"📅 Fecha: {v['Fecha']}\n"
                        f"💰 Total: ${int(v['Total']):,} COP"
                    )
                )

            usuarios[chat_id]["ventas_vistas"] = len(ventas_emp)

# 🚀 BOT
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, registrar_empleado))

# ⏱️ REVISA CADA 5 SEGUNDOS
updater.job_queue.run_repeating(monitor_ventas, interval=5, first=5)

print("🤖 Bot activo y leyendo ventas...")
updater.start_polling()
updater.idle()
