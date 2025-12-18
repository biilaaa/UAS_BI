import numpy as np
import plotly.graph_objects as go
import streamlit as st


def _make_heart_path(num_points: int = 400):
    """Buat koordinat bentuk hati (heart curve) 2D."""
    t = np.linspace(0, 2 * np.pi, num_points)
    x = 16 * np.sin(t) ** 3
    y = (
        13 * np.cos(t)
        - 5 * np.cos(2 * t)
        - 2 * np.cos(3 * t)
        - np.cos(4 * t)
    )

    x = x / np.max(np.abs(x))
    y = y / np.max(np.abs(y))
    return x, y


def show_probability_animation(model, input_df):
    """
    Menampilkan:
    - Animasi heart beat (risiko)
    - Semi "liquid gauge" probabilitas risiko

    Return:
        (prob_no_risk, prob_risk)
    """
    prob = model.predict_proba(input_df)[0]
    prob_no_risk = float(prob[0])
    prob_risk = float(prob[1])

    x, y = _make_heart_path()

    frames = []
    n_frames = 20
    for i in range(n_frames):
        scale = 0.9 + 0.12 * np.sin(2 * np.pi * i / n_frames)
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=x,
                        y=y * scale,
                        fill="toself",
                        mode="lines",
                        line=dict(color="#b91c1c", width=4),
                    )
                ]
            )
        )

    heart_fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=y,
                fill="toself",
                mode="lines",
                line=dict(color="#b91c1c", width=4),
            )
        ],
        frames=frames,
    )

    heart_fig.update_layout(
        title="Heart Beat Animation (Risiko)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
        margin=dict(l=0, r=0, t=40, b=0),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.5,
                y=-0.1,
                xanchor="center",
                yanchor="top",
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 120, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    )
                ],
            )
        ],
    )

    st.plotly_chart(heart_fig, use_container_width=True)

    risk_percent = prob_risk * 100.0

    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_percent,
            number={"suffix": "%", "font": {"size": 32, "color": "#4b5563"}},
            title={
                "text": "Probabilitas Pasien Berisiko",
                "font": {"size": 16, "color": "#1e293b"},
            },
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#ef4444"},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, 40], "color": "#e0f2fe"},
                    {"range": [40, 70], "color": "#fee2e2"},
                    {"range": [70, 100], "color": "#fecaca"},
                ],
                "threshold": {
                    "line": {"color": "#dc2626", "width": 4},
                    "thickness": 0.8,
                    "value": risk_percent,
                },
            },
        )
    )

    gauge_fig.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.markdown("#### 💧 Liquid Fill Probability Gauge")
    st.plotly_chart(gauge_fig, use_container_width=True)

    return prob_no_risk, prob_risk
