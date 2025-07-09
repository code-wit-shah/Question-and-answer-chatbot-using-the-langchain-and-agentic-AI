import streamlit as st
import requests

# Streamlit page config
st.set_page_config(page_title="Groq Q&A Chatbot", page_icon="🤖", layout="centered")

# Title and intro
st.title("🤖 Groq Q&A Chatbot")
st.markdown("Ask anything and get an intelligent answer using LLaMA3 models hosted on Groq API.")

# User input
user_input = st.text_input("💬 Enter your question:")

# Model selection dropdown
model = st.selectbox("🧠 Choose a model:", ["llama3-8b", "llama3-70b"])

# Submit button
if st.button("📝 Get Answer") and user_input.strip():
    with st.spinner("🤔 Thinking..."):
        try:
            response = requests.post(
                "http://localhost:8000/chat",  # Make sure FastAPI is running here
                json={"question": user_input, "model": model},
                timeout=20
            )

            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "")
                if answer:
                    st.success("✅ Answer:")
                    st.markdown(f"> {answer}")
                else:
                    st.warning("⚠️ No answer found in the response.")
            else:
                error_msg = response.json().get("error", "Unknown error.")
                st.error(f"❌ Backend error {response.status_code}: {error_msg}")

        except requests.exceptions.RequestException as e:
            st.error(f"🚫 Request failed: {e}")
