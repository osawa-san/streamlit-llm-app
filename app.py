import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI client
# Try Streamlit secrets first, then environment variables
api_key = None
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.sidebar.success("✅ APIキーをSecretsから読み込みました")
except Exception as e:
    st.sidebar.warning(f"⚠️ Secretsからの読み込み失敗: {str(e)}")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.sidebar.info("✅ APIキーを環境変数から読み込みました")
    else:
        st.sidebar.error("❌ APIキーが見つかりません")

if not api_key:
    st.error("🔑 OpenAI APIキーが設定されていません")
    st.info("Streamlit Community Cloudをお使いの場合:")
    st.code("""
アプリの設定 > Secrets で以下を追加してください:

OPENAI_API_KEY = "your-api-key-here"
    """)
    st.stop()

try:
    client = OpenAI(api_key=api_key)
    st.sidebar.success("✅ OpenAIクライアント初期化完了")
except Exception as e:
    st.error(f"❌ OpenAIクライアント初期化エラー: {str(e)}")
    st.stop()

st.title("🤖 Streamlit LLM App")
st.write("OpenAI APIを使ったチャットアプリケーション")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("何か質問してください..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            assistant_response = response.choices[0].message.content
            st.markdown(assistant_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.error("OpenAI APIキーが正しく設定されているか確認してください。")