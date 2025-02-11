import streamlit as st
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
API_KEY = your_open_exchange_rates_api_key  # Clave API
BASE_URL = "https://openexchangerates.org/api/latest.json"

# Configuración inicial de la página
st.set_page_config(layout="wide", page_title="Price Simulator")

# Función para obtener la tasa de cambio desde el API
def obtener_tasa_cambio():
    try:
        response = requests.get(BASE_URL, params={"app_id": API_KEY, "base": "USD"})
        data = response.json()
        return data['rates']['VES']
    except Exception as e:
        st.error("Error when obtaining te exchange rate. Verify your conexion or API.")
        return None

# Función para calcular precios ajustados
def calcular_precio(costo_usd, tasa_cambio, margen):
    costo_bs = costo_usd * tasa_cambio
    precio_venta_bs = costo_bs / (1 - margen)
    precio_venta_usd = precio_venta_bs / tasa_cambio
    return costo_bs, precio_venta_bs, precio_venta_usd

# Función para formatear números en estilo español
def format_currency(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def show():
    # Obtener tasa de cambio diaria
    tasa_diaria = obtener_tasa_cambio()
    
    # Interfaz en Streamlit
    st.title("FX Impact Simulator: Costs & Pricing")

    st.markdown("""
Understand how exchange rate fluctuations impact costs and pricing. This tool allows you to compare costs and selling prices under different exchange rate scenarios, offering valuable insights for pricing strategy adjustments. Built specifically for a family business in Venezuela, where FX volatility is a daily challenge, it integrates an Exchange Rate API to provide real-time daily rates for accurate calculations.
""")
    
    # Botón para regresar al Menú Principal
    #if st.button("Regresar"):
     #   st.session_state.current_page = None

    # Mostrar la tasa diaria en un contenedor visible
    if tasa_diaria:
        st.sidebar.markdown(
            f"<div style='position: fixed; top: 10px; right: 10px; background-color: #f0f0f0; padding: 10px; border-radius: 8px;'>"
            f"<strong>Daily Actual Exchage Rate (USD a Bs):</strong><br><span style='color: green;'>{tasa_diaria:.2f}</span> Bs</div>",
            unsafe_allow_html=True
        )

    # Entradas del usuario
    st.sidebar.header("Input Parameters")
    costo_usd = st.sidebar.number_input("Cost per Galon (USD):", value=12.00)
    tasa_cambio_actual = st.sidebar.number_input("Actual Exchange Rate (Bs/USD):", value=tasa_diaria if tasa_diaria else 30.0)
    tasa_cambio_nueva = st.sidebar.number_input("New Exchange Rate (Bs/USD):", value=tasa_cambio_actual + 5)
    margen = st.sidebar.slider("Target Margin (%):", 0, 50, 30) / 100

    # Cálculo de costos y precios
    costo_bs_actual, precio_venta_bs_actual, precio_venta_usd_actual = calcular_precio(costo_usd, tasa_cambio_actual, margen)
    costo_bs_nuevo, precio_venta_bs_nuevo, precio_venta_usd_nuevo = calcular_precio(costo_usd, tasa_cambio_nueva, margen)

    # Resultados
    st.subheader("Results")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write(f"**Actual Cost p/g:** {format_currency(costo_bs_actual)} Bs ({format_currency(costo_usd)} USD)")
    with col2:
        st.write(f"**Actual Price p/g:** {format_currency(precio_venta_bs_actual)} Bs ({format_currency(precio_venta_usd_actual)} USD)")
    with col3:
        st.write(f"**New Cost p/g:** {format_currency(costo_bs_nuevo)} Bs ({format_currency(costo_usd)} USD)")
    with col4:
        st.write(f"**New Price p/g:** {format_currency(precio_venta_bs_nuevo)} Bs ({format_currency(precio_venta_usd_nuevo)} USD)")

    # Comparación gráfica
    fig = go.Figure()

    # Barra de costos
    fig.add_trace(go.Bar(
        x=["Actual", "New"],
        y=[costo_bs_actual, costo_bs_nuevo],
        name="Cost (Bs)",
        marker_color="#216AE8",
        hovertemplate="Cost: %{y:,.2f} Bs<extra></extra>"
    ))

    # Barra de precios de venta
    fig.add_trace(go.Bar(
        x=["Actual", "New"],
        y=[precio_venta_bs_actual, precio_venta_bs_nuevo],
        name="Sales Price (Bs)",
        marker_color="#F0FDA8",
        hovertemplate="Price: %{y:,.2f} Bs<extra></extra>"
    ))

    # Configuración del diseño del gráfico
    fig.update_layout(
        barmode="group",
        title="Cost and Price Comparation",
        xaxis_title="State",
        yaxis_title="Amounts (Bs)",
        height=400,
        legend_title="Categories",
        template="simple_white"
    )

    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=True)

    st.sidebar.markdown("""
<div class="instrucciones-box">
<h3>💡 How to Use This Tool</h3>
<ol>
    <li>📊 Adjust input parameters such as cost per gallon, exchange rate, and target margin.</li>
    <li>🔄 Compare how changes in the exchange rate affect costs and pricing.</li>
    <li>📉 Visualize the impact with clear bar charts.</li>
    <li>💡 Use the insights to make data-driven pricing decisions.</li>
</ol>
</div>
<style>
    .instrucciones-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        font-size: 14px;
    }
    .instrucciones-box ol, .instrucciones-box li {
        font-size: 16px;
        line-height: 1.4;
    }
    .instrucciones-box h3 {
        margin-top: 0;
        margin-bottom: 5px;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)
    st.markdown("""
---
### ⚠ Disclaimer  
This tool is provided for informational purposes only and does not constitute financial advice. While it uses real-time exchange rate data, users should verify all calculations before making financial decisions.  

© 2024 **Patricia Barrios**. All rights reserved.
""")


# Ejecutar la página
if __name__ == "__main__":
    show()

