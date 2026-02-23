# server.py
import os
import logging
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Union
import requests
import json
from datetime import datetime

logging.getLogger("mcp").setLevel(logging.ERROR)

# MCPサーバーの初期化
mcp = FastMCP("Demo")

BASE_URL = "https://jsonplaceholder.typicode.com"

# スクリプト自身のディレクトリを取得し、各種パスを設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "report_template.html")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORT_DIR, exist_ok=True)

# ツールを定義
@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの数値を足し算します。"""
    return a + b

@mcp.tool()
async def search_address_by_zipcode(zipcode: Union[str, int]) -> str:
    """
    郵便番号から日本の住所を検索するツール
    郵便番号から住所を検索するように要求された場合にこのツールを使う

    Args:
        zipcode: 数値でも文字列でも受け付けます。
    
    Returns:
        住所情報の文字列、またはエラーメッセージ。
    """
    
    # 数値(int)で送られてきた場合に文字列(str)へ変換する
    str_zip = str(zipcode)

    # 入力値のクリーニング（ハイフン除去）
    clean_zip = str_zip.replace("-", "")

    # 7桁でない場合はAPIを叩く前に返す（バリデーション）
    if len(clean_zip) != 7 or not clean_zip.isdigit():
        return "エラー: 郵便番号は7桁の数字で指定してください。"

    url = "https://zipcloud.ibsnet.co.jp/api/search"
    params = {"zipcode": clean_zip}

    # API実行（検証環境へのリクエストを想定）
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != 200:
                return f"APIエラー: {data.get('message', '不明なエラー')}"
            
            if data["results"] is None:
                return "該当する住所が見つかりませんでした。"
            
            # 結果の整形
            result = data["results"][0]
            address = f"{result['address1']}{result['address2']}{result['address3']}"
            kana = f"{result['kana1']}{result['kana2']}{result['kana3']}"
            
            return f"【検索結果】\n住所: {address}\nフリガナ: {kana}\n都道府県コード: {result['prefcode']}"

    except Exception as e:
        return f"システムエラーが発生しました: {str(e)}"


@mcp.tool()
async def get_all_user_info() -> str:
    """
    テストデータにおける各ユーザの情報をまとめて取得するAPI
    各ユーザに関して「ユーザID」「名前」「ユーザ名」「メールアドレス」「住所」「電話番号」「webサイト」「会社情報」の情報をそれぞれ取得する。
    
    取得されるデータの例：
    {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {
            "lat": "-37.3159",
            "lng": "81.1496"
            }
        },
        "phone": "1-770-736-8031 x56442",
        "website": "hildegard.org",
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets"
        }
    }
    """
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            # 1. HTTPステータスはresponseオブジェクトから確認する
            if response.status_code != 200:
                return f"APIエラー: ステータスコード {response.status_code}"
            
            # 2. JSON配列（リスト）として受け取る
            data = response.json()
            
            # 空のリストが返ってきた場合のチェック
            if not data:
                return "レスポンスが空でした"
            
            # 3. リストを整形されたJSON文字列に変換して返す
            return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"システムエラーが発生しました: {str(e)}"
    


@mcp.tool()
async def get_all_posts_by_id(userId: str) -> str:
    """
    テストデータにおけるユーザのpostをユーザIDを指定して取得するAPI
    
    取得されるデータの例：
    {
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
    }
    """
    url = "https://jsonplaceholder.typicode.com/posts"
    params = {"userId": userId}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params = params)
            response.raise_for_status()
            if response.status_code != 200:
                return f"APIエラー: ステータスコード {response.status_code}"
            
            data = response.json()
            
            if not data:
                return f"指定されたuserId ({userId}) の投稿は見つかりませんでした。"
            
            return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"システムエラーが発生しました: {str(e)}"


# 実行部分（uvicornは不要。mcp.run() が stdio 通信を開始します）
if __name__ == "__main__":
    # print("Starting MCP server...")
    mcp.run()