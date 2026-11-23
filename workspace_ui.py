"""Shared owner workspace components and chart presentation."""
from html import escape
from pathlib import Path
import streamlit as st

RED = '#9D3439'
BLUE = '#526D9A'
GREEN = '#39816C'
MUTED = '#8993A4'

def workspace_header(title, description, section='WORKSPACE'):
    st.markdown('<span class="workspace-marker"></span>', unsafe_allow_html=True)
    st.caption(f'HOTVILE / {section}')
    st.title(title)
    st.markdown(f'<p class="workspace-description">{escape(description)}</p>', unsafe_allow_html=True)
    apply_workspace()

def apply_workspace():
    css=Path(__file__).with_name('workspace.css').read_text(encoding='utf-8')
    st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)

def chart_style(fig, title=None, currency=False, height=330):
    fig.update_layout(template='plotly_white', height=height,
        paper_bgcolor='white',plot_bgcolor='white',
        font=dict(family='Arial, sans-serif',size=12,color='#566174'),
        title=dict(text=title or '',font=dict(size=14,color='#202B3D'),x=0),
        margin=dict(l=65,r=25,t=40 if title else 20,b=65),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,x=0,title_text=''),
        hoverlabel=dict(bgcolor='white',font_color='#202B3D'))
    fig.update_xaxes(automargin=True,showline=False,zeroline=False,gridcolor='#EEF1F5',title_standoff=15)
    fig.update_yaxes(automargin=True,showline=False,zeroline=False,gridcolor='#EEF1F5',title_standoff=15)
    if currency: fig.update_yaxes(tickprefix='$',tickformat=',.0f',rangemode='tozero')
    return fig

def show_chart(fig, key):
    st.plotly_chart(fig,width='stretch',key=key,config={'displayModeBar':False,'responsive':True})
