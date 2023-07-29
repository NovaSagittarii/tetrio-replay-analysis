import streamlit as st
import json

uploaded_files = st.file_uploader("Choose a TTRM file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
  obj = json.load(uploaded_file)
  st.write(obj)