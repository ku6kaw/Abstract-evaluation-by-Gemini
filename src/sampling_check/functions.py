import os
import time
import pandas as pd
from tqdm import tqdm


def create_user_message(abstract, rules):
    return f"""
    Abstract: {abstract}
    
    {rules}
    """


def generate_response(model, abstract, rules):
    response = model.generate_content(create_user_message(abstract, rules))
    return response


def parse_response(response):
    if pd.isna(response):
        return {}
    try:
        # JSON形式をデコード
        parsed = json.loads(response)
        if isinstance(parsed, list):  # リストの場合
            if isinstance(parsed[0], dict) and "rules" in parsed[0]:
                rules = parsed[0]["rules"]
            else:
                rules = []
        elif isinstance(parsed, dict):  # 辞書の場合
            if "results" in parsed:  # "results"キーがある場合
                rules = parsed["results"][0].get("rules", [])
            else:  # "rules"キーが直接ある場合
                rules = parsed.get("rules", [])
        else:
            rules = []
        # ルールを辞書形式で返す
        return {f"rule{i+1}": rule for i, rule in enumerate(rules)}
    except json.JSONDecodeError:
        return {}


def load_csv_with_id(file_path):
    """
    CSVファイルを読み込み、IDカラムを追加して再配置します。

    Args:
        file_path (str): CSVファイルのパス。

    Returns:
        pd.DataFrame: 再配置後のデータフレーム。
    """
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        print("データの読み込みに成功しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

    # IDカラムを追加
    df["ID"] = df.index + 1
    cols = ["Field", "Citation", "ID", "Title", "Abstract"]
    return df[cols]


def process_abstracts(df, model, rules):
    """
    データフレームからアブストラクトを抽出し、モデルを使用してレスポンスを生成します。

    Args:
        df (pd.DataFrame): 入力データフレーム。
        model: モデルオブジェクト。
        rules (str): ルール定義テキスト。

    Returns:
        pd.DataFrame: 生成されたレスポンスを含むデータフレーム。
    """
    # アブストラクトを辞書形式リストに変換
    abstracts = [
        {"abstract_id": row["ID"], "content": row["Abstract"]}
        for _, row in df.dropna(subset=["Abstract"]).iterrows()
    ]

    raw_responses = []
    for i in tqdm(range(len(abstracts))):
        abstract = abstracts[i]
        response = generate_response(model, abstract["content"], rules)
        raw_responses.append({
            "abstract_id": abstract["abstract_id"],
            "response": response.text
        })
        time.sleep(3)  # インターバルを挿入

    return pd.DataFrame(raw_responses)


def merge_and_save_results(df, results_df, output_file):
    """
    レスポンスを元のデータフレームとマージし、結果を保存します。

    Args:
        df (pd.DataFrame): 元のデータフレーム。
        results_df (pd.DataFrame): レスポンスデータフレーム。
        output_file (str): 保存先のCSVファイルパス。
    """
    # レスポンスをパースして新しいカラムを作成
    rules_df = results_df["response"].apply(parse_response).apply(pd.Series)

    # 元のデータフレームに結合
    results_df = pd.concat([results_df, rules_df], axis=1).drop(columns=["response"])
    merged_df = df.merge(results_df, left_on="ID", right_on="abstract_id", how="left").drop(columns=["abstract_id"])

    # 結果を保存
    merged_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"結果を保存しました: {output_file}")

# 関数をまとめて実行するエントリーポイント
def create_test_data(file_path, model, rules, output_file):
    """
    CSVデータの読み込みから処理、結果保存までを一括で実行する関数。

    Args:
        file_path (str): 入力CSVファイルのパス。
        model: モデルオブジェクト。
        rules (str): ルール定義テキスト。
        output_file (str): 結果保存先のCSVファイルパス。
    """
    df = load_csv_with_id(file_path)
    if df is None:
        return

    results_df = process_abstracts(df, model, rules)
    merge_and_save_results(df, results_df, output_file)
    print("処理が完了しました。")
