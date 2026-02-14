import streamlit as st
import streamlit.components.v1 as components

def open_whatsapp_popup(url):
    """
    Injects JavaScript to open a URL in a popup window.
    """
    js = f"""
    <script>
        window.open("{url}", "_blank", "width=600,height=700");
    </script>
    """
    components.html(js, height=0, width=0)
