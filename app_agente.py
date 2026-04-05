
import streamlit as st
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import base64

# ==========================================
# CONFIGURACIÓN VISUAL (Tu diseño original)
# ==========================================
st.set_page_config(page_title="CRM IMAGECOLOMBIA", page_icon="📈", layout="centered")


# --- LÓGICA DE CLASIFICACIÓN (EL CEREBRO) ---
def clasificar_lead(presupuesto, motivo):
    """Asigna una prioridad basada en el valor y la intención del cliente."""
    score = 0
    
    # Puntos por Presupuesto
    if presupuesto == "Más de 4M": score += 15
    elif presupuesto == "Entre 3M y 4M": score += 10
    elif presupuesto == "Entre 2M y 3M": score += 5
    
    # Puntos por Motivo
    if motivo == "Iniciar proyecto o servicio": score += 15
    elif motivo == "Asesoría de servicios": score += 5
    
    # Clasificación Final
    if score >= 25: return "🔴 ALTA (Prioridad Oro)"
    elif score >= 10: return "🟡 MEDIA (Seguimiento)"
    else: return "🟢 BAJA (Informativo)"

# ==========================================
# INICIO DEL CÓDIGO DE DISEÑO CSS
# ==========================================
st.markdown(
    """
    <style>
    /* 1. Fondo de la aplicación */
    .stApp {
        background-color: #01153e; 
    }

    /* 2. El NUEVO Contenedor para Logo + Título */
    .encabezado-compacto {
        display: flex;
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        text-align: center;
        margin-top: 0px; 
        margin-bottom: 20px; 
    }

    /* 3. Estilo para el Logo dentro del contenedor */
    .encabezado-compacto img {
        margin-bottom: 1px !important; 
        padding: 0 !important;
    }

    /* 4. Estilo del Título Principal dentro del contenedor */
    .titulo-personalizado {
        color: #ffffff;
        font-size: 45px !important;
        font-weight: bold;
        margin-top: 0 !important; 
        padding-top: 0 !important;
        padding-bottom: 10px;
        text-align: center; 
        margin-bottom: 10px;

        /* --- LA LÍNEA DECORATIVA --- */
        border-bottom: 4px solid #14db64; 
        display: inline-block; 
        padding-bottom: 10px; 
        width: 100%; 
    }

    /* 3. Estilo para el texto de abajo si también lo quieres centrado */
    .subtitulo-personalizado {
        color: #ccd1d1; 
        text-align: center; 
        margin-bottom: 30px;
    }

    /* 4. Estilo del cuadro (Formulario) con SOMBRA */
    [data-testid="stForm"] {
        background-color: rgba(14, 125, 38, 0.7); 
        padding: 2.5em;
        border-radius: 20px;
        border: none;
        box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.5); 
    }

    /* 6. Estilo de los campos de texto */
    input {
        background-color: #e0fcf1 !important; 
        border-radius: 12px !important; 
        color: #01153e !important; 
        font-weight: bold !important; 
        text-transform: uppercase; 
    }
    
    /* 7. Color de las etiquetas (labels) */
    label p {
        color: #ffffff !important; 
        font-weight: 600;
        font-size: 1.1em;
    }

    /* 8. Estilo para el selectbox y otros widgets */
    div[data-baseweb="select"] > div {
        background-color: #e0fcf1 !important;
        color: #01153e !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
    }

    /* 9. Estilo del Botón de Registro FORZADO */
    [data-testid="stForm"] button {
        background-color: #b6ffad; 
        color: #01153e; 
        font-size: 20px; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 12px; 
        border: none; 
        padding: 18px; 
        transition: all 0.3s ease; 
        box-shadow: 0px 5px 20px rgba(20, 219, 100, 0.3); 
    }

    /* 10. Efecto al pasar el mouse (Hover) FORZADO */
    [data-testid="stForm"] button:hover {
        background-color: #f29327; 
        color: white;
        transform: scale(1.02); 
        box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.4); 
    }

    /* edicion del menu desplegable del selectbox */
    div[data-baseweb="popover"], 
    div[data-baseweb="popover"] > div, 
    div[data-baseweb="popover"] ul {
        background-color: rgba(1, 21, 62, 0.7) !important; 
        border-radius: 15px !important; 
        border: 1px solid #14db64 !important; 
    }

    [role="option"]:hover, 
    [role="option"]:hover > div, 
    [aria-selected="true"] {
        background-color: rgba(242, 147, 39, 0.6) !important; 
        color: #ffffff !important;
        cursor: pointer;
    }

    [role="option"]:hover * {
        background-color: transparent !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# Carga del Logo 
# ==========================================
import base64

def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        # Imagen temporal si no encuentra el logo
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

logo_base64 = get_image_base64("logo.png") 

st.markdown(
    f"""
    <div class="encabezado-compacto">
        <img src="data:image/png;base64,{logo_base64}" width="200">
        <p class="titulo-personalizado">Sistema de Ingreso de Leads</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <p class="subtitulo-personalizado">
        Bienvenida al panel de registro manual para agentes de IMAGECOLOMBIA Publicidad. <br>
        Querido agente, recuerde llenar todos los campos correctamente, no deje campo sin llenar. Gracias.
    </p>
    """, unsafe_allow_html=True)


# ==========================================
# FUNCIONES DE BASE DE DATOS (NUEVO MOTOR)
# ==========================================
# 1. Función para Guardar (SQL Local)
def guardar_en_sql(datos):
    conn = sqlite3.connect('agencia_leads.db')
    cursor = conn.cursor()
    # Creamos la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nombre TEXT,
            contacto TEXT,
            correo TEXT,
            categoria TEXT,
            presupuesto TEXT,
            motivo TEXT,
            observaciones TEXT,
            prioridad TEXT
        )
    ''')
    # Insertamos los datos
    query = '''
        INSERT INTO leads (fecha, nombre, contacto, correo, categoria, presupuesto, motivo, observaciones, prioridad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, datos)
    conn.commit()
    conn.close()

# 2. Función para Consultar (SQL Local)
def consultar_leads_sql():
    conn = sqlite3.connect('agencia_leads.db')
    df = pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC", conn)
    conn.close()
    return df

# 3. Función para Google Sheets (Nube)
def guardar_en_sheets(datos):
    try:
        # 1. Definir el alcance (Scope)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # 2. Cargar credenciales desde los Secrets de Streamlit
        # IMPORTANTE: Usa st.secrets (en inglés)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds"], scope)
        
        # 3. Autorizar el cliente
        client = gspread.authorize(creds)
        sheet = client.open("Sistema_Leads_Agencia").get_worksheet(0)
        sheet.append_row(list(datos))
    except Exception as e:
        st.error(f"Error en la nube: {e}")

# ==========================================
# FORMULARIO DE ENTRADA 
# ==========================================
with st.form("my_form"):
    st.subheader("Ingreso datos del cliente")
    
    # Campos de entrada
    nombre_raw = st.text_input("Nombre completo / Empresa")
    contacto = st.text_input("WhatsApp / Teléfono")
    correo = st.text_input("Correo Electrónico:")
    
    categoria = st.selectbox("Categoría de Servicio", [
        "Seleccione un servicio",
        "Software y/o Automatización con IA", 
        "Desarrollo web o Apps", 
        "Diseño de marcas", 
        "Marketing digital",
        "Otro"
    ])
    
    presupuesto = st.selectbox("Presupuesto Estimado", [
        "Seleccione un rango",
        "Menos de 1M",  
        "Entre 1M y 2M",
        "Entre 2M y 3M",
        "Entre 3M y 4M",
        "Más de 4M",
    ])
    
    motivo = st.selectbox("Motivo de Contacto", [
        "Seleccione su motivo",
        "Consulta general",  
        "Iniciar proyecto o servicio",
        "Asesoría de servicios",
        "Otros",
    ])
    
    observaciones = st.text_input("Prospectos adicionales y/o observaciones especificas")

    # Botón de submit
    submit = st.form_submit_button("Registrar en el Sistema")


# ==========================================
# LÓGICA DEL BOTÓN (NUEVO CABLEADO)
# ==========================================
if submit:
    # 1. Validación de campos obligatorios (Auditoría de Datos)
    if (nombre_raw == "" or contacto == "" or categoria == "Seleccione un servicio" or 
        presupuesto == "Seleccione un rango" or motivo == "Seleccione su motivo"):
        st.error("🚨 Error: Faltan campos obligatorios. Por favor rellene Nombre, WhatsApp, Categoría, Presupuesto y Motivo.")
    else:
        
        prioridad = clasificar_lead(presupuesto, motivo)
        # Preparamos los datos
        nombre = nombre_raw.upper() # Forzamos mayúsculas
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Fecha y Hora
        
        # Tupla para SQL (sin el ID, que es autoincremental 8 datos)
        datos_tupla = (fecha_actual, nombre, contacto, correo, categoria, presupuesto, motivo, observaciones, prioridad)

        # Lista para Sheets (9 datos para 9 columnas: de la A a la I)
        # Ponemos "" en el ID para que la columna A quede libre para tu ID manual
        datos_lista = ("", fecha_actual, nombre, contacto, correo, categoria, presupuesto, motivo, observaciones, prioridad)
        # 2. Guardado simultáneo (Tolerancia a Fallos)
        with st.spinner("Guardando y clasificarregistro simultáneamente en SQL y Google Sheets..."):
            # Guardamos en Local (SQL)
            guardar_en_sql(datos_tupla)
            
            # Guardamos en la Nube (Sheets)
            guardar_en_sheets(datos_lista)
        
        # 3. Mensaje de éxito
        st.balloons() # ¡Confeti visual!
        st.success(f"🎉 ¡Éxito! El lead de **{nombre}** ha sido registrado correctamente en la base de datos local y sincronizado en la nube (Google Sheets).")
        st.info("Puede verificar el registro en el repositorio de Excel compartido.")


# ==========================================
# LSECCIÓN DEL VISUALIZADOR DEL PANEL
# ==========================================
# --- SECCIÓN DEL VISUALIZADOR (DASHBOARD) ---
st.markdown("---") # Crea una línea divisoria elegante
st.subheader("📊 Panel de Control: Visualización de Leads")
st.write("Haz clic abajo para refrescar la lista de prospectos guardados en la base de datos.")

if st.button("🔄 Actualizar y Ver Tabla"):
    # Llamamos a la función que creamos arriba
    df_leads = consultar_leads_sql()
    
    if not df_leads.empty:
        # Mostramos la tabla con un diseño que use todo el ancho
        st.dataframe(df_leads, use_container_width=True)
    else:
        st.warning("Aún no hay registros en la base de datos para mostrar.")