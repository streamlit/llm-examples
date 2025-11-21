import base64
from pathlib import Path

import streamlit as st

from auth_encrypt import create_user, verify_user, decrypt_user_file, _USER_DATA_DIR


st.set_page_config(page_title="Login + Encrypt Demo")

st.title("🔒 Login and File Encryption Demo")

mode = st.radio("Mode", ["Login", "Create account"])

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if mode == "Create account":
    uploaded = st.file_uploader("Upload a file to encrypt for this user", type=None)
    if st.button("Create account and encrypt"):
        if not username or not password or not uploaded:
            st.error("Provide username, password and a file to encrypt")
        else:
            data = uploaded.read()
            ok, msg = create_user(username, password, data)
            if ok:
                st.success(msg)
                # offer download of encrypted file
                enc_path = _USER_DATA_DIR / f"{username}.enc"
                if enc_path.exists():
                    enc_bytes = enc_path.read_bytes()
                    st.download_button("Download encrypted file", enc_bytes, file_name=f"{username}.enc")
            else:
                st.error(msg)

else:
    if st.button("Login and decrypt user's stored file"):
        if not username or not password:
            st.error("Provide username and password")
        else:
            ok, key = verify_user(username, password)
            if not ok:
                st.error("Invalid username or password")
            else:
                ok2, pt, m = decrypt_user_file(username, key)
                if not ok2:
                    st.error(m)
                else:
                    # try to render as text if possible
                    try:
                        text = pt.decode("utf-8")
                        st.text_area("Decrypted content", value=text, height=300)
                    except Exception:
                        st.success("File decrypted — binary data")
                        st.download_button("Download decrypted file", pt, file_name=f"{username}.decrypted")
