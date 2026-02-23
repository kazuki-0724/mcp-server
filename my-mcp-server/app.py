import streamlit as st
from openai import OpenAI
import json
import requests

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

st.title("🤖 ツール連携 LLMチャット")

# ==========================================
# 1. ツール（関数）の定義と実体の作成
# ==========================================

# LLMに渡すツールの説明書
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_address_by_zipcode",
            "description": "日本の郵便番号から住所を検索します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "zipcode": {
                        "type": "string",
                        "description": "ハイフンなしの7桁の郵便番号（例: 3310071）"
                    }
                },
                "required": ["zipcode"]
            }
        }
    }
]

# 実際にPythonで実行される処理（ZipCloud APIを利用）
def execute_search_address(zipcode):
    url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
    response = requests.get(url)
    data = response.json()
    if data and data.get("results"):
        result = data["results"][0]
        return f"{result['address1']}{result['address2']}{result['address3']}"
    return "該当する住所が見つかりませんでした。"

# ==========================================
# 2. UIとチャットのメインロジック
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    # 内部のツール実行ログは画面のチャット欄には表示しない
    if message["role"] != "tool":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("メッセージを入力..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("考え中...")

        # 1回目のAPIリクエスト（ツールの説明書を一緒に送る）
        response = client.chat.completions.create(
            model="local-model",
            messages=st.session_state.messages,
            tools=tools, # ここでツールを渡しています
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # LLMが「ツールを使いたい」と判断した場合の処理
        if response_message.tool_calls:
            # アシスタントのツール呼び出し要求を履歴に保存
            st.session_state.messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "search_address_by_zipcode":
                    # LLMが抽出した引数（郵便番号）を取り出す
                    args = json.loads(tool_call.function.arguments)
                    zipcode = args.get("zipcode", "")
                    
                    st.toast(f"ツール実行中: 郵便番号 {zipcode} を検索しています...", icon="🔍")
                    
                    # 用意したPython関数を実行
                    address_result = execute_search_address(zipcode)
                    
                    # 実行結果（住所）を履歴に追加（role: "tool" として扱う）
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": address_result
                    })
            
            # 2回目のAPIリクエスト（ツールの結果を踏まえて、最終的な回答を作らせる）
            final_response = client.chat.completions.create(
                model="local-model",
                messages=st.session_state.messages
            )
            final_content = final_response.choices[0].message.content
            message_placeholder.markdown(final_content)
            st.session_state.messages.append({"role": "assistant", "content": final_content})
            
        else:
            # ツールを使わず普通に回答してきた場合
            message_placeholder.markdown(response_message.content)
            st.session_state.messages.append({"role": "assistant", "content": response_message.content})