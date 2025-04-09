from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64

app = Flask(__name__)
# CORS設定を環境変数から取得
CORS_ORIGIN = os.environ.get('CORS_ORIGIN', '*')
CORS(app, resources={r"/*": {"origins": CORS_ORIGIN}})

# ロギングレベルを環境変数から取得
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, LOG_LEVEL))

# Google Sheets API設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1Uyj3dCa06lFODVd9pcr5g8BH7KJs3MA0CAebae2L7og')

def format_sheet_date(date):
    # 日付の区切り文字を/から-に変更
    return date.replace('/', '-')

def get_google_sheets_service():
    try:
        # 環境変数から認証情報を取得
        credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not credentials_json:
            raise ValueError("環境変数 GOOGLE_CREDENTIALS が設定されていません")
        
        # Base64デコード
        credentials_info = json.loads(base64.b64decode(credentials_json))
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        logging.error(f"Error creating Google Sheets service: {str(e)}")
        return None

def ensure_sheets_exist(service):
    try:
        # スプレッドシートの情報を取得
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        existing_sheets = {
            sheet['properties']['title']: sheet['properties']['sheetId'] 
            for sheet in sheet_metadata.get('sheets', [])
        }
        
        # 必要なシートのリスト（ハイフン形式）
        required_sheets = [
            '4-9',
            '4-11',
            '4-15(ローストビーフ)',
            '4-16',
            '4-17(シュラスコ)',
            '4-18',
            '4-19',
            '4-22(寿司)',
            '4-23',
            '4-25'
        ]
        
        # 作成が必要なシートを特定
        sheets_to_create = [sheet for sheet in required_sheets if sheet not in existing_sheets]
        
        if sheets_to_create:
            requests = []
            for sheet_title in sheets_to_create:
                # シート作成リクエストを追加
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_title,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 2
                            }
                        }
                    }
                })
            
            # まずシートを作成
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()
            
            # 更新後のスプレッドシート情報を再取得
            sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
            all_sheets = {
                sheet['properties']['title']: sheet['properties']['sheetId'] 
                for sheet in sheet_metadata.get('sheets', [])
            }
            
            # ヘッダーを設定するリクエストを作成
            header_requests = []
            for sheet_title in sheets_to_create:
                if sheet_title in all_sheets:
                    header_requests.append({
                        'updateCells': {
                            'rows': [{
                                'values': [
                                    {'userEnteredValue': {'stringValue': '新入生氏名'}},
                                    {'userEnteredValue': {'stringValue': '（連絡担当者）'}}
                                ]
                            }],
                            'fields': 'userEnteredValue',
                            'range': {
                                'sheetId': all_sheets[sheet_title],
                                'startRowIndex': 0,
                                'endRowIndex': 1,
                                'startColumnIndex': 0,
                                'endColumnIndex': 2
                            }
                        }
                    })
            
            # ヘッダーを設定
            if header_requests:
                body = {'requests': header_requests}
                service.spreadsheets().batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body=body
                ).execute()
            
            logging.info(f"Created sheets: {sheets_to_create}")
            
    except Exception as e:
        logging.error(f"Error ensuring sheets exist: {str(e)}")
        raise e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dates', methods=['GET'])
def get_dates():
    dates = [
        '4-9',
        '4-11',
        '4-15(ローストビーフ)',
        '4-16',
        '4-17(シュラスコ)',
        '4-18',
        '4-19',
        '4-22(寿司)',
        '4-23',
        '4-25'
    ]
    return jsonify(dates)

@app.route('/api/participants', methods=['POST'])
def add_participant():
    try:
        participant_data = request.json
        
        if not all(key in participant_data for key in ['date', 'name', 'contact']):
            return jsonify({"error": "必須項目が不足しています"}), 400
        
        service = get_google_sheets_service()
        if not service:
            return jsonify({"error": "Google Sheets APIの接続に失敗しました"}), 500

        # 必要なシートが存在することを確認
        ensure_sheets_exist(service)

        # スプレッドシートに書き込むデータを準備
        date = format_sheet_date(participant_data['date'])
        name = participant_data['name']
        contact = f"（{participant_data['contact']}）"  # 連絡担当者名を括弧で囲む
        
        # データを追加
        range_name = f"'{date}'!A:B"
        values = [[name, contact]]
        
        body = {
            'values': values
        }
        
        # 最終行に追加
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return jsonify({"success": True})
    
    except Exception as e:
        logging.error(f"Error adding participant: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)