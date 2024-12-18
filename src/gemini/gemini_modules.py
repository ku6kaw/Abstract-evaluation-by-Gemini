import os
import time
import json
import pandas as pd
from tqdm import tqdm

# レスポンス生成用メッセージ
def create_user_message(abstract, rules):
    return f"Abstract: {abstract}\n\n{rules}"

# Geminiモデルでレスポンス生成
def generate_response(model, abstract, rules):
    user_message = create_user_message(abstract, rules)
    response = model.generate_content(user_message)
    return response

# レスポンスのパース
def parse_response(response):
    try:
        parsed = json.loads(response)
        rules = parsed.get("results", [{}])[0].get("rules", [])
        return {f"rule{i+1}": rule for i, rule in enumerate(rules)}
    except (json.JSONDecodeError, KeyError, IndexError):
        return {}

# ファイル処理のメイン関数
def process_gemini(model, rules, base_input_path, base_output_path, selected_field, citation_type):
    """
    分野名とhigh/lowに基づきCSVファイルを処理し、結果を保存する。

    Args:
        model: Geminiモデルオブジェクト
        rules (str): ルール定義テキスト
        base_input_path (str): 入力データの基本ディレクトリ
        base_output_path (str): 出力データの基本ディレクトリ
        selected_field (str): 処理対象の分野名
        citation_type (str): "high" または "low"
    """
    # 入出力ディレクトリの設定
    input_path = os.path.join(base_input_path, selected_field)
    output_path = os.path.join(base_output_path, selected_field)
    os.makedirs(output_path, exist_ok=True)

    # 対象ファイルを取得
    csv_files = [f for f in os.listdir(input_path) if f.endswith(".csv") and citation_type in f]

    # CSVファイルの処理
    for file_name in csv_files:
        input_file = os.path.join(input_path, file_name)
        output_file = os.path.join(output_path, file_name)

        try:
            # CSV読み込み
            df = pd.read_csv(input_file, encoding="utf-8")
            print(f"データの読み込みに成功しました: {input_file}")
        except Exception as e:
            print(f"読み込みエラー: {e}")
            continue

        # IDカラム追加
        df["ID"] = df.index
        abstracts = [{"abstract_id": row["ID"], "content": row["Abstract"]} for _, row in df.dropna(subset=["Abstract"]).iterrows()]

        if not abstracts:
            print(f"アブストラクトが空のためスキップ: {file_name}")
            continue

        # Geminiモデルで処理
        raw_responses = []
        for abstract in tqdm(abstracts, desc=f"Processing {file_name}"):
            try:
                response = generate_response(model, abstract["content"], rules)
                raw_responses.append({"abstract_id": abstract["abstract_id"], "response": response.text})
                time.sleep(4)  # APIレート制限対策
            except Exception as e:
                print(f"処理エラー: {e}")

        # レスポンスをパースして保存
        try:
            results_df = pd.DataFrame(raw_responses)
            rules_df = results_df["response"].apply(parse_response).apply(pd.Series)
            results_df = pd.concat([results_df, rules_df], axis=1).drop(columns=["response"])
            merged_df = df.merge(results_df, left_on="ID", right_on="abstract_id", how="left").drop(columns=["abstract_id"])

            # 保存
            merged_df.to_csv(output_file, index=False, encoding="utf-8")
            print(f"結果を保存しました: {output_file}")
        except Exception as e:
            print(f"保存エラー: {e}")
