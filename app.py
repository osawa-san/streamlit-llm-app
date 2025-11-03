import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# ✅ Secrets からキーを取得
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("🔑 OpenAI APIキーが見つかりません。Secretsの設定を確認してください。")
    st.info("Streamlit Community Cloudをお使いの場合:")
    st.code("""
アプリの設定 > Secrets で以下を追加してください:

OPENAI_API_KEY = "your-api-key-here"
    """)
    st.stop()
else:
    try:
        client = OpenAI(api_key=api_key)
        st.success("✅ OpenAI APIキーが正しく読み込まれました！")
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
            error_message = str(e)
            st.error(f"❌ エラーが発生しました: {error_message}")
            
            # 具体的なエラー種別に応じたガイダンス
            if "429" in error_message or "quota" in error_message.lower():
                st.warning("🚨 **API利用制限エラー (Error 429)**")
                st.info("""
**解決方法:**
1. OpenAI Platform (https://platform.openai.com/usage) で使用量を確認
2. 請求設定 (https://platform.openai.com/account/billing) でクレジットを追加
3. 月次リセットまで待機（無料枠の場合）
4. 新しいOpenAIアカウントで別のAPIキーを取得
                """)
            elif "401" in error_message:
                st.info("🔑 APIキーが無効または期限切れです。新しいキーを生成してください。")
            else:
                st.info("🔧 一時的な問題の可能性があります。しばらく待ってから再試行してください。")