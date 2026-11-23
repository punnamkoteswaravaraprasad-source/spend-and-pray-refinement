"""Shared owner workspace components and chart presentation."""
from html import escape
from pathlib import Path
import streamlit as st

RED = '#ED512E'
BLUE = '#ED512E'
GREEN = '#333333'
MUTED = '#ACA29B'

def workspace_header(title, description, section='WORKSPACE'):
    st.markdown('<span class="workspace-marker"></span>', unsafe_allow_html=True)
    st.markdown(f'<header class="analytics-header"><div class="header-kicker">{escape(section)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></header>', unsafe_allow_html=True)
    apply_workspace()

def metric_tile(column, label, value, description, key, tone='blue', icon='chart'):
    paths={'chart':'<path d="M4 18V9m7 9V4m7 14v-6M2 21h20"/>',
           'orders':'<path d="M6 3h9l4 4v14H6zM14 3v5h5M9 12h7M9 16h5"/>',
           'check':'<path d="M4 4h16v16H4zM8 12l3 3 5-6"/>',
           'alert':'<path d="M12 3L2 21h20zM12 9v5M12 17v1"/>',
           'money':'<path d="M12 2v20M18 6H9a4 4 0 000 8h6a4 4 0 000-8M6 18h9"/>'}
    with column:
        with st.container(border=True,key=f'workspace_tile_{key}'):
            st.markdown(f'<span class="tile-icon {tone}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">{paths.get(icon,paths["chart"])}</svg></span>',unsafe_allow_html=True)
            st.metric(label,value)
            st.caption(description)

def progress_panel(title, description, entries, key):
    with st.container(border=True,key=f'workspace_panel_{key}'):
        st.subheader(title)
        st.caption(description)
        parts=[]
        for label,value,display,color in entries:
            safe=max(0,min(100,float(value)))
            parts.append(f'<div class="progress-row"><div><span>{escape(label)}</span><b>{escape(display)}</b></div><div class="progress-track"><span style="width:{safe}%;background:{color}"></span></div></div>')
        st.markdown(''.join(parts),unsafe_allow_html=True)

def apply_workspace():
    css=Path(__file__).with_name('workspace.css').read_text(encoding='utf-8')
    css += '\n' + Path(__file__).with_name('brand.css').read_text(encoding='utf-8')
    st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)

def chart_style(fig, title=None, currency=False, height=330):
    fig.update_layout(template='plotly_white', height=height,
        paper_bgcolor='white',plot_bgcolor='white',
        font=dict(family='Arial, sans-serif',size=12,color='#566174'),
        title=dict(text=title or '',font=dict(size=14,color='#242424'),x=0),
        margin=dict(l=65,r=25,t=40 if title else 20,b=65),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,x=0,title_text=''),
        hoverlabel=dict(bgcolor='white',font_color='#242424'))
    fig.update_xaxes(automargin=True,showline=False,zeroline=False,gridcolor='#EEF1F5',title_standoff=15)
    fig.update_yaxes(automargin=True,showline=False,zeroline=False,gridcolor='#EEF1F5',title_standoff=15)
    if currency: fig.update_yaxes(tickprefix='$',tickformat=',.0f',rangemode='tozero')
    return fig

def show_chart(fig, key):
    st.plotly_chart(fig,width='stretch',key=key,config={'displayModeBar':False,'responsive':True})
