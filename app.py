import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import requests
import base64

# Configuración de la página
st.set_page_config(
    page_title="Bitácora de Entregas",
    page_icon="📊",
    layout="wide"
)

# Aplicar estilos CSS personalizados para la sidebar
st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #01E400 0%, #00C400 100%);
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] .stButton button {
        background-color: white;
        color: #01E400;
        border: 2px solid white;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #f0fff0;
        color: #00C400;
        border-color: #f0fff0;
        transform: translateY(-2px);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2, 
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: white !important;
        text-align: center;
    }
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown .stCaption {
        color: white !important;
        text-align: center;
    }
    
    /* Radio button styling */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        gap: 8px;
    }
    
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] p {
        color: #01E400 !important;
        font-weight: 600;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
        padding: 15px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Main content improvements */
    .main-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Metric cards styling */
    [data-testid="metric-container"] {
        background-color: #f8fff8;
        border: 1px solid #e6ffe6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(1,228,0,0.1);
    }
    
    /* Sidebar header styling */
    .sidebar-header {
        background: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .sidebar-header h3 {
        color: white !important;
        font-weight: 700;
        font-size: 1.2em;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .sidebar-subheader {
        background: rgba(255, 255, 255, 0.1);
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-subheader h4 {
        color: white !important;
        font-weight: 600;
        font-size: 1.1em;
        margin: 0;
    }
    
    /* Divider styling */
    .custom-divider {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Logo de GoPass
st.markdown("""
<div class="logo-container">
    <img src="https://i.imgur.com/z9xt46F.jpeg"
         style="width: 300px; border-radius: 10px;" 
         alt="Logo Gopass">
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📊 Bitácora de Entregas de Turno")
st.markdown('</div>', unsafe_allow_html=True)

# Función para cargar datos desde GitHub
@st.cache_data(ttl=60)  # Cache por 60 segundos
def cargar_datos_github():
    try:
        # Obtener configuración de GitHub desde secrets
        github_token = st.secrets["github"]["token"]
        repo_owner = st.secrets["github"]["repo_owner"]
        repo_name = st.secrets["github"]["repo_name"]
        file_path = st.secrets["github"]["file_path"]
        
        # URL de la API de GitHub
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Obtener el archivo
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            
            # Decodificar contenido
            content = base64.b64decode(file_data["content"])
            df = pd.read_excel(BytesIO(content))
            
            # Convertir columna de fecha si existe
            if 'Fecha y Hora' in df.columns:
                df['Fecha y Hora'] = pd.to_datetime(df['Fecha y Hora'])
                df['Fecha'] = df['Fecha y Hora'].dt.date
                df['Hora'] = df['Fecha y Hora'].dt.strftime('%H:%M:%S')
            
            return df, None
        
        elif response.status_code == 404:
            return None, "No se encontró el archivo. Aún no hay registros."
        
        else:
            return None, f"Error al acceder a GitHub: {response.status_code}"
    
    except KeyError as e:
        return None, f"Error de configuración: Falta {str(e)} en secrets"
    
    except Exception as e:
        return None, f"Error: {str(e)}"

# Sidebar
st.sidebar.markdown("""
<div class="sidebar-header">
    <h3>🔍 Navegación</h3>
</div>
""", unsafe_allow_html=True)

opcion = st.sidebar.radio(
    "Selecciona una opción:",
    ["📋 Ver Bitácora General", "📅 Ver Bitácora de Hoy"]
)

st.sidebar.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-subheader">
    <h4>🔄 Actualizar datos</h4>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Recargar Datos", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# Botón para redirigir al formulario
st.sidebar.link_button("📝 Ir al Formulario", 
                         url="https://formulario-aseguramiento-angeltorres.streamlit.app/", 
                         use_container_width=True):


st.sidebar.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="font-weight: 600; margin-bottom: 5px;">Bitácora de Entregas | Gopass</p>
    <p style="font-size: 0.9em; opacity: 0.9;">Created by Angel Torres</p>
</div>
""", unsafe_allow_html=True)

# Cargar datos
with st.spinner("Cargando datos desde GitHub..."):
    df, error = cargar_datos_github()

if error:
    st.error(f"❌ {error}")
    st.info("💡 Asegúrate de que el archivo exista en el repositorio y que los secrets estén configurados correctamente.")
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ No hay registros disponibles aún.")
    st.info("Los registros aparecerán aquí una vez que se completen entregas de turno.")
    st.stop()

# ========== BITÁCORA GENERAL ==========
if opcion == "📋 Ver Bitácora General":
    st.header("📋 Bitácora General de Entregas")
    
    # Estadísticas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Entregas", len(df))
    
    with col2:
        if 'Nombre' in df.columns:
            st.metric("Usuarios Activos", df['Nombre'].nunique())
    
    with col3:
        if 'Actividad' in df.columns:
            st.metric("Actividades Registradas", df['Actividad'].nunique())
    
    with col4:
        if 'Fecha' in df.columns:
            st.metric("Días con Registro", df['Fecha'].nunique())
    
    st.markdown("---")
    
    # Filtros
    st.subheader("🔍 Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Nombre' in df.columns:
            nombres = ["Todos"] + sorted(df['Nombre'].unique().tolist())
            nombre_filtro = st.selectbox("Filtrar por Usuario", nombres)
        else:
            nombre_filtro = "Todos"
    
    with col2:
        if 'Actividad' in df.columns:
            actividades = ["Todas"] + sorted(df['Actividad'].unique().tolist())
            actividad_filtro = st.selectbox("Filtrar por Actividad", actividades)
        else:
            actividad_filtro = "Todas"
    
    with col3:
        if 'Fecha' in df.columns:
            fecha_inicio = st.date_input(
                "Desde",
                value=df['Fecha'].min(),
                min_value=df['Fecha'].min(),
                max_value=df['Fecha'].max()
            )
            fecha_fin = st.date_input(
                "Hasta",
                value=df['Fecha'].max(),
                min_value=df['Fecha'].min(),
                max_value=df['Fecha'].max()
            )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if nombre_filtro != "Todos" and 'Nombre' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Nombre'] == nombre_filtro]
    
    if actividad_filtro != "Todas" and 'Actividad' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Actividad'] == actividad_filtro]
    
    if 'Fecha' in df.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['Fecha'] >= fecha_inicio) & 
            (df_filtrado['Fecha'] <= fecha_fin)
        ]
    
    st.markdown("---")
    
    # Mostrar datos filtrados
    st.subheader(f"📊 Registros Encontrados: {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        # Mostrar cada registro en un expander
        for idx, row in df_filtrado.iterrows():
            with st.expander(
                f"🕐 {row.get('Fecha', 'N/A')} {row.get('Hora', 'N/A')} - "
                f"{row.get('Nombre', 'N/A')} - {row.get('Actividad', 'N/A')}"
            ):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**📌 Información General**")
                    st.write(f"**Usuario:** {row.get('Nombre', 'N/A')}")
                    st.write(f"**Actividad:** {row.get('Actividad', 'N/A')}")
                    st.write(f"**Fecha:** {row.get('Fecha', 'N/A')}")
                    st.write(f"**Hora:** {row.get('Hora', 'N/A')}")
                
                with col2:
                    st.markdown("**📝 Detalles**")
                    
                    # Mostrar todos los campos relevantes
                    for column in df_filtrado.columns:
                        if column not in ['Fecha y Hora', 'Fecha', 'Hora', 'Nombre', 'Actividad']:
                            valor = row[column]
                            if pd.notna(valor) and str(valor).strip() != '':
                                st.write(f"**{column}:** {valor}")
        
        # Opción de descarga
        st.markdown("---")
        st.subheader("📥 Descargar Datos")
        
        # Exportar a Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Bitácora')
        output.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name=f"bitacora_general_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    else:
        st.info("No se encontraron registros con los filtros aplicados.")

# ========== BITÁCORA DE HOY ==========
elif opcion == "📅 Ver Bitácora de Hoy":
    st.header("📅 Bitácora de Hoy")
    
    # Obtener fecha de hoy
    hoy = date.today()
    st.info(f"📆 Mostrando registros del: **{hoy.strftime('%d/%m/%Y')}**")
    
    # Filtrar por fecha de hoy
    if 'Fecha' in df.columns:
        df_hoy = df[df['Fecha'] == hoy].copy()
    else:
        df_hoy = pd.DataFrame()
    
    # Estadísticas del día
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Entregas de Hoy", len(df_hoy))
    
    with col2:
        if 'Nombre' in df_hoy.columns and len(df_hoy) > 0:
            st.metric("Usuarios Hoy", df_hoy['Nombre'].nunique())
        else:
            st.metric("Usuarios Hoy", 0)
    
    with col3:
        if 'Actividad' in df_hoy.columns and len(df_hoy) > 0:
            st.metric("Actividades Hoy", df_hoy['Actividad'].nunique())
        else:
            st.metric("Actividades Hoy", 0)
    
    st.markdown("---")
    
    # FILTRO PARA BITÁCORA DE HOY
    if len(df_hoy) > 0:
        st.subheader("🔍 Filtros para Hoy")
        
        # Filtro por usuario
        if 'Nombre' in df_hoy.columns:
            usuarios_hoy = ["Todos"] + sorted(df_hoy['Nombre'].unique().tolist())
            usuario_filtro_hoy = st.selectbox(
                "Filtrar por Usuario", 
                usuarios_hoy,
                key="filtro_usuario_hoy"
            )
        else:
            usuario_filtro_hoy = "Todos"
        
        # Aplicar filtro
        df_hoy_filtrado = df_hoy.copy()
        
        if usuario_filtro_hoy != "Todos" and 'Nombre' in df_hoy.columns:
            df_hoy_filtrado = df_hoy_filtrado[df_hoy_filtrado['Nombre'] == usuario_filtro_hoy]
        
        st.markdown("---")
        
        # Mostrar estadísticas filtradas
        if usuario_filtro_hoy != "Todos":
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"Entregas de {usuario_filtro_hoy}", len(df_hoy_filtrado))
            with col2:
                if 'Actividad' in df_hoy_filtrado.columns:
                    st.metric("Actividades Realizadas", df_hoy_filtrado['Actividad'].nunique())
        
        # Ordenar por hora (más reciente primero)
        df_hoy_filtrado = df_hoy_filtrado.sort_values('Fecha y Hora', ascending=False)
        
        st.subheader(f"📊 Registros de Hoy: {len(df_hoy_filtrado)}")
        
        if len(df_hoy_filtrado) > 0:
            # Mostrar cada registro
            for idx, row in df_hoy_filtrado.iterrows():
                with st.expander(
                    f"🕐 {row.get('Hora', 'N/A')} - "
                    f"{row.get('Nombre', 'N/A')} - {row.get('Actividad', 'N/A')}",
                    expanded=True
                ):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("**📌 Información General**")
                        st.write(f"**Usuario:** {row.get('Nombre', 'N/A')}")
                        st.write(f"**Actividad:** {row.get('Actividad', 'N/A')}")
                        st.write(f"**Hora:** {row.get('Hora', 'N/A')}")
                    
                    with col2:
                        st.markdown("**📝 Detalles**")
                        
                        # Mostrar todos los campos relevantes
                        for column in df_hoy_filtrado.columns:
                            if column not in ['Fecha y Hora', 'Fecha', 'Hora', 'Nombre', 'Actividad']:
                                valor = row[column]
                                if pd.notna(valor) and str(valor).strip() != '':
                                    st.write(f"**{column}:** {valor}")
            
            # Opción de descarga
            st.markdown("---")
            st.subheader("📥 Descargar Datos de Hoy")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_hoy_filtrado.to_excel(writer, index=False, sheet_name='Bitácora Hoy')
            output.seek(0)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name=f"bitacora_hoy_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info(f"No hay registros para {usuario_filtro_hoy} en el día de hoy.")
    
    else:
        st.warning("⚠️ No hay registros para el día de hoy.")
        st.info("Los registros de hoy aparecerán aquí una vez que se completen entregas de turno.")

# Footer
st.markdown("---")
st.caption("Bitácora de Entregas de Turno - Aseguramiento | Gopass | Created by Angel Torres")
