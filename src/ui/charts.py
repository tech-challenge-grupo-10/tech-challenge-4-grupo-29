import plotly.graph_objects as go

def plot_radar_chart(emotions_dict, title):
    """Gera um gráfico de radar interativo usando Plotly."""
    if not emotions_dict or "Erro" in emotions_dict:
        return go.Figure().add_annotation(text="Dados insuficientes para o gráfico", showarrow=False)
        
    categories = list(emotions_dict.keys())
    values = list(emotions_dict.values())
    
    # Fechar o polígono do radar
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(values) if max(values) > 0 else 100])),
        showlegend=False,
        title=title
    )
    return fig

def plot_gauge_chart(value, title, max_val, thresholds):
    """Gera um gráfico de velocímetro (Gauge) para sensores."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': thresholds
        }
    ))
    fig.update_layout(height=300)
    return fig
