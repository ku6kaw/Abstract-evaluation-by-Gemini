import os
import pandas as pd

fields = ["Physics", "Biochemistry_Molecular_Biology", "Chemistry", "Materials_Science", "Engineering"]
categories = ["high", "low"]


def convert_all_txt_to_csv(input_dir, output_dir, columns_to_rename, columns_to_keep):
    """
    指定されたディレクトリ内のすべての.txtファイルをCSVに変換します。
    ファイル名は `{分野名}_{high or low}1000.txt` 形式で、出力は `{分野名}_{high or low}1000.csv` 形式です。

    Args:
        input_dir (str): 入力.txtファイルが格納されているディレクトリのパス。
        output_dir (str): 出力.csvファイルを保存するディレクトリのパス。
        columns_to_rename (dict): 旧列名と新列名の対応を持つ辞書。
        columns_to_keep (list): 出力CSVに保持する列名のリスト。
    """
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)

    # .txt ファイルのリストを取得
    txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]

    for txt_file in txt_files:
        # 入力ファイルと出力ファイルのパスを設定
        file_name = os.path.splitext(txt_file)[0]  # 拡張子を除いたファイル名
        input_file = os.path.join(input_dir, txt_file)
        output_file = os.path.join(output_dir, f"{file_name}.csv")

        # タブ区切りの.txtファイルを読み込み
        try:
            df = pd.read_csv(input_file, sep="\t", encoding="utf-8")
        except Exception as e:
            print(f"データの読み込み中にエラーが発生しました: {e}")
            continue

        # 列名の変更
        try:
            df = df.rename(columns=columns_to_rename)
        except Exception as e:
            print(f"列名の変更中にエラーが発生しました: {e}")
            continue

        # 指定した列のみ保持
        try:
            df = df[columns_to_keep]
        except KeyError as e:
            print(f"指定した列が存在しません: {e}")
            continue

        # CSVファイルとして保存
        try:
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
        except Exception as e:
            print(f"CSVファイルの保存中にエラーが発生しました: {e}")

    print("全ての処理が完了しました。")


def split_csv_files(input_dir, output_base_dir, rows_per_file=100):
    """
    指定されたディレクトリ内のすべてのCSVファイルを分割して保存します。
    分割後のファイルは、元のファイル名に番号を付けて保存します。

    Args:
        input_dir (str): 分割対象のCSVファイルが格納されているディレクトリ。
        output_base_dir (str): 分割後のファイルを保存する基準ディレクトリ。
        rows_per_file (int): 1ファイルあたりの行数（デフォルト: 100）。
    """
    # 入力ディレクトリ内のすべてのCSVファイルを取得
    csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]

    for csv_file in csv_files:
        input_file = os.path.join(input_dir, csv_file)

        # ファイル名から分野名とカテゴリを取得
        file_base_name = os.path.splitext(csv_file)[0]
        field_name, category = file_base_name.split("_")[:2]  # 例: "Physics_high1000" から "Physics" と "high" を取得

        # 出力先ディレクトリを作成
        output_dir = os.path.join(output_base_dir, field_name)
        os.makedirs(output_dir, exist_ok=True)

        try:
            # CSVファイルを読み込む
            df = pd.read_csv(input_file, encoding="utf-8")
            print(f"CSVファイル {input_file} の読み込みに成功しました。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            continue

        # 分割して保存
        num_chunks = (len(df) + rows_per_file - 1) // rows_per_file  # 必要なファイル数を計算
        for i in range(num_chunks):
            start_idx = i * rows_per_file
            end_idx = start_idx + rows_per_file
            chunk_df = df.iloc[start_idx:end_idx]

            # 分割後のファイル名を作成
            output_file = os.path.join(output_dir, f"{file_base_name}_{i+1}.csv")

            try:
                chunk_df.to_csv(output_file, index=False, encoding="utf-8")
                print(f"ファイル {output_file} を保存しました。")
            except Exception as e:
                print(f"ファイル {output_file} の保存中にエラーが発生しました: {e}")

        print(f"{num_chunks} 個のファイルに分割されました: {csv_file}")

    print("全てのCSVファイルの分割処理が完了しました。")


def combine_csv_files(input_dir, output_dir, fields=fields, categories=categories):
    """
    指定された分野とカテゴリに基づいてCSVファイルを結合し、結果を保存します。

    Args:
        fields (list): 結合する分野名のリスト。
        categories (list): 結合するカテゴリ名（high/low）のリスト。
        input_dir (str): 入力ファイルが格納されているベースディレクトリのパス。
        output_dir (str): 結合結果を保存するベースディレクトリのパス。
    """
    for field in fields:
        for category in categories:
            # 結合対象のファイルリストを生成
            input_files = [
                os.path.join(input_dir, f"{field}/{field}_{category}1000_{i}.csv") 
                for i in range(1, 11)
            ]

            # データフレームリストの作成
            dataframes = []
            for file in input_files:
                if os.path.exists(file):
                    try:
                        df = pd.read_csv(file, encoding="utf-8")
                        dataframes.append(df)
                        print(f"ファイル {file} を読み込みました。")
                    except Exception as e:
                        print(f"ファイル {file} の読み込み中にエラーが発生しました: {e}")
                else:
                    print(f"ファイル {file} が存在しません。")

            # データを結合
            if dataframes:
                combined_df = pd.concat(dataframes, ignore_index=True)

                # IDを再生成
                combined_df["ID"] = range(1, len(combined_df) + 1)

                # 出力ファイル名を生成
                output_file = os.path.join(output_dir, f"{field}_{category}1000.csv")

                # 結合データを保存
                try:
                    os.makedirs(output_dir, exist_ok=True)  # 出力ディレクトリを作成
                    combined_df.to_csv(output_file, index=False, encoding="utf-8")
                    print(f"ファイル {output_file} を保存しました。")
                except Exception as e:
                    print(f"ファイル {output_file} の保存中にエラーが発生しました: {e}")
            else:
                print(f"{field} の {category} データに結合可能なファイルがありませんでした。")

    print("全ての結合処理が完了しました。")
