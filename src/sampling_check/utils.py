import os
import pandas as pd

data_path = "../../data/csv/all"
fields = ["BioChemistry_Molecular_Biology", "Chemistry", "Engineering", "Materials_Science", "Physics"]
citations = ["high", "low"]


def process_csv_files(output_file, data_path=data_path, fields=fields, citations=citations):
    """
    指定されたフォルダ内のCSVファイルを処理し、指定条件に基づいてデータを抽出・保存します。

    Args:
        data_path (str): CSVファイルが格納されているフォルダのパス。
        fields (list): フィールド名のリスト。
        citations (list): 引用分類のリスト。
        output_file (str): 保存先のCSVファイルパス。
    """
    # 最終的に格納するデータフレーム
    final_df = pd.DataFrame(columns=["Field", "Citation", "ID", "Title", "Abstract"])

    # 各フィールドと分類に対応するファイルを処理
    for field in fields:
        for citation in citations:
            file_name = f"{field}_{citation}1000.csv"
            file_path = os.path.join(data_path, file_name)

            if os.path.exists(file_path):
                # CSVを読み込み
                df = pd.read_csv(file_path, encoding="utf-8")

                # アブストラクトが欠損していない行を選択
                valid_rows = df.dropna(subset=["Abstract"])

                # 先頭10件を取得
                selected_rows = valid_rows.head(10)

                # データフレームに格納するためのリストを作成
                for idx, row in selected_rows.iterrows():
                    final_df = pd.concat([
                        final_df,
                        pd.DataFrame({
                            "Field": [field],
                            "Citation": [citation],
                            "ID": [idx + 1],
                            "Title": [row["Title"]],
                            "Abstract": [row["Abstract"]],
                        })
                    ], ignore_index=True)

    # DataFrameをCSVファイルとして保存
    final_df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"データが {output_file} に保存されました。")

def load_file_content(file_path):
    """
    テキストファイルの内容を読み込む関数。
    
    Args:
        file_path (str): テキストファイルのパス。
        
    Returns:
        str: ファイルの内容。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} が見つかりません。")
    
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


