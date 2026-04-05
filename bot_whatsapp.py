from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# --- FUNCIONES DE GUARDADO (Tus funciones originales) ---
def guardar_en_sql(datos):
    conn = sqlite3.connect('agencia_leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT, nombre TEXT, contacto TEXT, correo TEXT, 
            categoria TEXT, presupuesto TEXT, motivo TEXT, observaciones TEXT
        )
    ''')
    query = '''INSERT INTO leads (fecha, nombre, contacto, correo, categoria, presupuesto, motivo, observaciones) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor.execute(query, datos)
    conn.commit()
    conn.close()

def guardar_en_sheets(datos):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Sistema_Leads_Agencia").get_worksheet(0)
        sheet.append_row(list(datos))
    except Exception as e:
        print(f"Error en Google Sheets: {e}")

# --- LÓGICA DE IMAGBOT ---
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    # 1. Obtener el mensaje y el número del cliente
    msg_body = request.form.get('Body').strip().lower()
    numero_cliente = request.form.get('From').replace('whatsapp:', '')
    
    resp = MessagingResponse()
    msg = resp.message()

    # 2. El saludo de ImagBOT
    if msg_body in ['hola', 'buenos dias', 'buenas tardes', 'inicio', 'buenas']:
        msg.body("¡Hola! Qué gusto saludarte. Bienvenido a IMAGECOLOMBIA Publicidad. 🚀\n\n"
                 "Soy *ImagBOT* tu asistente virtual. Para brindarte una mejor experiencia, "
                 "por favor indícame tu **Nombre Completo**.")
        return str(resp)

    # 3. Registro rápido (Prototipo)
    else:
        nombre_cliente = msg_body.upper()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Datos automáticos para el primer registro del bot
        datos_sql = (fecha, nombre_cliente, numero_cliente, "Capturado por Bot", "Interés General", "Por definir", "Chatbot", "Registro Automático")
        datos_excel = ["", fecha, nombre_cliente, numero_cliente, "Capturado por Bot", "Interés General", "Por definir", "Por definir", "ChatBot"]

        try:
            guardar_en_sql(datos_sql)
            guardar_en_sheets(datos_excel)
            msg.body(f"¡Gracias {nombre_cliente}! He registrado tu contacto automáticamente en nuestro sistema. 📈\n\n"
                     "Un asesor experto de IMAGECOLOMBIA te escribirá pronto. ¡Ten un gran día!")
        except Exception as e:
            msg.body("Lo siento, tuve un pequeño error al guardar tus datos. Pero mi equipo ya está al tanto.")
            print(f"Error: {e}")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)