"""Shared owner scope; the persistent value is independent of widget cleanup."""
import streamlit as st
SCOPES = ['Customer orders', 'Illustrative sample', 'Combined']


def _remember_scope():
    st.session_state['owner_data_scope'] = st.session_state['scope_control']


def owner_scope():
    current = st.session_state.get('owner_data_scope', SCOPES[1])
    scope = st.sidebar.selectbox('Data scope', SCOPES, index=SCOPES.index(current),
                                key='scope_control', on_change=_remember_scope)
    st.session_state['owner_data_scope'] = scope
    st.caption(f'Data scope: {scope}. Dashboard filters further narrow this scope; Order Matching has its own status filter.')
    if scope == 'Illustrative sample':
        st.info('Illustrative records are read-only and excluded from customer checkout. This project does not generate sample orders automatically.')
    elif scope == 'Combined':
        st.info('Combined view includes customer records and explicitly supplied illustrative records. Source labels distinguish them.')
    return scope
