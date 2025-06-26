import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Configuración
st.set_page_config(page_title="Parámetros Generales", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("SJDSFERE-2680 - Revision Parametros Generales.csv", sep=";", dtype={"VALORPORDEFECTO": str, "VALORPORCENTRO": str})
    df["FUENTE"] = df["FUENTE"].str.upper()
    return df

df = load_data()

# Dividir por sistema
df_sfere = df[df["FUENTE"] == "SFERE"]
df_ticares = df[df["FUENTE"] == "TICARES"]

codigos_sfere = set(df_sfere["CODIGOPARAMETRO"])
codigos_ticares = set(df_ticares["CODIGOPARAMETRO"])

solo_sfere = codigos_sfere - codigos_ticares
solo_ticares = codigos_ticares - codigos_sfere
ambos = codigos_sfere & codigos_ticares

conteos = {
    "Solo en TiCares": len(solo_ticares),
    "En ambos sistemas": len(ambos),
    "Solo en SFERE": len(solo_sfere)
}

# Título
st.title("⚙️ Comparativa de Parámetros Generales entre SFERE y TiCares")
st.subheader("📊 Distribución de parámetros por grupo")
# Gráfico apilado horizontal
fig = go.Figure()

fig.add_trace(go.Bar(
    y=["Parámetros"],
    x=[conteos["Solo en TiCares"]],
    name="Solo en TiCares",
    orientation='h',
    marker=dict(color="#6c757d"),
    customdata=["Solo en TiCares"],
    hovertemplate="%{customdata}<br>Cantidad: %{x}<extra></extra>",
))
fig.add_trace(go.Bar(
    y=["Parámetros"],
    x=[conteos["En ambos sistemas"]],
    name="En ambos sistemas",
    orientation='h',
    marker=dict(color="#17a2b8"),
    customdata=["En ambos sistemas"],
    hovertemplate="%{customdata}<br>Cantidad: %{x}<extra></extra>",
))
fig.add_trace(go.Bar(
    y=["Parámetros"],
    x=[conteos["Solo en SFERE"]],
    name="Solo en SFERE",
    orientation='h',
    marker=dict(color="#28a745"),
    customdata=["Solo en SFERE"],
    hovertemplate="%{customdata}<br>Cantidad: %{x}<extra></extra>",
))

fig.update_layout(
    barmode='stack',
    height=250,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        traceorder='normal', 
        orientation="h",
        yanchor="bottom",
        y=-0.65,
        xanchor="center",
        x=0.5
    ),
   xaxis=dict(
        title="Cantidad",
        showticklabels=True,
        showgrid=True,
        zeroline=False
    ),
    yaxis=dict(showticklabels=False),
)

st.plotly_chart(fig, use_container_width=True)

# Selector de grupo
grupo = st.radio("Selecciona el grupo de parámetros:", ["Solo en TiCares", "En ambos sistemas", "Solo en SFERE"], horizontal=True)

# Filtro por grupo
if grupo == "Solo en TiCares":
    df_group = df_ticares[df_ticares["CODIGOPARAMETRO"].isin(solo_ticares)]
elif grupo == "Solo en SFERE":
    df_group = df_sfere[df_sfere["CODIGOPARAMETRO"].isin(solo_sfere)]
else:
    df_group = df[df["CODIGOPARAMETRO"].isin(ambos)]

# Mostrar parámetros ordenados por código
st.markdown(f"### 📋 Parámetros disponibles `{grupo}`")
parametros_display = df_group[["CODIGOPARAMETRO", "DESCRIPCIONPARAMETRO", "VALORPORDEFECTO"]].drop_duplicates()
parametros_display = parametros_display.sort_values("CODIGOPARAMETRO")
st.dataframe(parametros_display, use_container_width=True)

# Selector de parámetro con opciones ordenadas
param_seleccionado = st.selectbox(
    "Selecciona un parámetro:",
    options=parametros_display["CODIGOPARAMETRO"].tolist(),
    format_func=lambda x: f"{x} - {parametros_display[parametros_display['CODIGOPARAMETRO'] == x]['DESCRIPCIONPARAMETRO'].values[0]}"
)

# Mostrar detalle
if param_seleccionado:
    st.markdown(f"### 🏥 Detalle por organización, centro, servicio del parámetro `{param_seleccionado}`")

    if grupo == "Solo en TiCares":
        detalle = df_ticares[df_ticares["CODIGOPARAMETRO"] == param_seleccionado]
        st.dataframe(detalle[["VALORPORCENTRO", "ORGANIZACION", "CENTRO", "SERVICIO"]], use_container_width=True)

    elif grupo == "Solo en SFERE":
        detalle = df_sfere[df_sfere["CODIGOPARAMETRO"] == param_seleccionado]
        st.dataframe(detalle[["VALORPORCENTRO", "ORGANIZACION", "CENTRO", "SERVICIO"]], use_container_width=True)

    elif grupo == "En ambos sistemas":
        df_t = df_ticares[df_ticares["CODIGOPARAMETRO"] == param_seleccionado][["VALORPORCENTRO", "ORGANIZACION", "CENTRO", "SERVICIO"]].copy()
        df_s = df_sfere[df_sfere["CODIGOPARAMETRO"] == param_seleccionado][["VALORPORCENTRO", "ORGANIZACION", "CENTRO", "SERVICIO"]].copy()

        # Rellenar NaN
        for df_tmp in [df_t, df_s]:
            for col in ["ORGANIZACION", "CENTRO", "SERVICIO"]:
                df_tmp[col] = df_tmp[col].fillna("")

        df_t["KEY"] = df_t["ORGANIZACION"] + "|" + df_t["CENTRO"] + "|" + df_t["SERVICIO"]
        df_s["KEY"] = df_s["ORGANIZACION"] + "|" + df_s["CENTRO"] + "|" + df_s["SERVICIO"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🩺 TiCares")
            st.dataframe(df_t.drop(columns=["KEY"]), use_container_width=True)

        with col2:
            st.markdown("### 🏥 SFERE")
            st.dataframe(df_s.drop(columns=["KEY"]), use_container_width=True)

        if st.button("🔍 Comparar"):
            merged = pd.merge(df_t, df_s, on="KEY", how="outer", suffixes=("_TICARES", "_SFERE"))

            def comparar(row):
                return all([
                    row.get("VALORPORCENTRO_TICARES") == row.get("VALORPORCENTRO_SFERE"),
                    row.get("ORGANIZACION_TICARES") == row.get("ORGANIZACION_SFERE"),
                    row.get("CENTRO_TICARES") == row.get("CENTRO_SFERE"),
                    row.get("SERVICIO_TICARES") == row.get("SERVICIO_SFERE"),
                ])

            merged["Coincide"] = merged.apply(comparar, axis=1)

            final = merged[[ 
                "ORGANIZACION_TICARES", "CENTRO_TICARES", "SERVICIO_TICARES", "VALORPORCENTRO_TICARES",
                "ORGANIZACION_SFERE", "CENTRO_SFERE", "SERVICIO_SFERE", "VALORPORCENTRO_SFERE",
                "Coincide"
            ]].rename(columns={
                "ORGANIZACION_TICARES": "ORGANIZACIÓN_TICARES",
                "CENTRO_TICARES": "CENTRO_TICARES",
                "SERVICIO_TICARES": "SERVICIO_TICARES",
                "VALORPORCENTRO_TICARES": "VALOR_TICARES",
                "ORGANIZACION_SFERE": "ORGANIZACIÓN_SFERE",
                "CENTRO_SFERE": "CENTRO_SFERE",
                "SERVICIO_SFERE": "SERVICIO_SFERE",
                "VALORPORCENTRO_SFERE": "VALOR_SFERE",
            })

            def color_filas(row):
                color = '#d4edda' if row["Coincide"] else '#f8d7da'
                return [f"background-color: {color}"] * len(row)

            st.markdown("### 🎨 Comparativa entre sistemas")
            st.dataframe(final.style.apply(color_filas, axis=1), use_container_width=True)


# --------- Aquí empieza la integración para exportar Excel ---------

def crear_excel_comparativa(df, df_sfere, df_ticares, solo_sfere, solo_ticares, ambos):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Hoja 1: Resumen general
        resumen_df = pd.DataFrame({
            'Grupo': ["Solo en TiCares", "En ambos sistemas", "Solo en SFERE"],
            'Cantidad': [len(solo_ticares), len(ambos), len(solo_sfere)]
        })
        resumen_df.to_excel(writer, sheet_name='Resumen general', index=False)

        # Hoja 2: Solo en TiCares (columnas básicas)
        df_ticares_solo = df_ticares[df_ticares["CODIGOPARAMETRO"].isin(solo_ticares)][
            ["CODIGOPARAMETRO", "DESCRIPCIONPARAMETRO", "VALORPORDEFECTO"]
        ].drop_duplicates()
        df_ticares_solo.to_excel(writer, sheet_name='Solo en TiCares', index=False)

        # Hoja 3: Solo en SFERE (columnas básicas)
        df_sfere_solo = df_sfere[df_sfere["CODIGOPARAMETRO"].isin(solo_sfere)][
            ["CODIGOPARAMETRO", "DESCRIPCIONPARAMETRO", "VALORPORDEFECTO"]
        ].drop_duplicates()
        df_sfere_solo.to_excel(writer, sheet_name='Solo en SFERE', index=False)

        # Hoja 4: Comparativa simple
        df_t_basico = df_ticares[df_ticares["CODIGOPARAMETRO"].isin(ambos)][
            ["CODIGOPARAMETRO", "DESCRIPCIONPARAMETRO", "VALORPORDEFECTO"]
        ].drop_duplicates()
        df_s_basico = df_sfere[df_sfere["CODIGOPARAMETRO"].isin(ambos)][
            ["CODIGOPARAMETRO", "DESCRIPCIONPARAMETRO", "VALORPORDEFECTO"]
        ].drop_duplicates()

        df_t_basico = df_t_basico.rename(columns={
            "DESCRIPCIONPARAMETRO": "DESCRIPCIONPARAMETRO_TICARES",
            "VALORPORDEFECTO": "VALORPORDEFECTO_TICARES"
        })
        df_s_basico = df_s_basico.rename(columns={
            "DESCRIPCIONPARAMETRO": "DESCRIPCIONPARAMETRO_SFERE",
            "VALORPORDEFECTO": "VALORPORDEFECTO_SFERE"
        })

        comparativa_simple = pd.merge(df_t_basico, df_s_basico, on="CODIGOPARAMETRO", how="outer")
        comparativa_simple.to_excel(writer, sheet_name='Ambos Sistemas', index=False)

        # Hoja 5: Comparativa detallada
        df_t_detalle = df_ticares[df_ticares["CODIGOPARAMETRO"].isin(ambos)].copy()
        df_s_detalle = df_sfere[df_sfere["CODIGOPARAMETRO"].isin(ambos)].copy()

        for col in ["ORGANIZACION", "CENTRO", "SERVICIO"]:
            df_t_detalle[col] = df_t_detalle[col].fillna("")
            df_s_detalle[col] = df_s_detalle[col].fillna("")

        # Renombrar columnas para merge con sufijos claros
        df_t_detalle = df_t_detalle.rename(columns={
            "CODIGOPARAMETRO": "CODIGOPARAMETRO_TICARES",
            "DESCRIPCIONPARAMETRO": "DESCRIPCIONPARAMETRO_TICARES",
            "VALORPORDEFECTO": "VALORPORDEFECTO_TICARES",
            "VALORPORCENTRO": "VALORPORCENTRO_TICARES",
            "ORGANIZACION": "ORGANIZACION_TICARES",
            "CENTRO": "CENTRO_TICARES",
            "SERVICIO": "SERVICIO_TICARES"
        })
        df_s_detalle = df_s_detalle.rename(columns={
            "CODIGOPARAMETRO": "CODIGOPARAMETRO_SFERE",
            "DESCRIPCIONPARAMETRO": "DESCRIPCIONPARAMETRO_SFERE",
            "VALORPORDEFECTO": "VALORPORDEFECTO_SFERE",
            "VALORPORCENTRO": "VALORPORCENTRO_SFERE",
            "ORGANIZACION": "ORGANIZACION_SFERE",
            "CENTRO": "CENTRO_SFERE",
            "SERVICIO": "SERVICIO_SFERE"
        })

        df_t_detalle['KEY'] = (df_t_detalle['CODIGOPARAMETRO_TICARES'] + "|" +
                               df_t_detalle['ORGANIZACION_TICARES'] + "|" +
                               df_t_detalle['CENTRO_TICARES'] + "|" +
                               df_t_detalle['SERVICIO_TICARES'])
        df_s_detalle['KEY'] = (df_s_detalle['CODIGOPARAMETRO_SFERE'] + "|" +
                               df_s_detalle['ORGANIZACION_SFERE'] + "|" +
                               df_s_detalle['CENTRO_SFERE'] + "|" +
                               df_s_detalle['SERVICIO_SFERE'])

        merged_detalle = pd.merge(df_t_detalle, df_s_detalle, on='KEY', how='outer')

        # Ahora sí, columnas esperadas
        detalle_cols = [
            'CODIGOPARAMETRO_TICARES', 'DESCRIPCIONPARAMETRO_TICARES',
            'VALORPORDEFECTO_TICARES', 'VALORPORCENTRO_TICARES', 'ORGANIZACION_TICARES', 'CENTRO_TICARES', 'SERVICIO_TICARES',
            'CODIGOPARAMETRO_SFERE', 'DESCRIPCIONPARAMETRO_SFERE',
            'VALORPORDEFECTO_SFERE', 'VALORPORCENTRO_SFERE', 'ORGANIZACION_SFERE', 'CENTRO_SFERE', 'SERVICIO_SFERE'
        ]

        # Filtramos solo columnas que existen para evitar errores (por si falta alguna)
        detalle_cols_existentes = [col for col in detalle_cols if col in merged_detalle.columns]

        merged_detalle[detalle_cols_existentes].to_excel(writer, sheet_name='Comparativa detallada', index=False)


    return output.getvalue()

# Botón para descargar Excel completo
st.markdown("---")
if st.button("📥 Descargar reporte completo en Excel"):
    with st.spinner("Generando archivo Excel..."):
        excel_bytes = crear_excel_comparativa(df, df_sfere, df_ticares, solo_sfere, solo_ticares, ambos)
        st.download_button(
            label="Descargar archivo Excel",
            data=excel_bytes,
            file_name="comparativa_parametros_generales.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
