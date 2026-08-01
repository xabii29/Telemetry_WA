import pandas as pd
import plotly.graph_objects as go

FILE_PATH = "pruebas_pista_2.csv"

def graficar_pista_directa(ruta_csv):
    """
    Grafica la pista en Plotly manteniendo el orden cronológico estricto
    de la telemetría para evitar el efecto telaraña.
    """
    df = pd.read_csv(ruta_csv)
    
    # Ordenar estrictamente por la distancia recorrida para mantener la secuencia de la pista
    df = df.sort_values(by='DistanceTraveled')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['PositionX'],
        y=df['PositionZ'],
        mode='lines',  # Cambiado a solo 'lines' para que Le Mans se vea limpio y continuo
        line=dict(color='#00ffcc', width=2), # Color estilo telemetría brillante
        text=[f"Distancia: {d:.1f} m" for d in df['DistanceTraveled']],
        hoverinfo='x+y+text',
        name='Le Mans (Mulsanne)'
    ))

    fig.update_layout(
        title="Mapa Real de Le Mans - Ingeniería Inversa Forza",
        xaxis=dict(title="Coordenada X", gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title="Coordenada Y", gridcolor='rgba(255,255,255,0.1)',scaleanchor="x"),
        plot_bgcolor='rgb(20, 20, 20)',
        paper_bgcolor='rgb(10, 10, 10)',
        font=dict(color='white')
    )
    fig.show()


# Bloque ejecutor
if __name__ == "__main__":
    # Cambia "pruebas_pista.csv" por el nombre de tu archivo de corrida
    try:
        graficar_pista_directa(FILE_PATH)
    except FileNotFoundError:
        print("❌ Error: Primero debes correr el receptor UDP para generar el archivo 'pruebas_pista.csv'.")
