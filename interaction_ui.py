from pathlib import Path
import streamlit as st

def apply_interactions():
    css = Path(__file__).with_name("interaction.css").read_text(encoding="utf-8")
    css += '\n' + Path(__file__).with_name('brand.css').read_text(encoding='utf-8')
    css += '\n' + Path(__file__).with_name('hotvile.css').read_text(encoding='utf-8')
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
