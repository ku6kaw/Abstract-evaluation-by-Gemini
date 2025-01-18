import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.proportion import proportions_ztest

# 日本語フォント設定（例: Hiragino Sans）
import matplotlib.font_manager as fm
plt.rcParams['font.family'] = 'Hiragino Sans'

def process_csv_with_dependencies(input_path, output_path):
    """
    指定されたCSVファイルを読み込み、依存関係に基づいて値を変更し、結果を保存します。
    Args:
        input_path (str): 入力CSVファイルのパス。
        output_path (str): 更新されたCSVファイルを保存するパス。
    """
    
    # noのときに依存するルール
    no_dependencies = {
        'rule1': ['rule2', 'rule3', 'rule4'],
        'rule5': ['rule6', 'rule7', 'rule8', 'rule9', 'rule10'],
        'rule11': ['rule12'],
        'rule13': ['rule15'],
        'rule17': ['rule18', 'rule19', 'rule20', 'rule21', 'rule22', 'rule23', 'rule24', 'rule27'],
        'rule25': ['rule26', 'rule28'],
    }
    
    # yesのときに依存するルール
    yes_dependencies = {
        'rule6': ['rule7'],  # 特別: rule6がyesの場合、rule7もyesにする
    }
    
    # CSVファイルの読み込み
    df = pd.read_csv(input_path)
    
    # noの依存関係に基づいて値を変更
    for key_rule, dependent_rules in no_dependencies.items():
        for dependent_rule in dependent_rules:
            # key_ruleが"no"の場合、dependent_rulesをすべて"no"に変更
            df.loc[df[key_rule] == 'no', dependent_rule] = 'no'
    
    # yesの依存関係に基づいて値を変更
    for key_rule, dependent_rules in yes_dependencies.items():
        for dependent_rule in dependent_rules:
            # key_ruleが"yes"の場合、dependent_rulesをすべて"yes"に変更
            df.loc[df[key_rule] == 'yes', dependent_rule] = 'yes'
    
    # 書き換えた結果を保存
    df.to_csv(output_path, index=False)

def load_data(data_dir):
    high_group = {}
    low_group = {}
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir, filename)
            field = filename.split("_high")[0] if "_high" in filename else filename.split("_low")[0]
            df = pd.read_csv(file_path)
            if "_high" in filename:
                high_group[field] = df
            elif "_low" in filename:
                low_group[field] = df
    return high_group, low_group

def preprocess_data(df):
    return df.dropna(subset=['Abstract'])

def calculate_ztest(high_df, low_df, rules):
    results = []
    for rule in rules:
        high_yes = (high_df[rule] == 'yes').sum()
        low_yes = (low_df[rule] == 'yes').sum()
        high_total = len(high_df)
        low_total = len(low_df)
        count = [high_yes, low_yes]
        nobs = [high_total, low_total]
        stat, p_value = proportions_ztest(count, nobs, alternative='two-sided')
        results.append({'Rule': rule, 'Z-statistic': stat, 'P-value': p_value})
    return pd.DataFrame(results)

def save_results(data, output_dir, filename):
    """
    数値データをCSVとして保存します。
    Args:
        data (DataFrame): 保存するデータ。
        output_dir (str): 保存先ディレクトリ。
        filename (str): 保存するファイル名。
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    data.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f'データを保存しました: {file_path}')

def visualize_results(results_df, graph_dir, data_dir, field, y_axis_limit):
    """
    グラフと数値データを保存します。
    Args:
        results_df (DataFrame): 結果データフレーム。
        graph_dir (str): グラフ保存先ディレクトリ。
        data_dir (str): データ保存先ディレクトリ。
        field (str): 分野名。
    """
    # データを保存
    save_results(results_df, data_dir, f"{field}_results.csv")

    # グラフを保存
    os.makedirs(graph_dir, exist_ok=True)
    x_positions = range(len(results_df))
    plt.figure(figsize=(12, 6))
    plt.bar(x_positions, results_df['Z-statistic'], color='skyblue', edgecolor='black')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
    plt.axhline(y=3.29, color='red', linestyle='--', label='0.001 有意水準 (+3.29)')
    plt.axhline(y=-3.29, color='red', linestyle='--', label='0.001 有意水準 (-3.29)')
    
    # 縦軸の範囲を固定
    plt.ylim(-y_axis_limit, y_axis_limit)
    
    plt.title(f'{field}のZ値分布', fontsize=16)
    plt.xlabel('評価指標', fontsize=14)
    plt.ylabel('Z値', fontsize=14)
    plt.xticks(ticks=x_positions, labels=results_df['Rule'], fontsize=16)
    plt.legend(fontsize=12)
    plt.tight_layout()

    output_file = os.path.join(graph_dir, f'{field}_ztest_visualization.png')
    plt.savefig(output_file)
    print(f'グラフを保存しました: {output_file}')
    plt.show()

def calculate_yes_ratios(df, rules):
    """
    指標ごとのyesの比率を計算します。
    Args:
        df (DataFrame): データフレーム。
        rules (list): 指標のリスト。
    Returns:
        DataFrame: 指標ごとのyes比率を含むデータフレーム。
    """
    ratios = {}
    for rule in rules:
        yes_ratio = (df[rule] == 'yes').mean()
        ratios[rule] = yes_ratio
    return pd.DataFrame(list(ratios.items()), columns=['Rule', 'Yes Ratio'])

def save_yes_ratio_graph(high_ratios, low_ratios, output_dir, title):
    """
    Yes比率のグラフを保存する関数
    Args:
        high_ratios (DataFrame): Highグループの指標ごとのYes比率。
        low_ratios (DataFrame): Lowグループの指標ごとのYes比率。
        output_dir (str): グラフの保存先ディレクトリ。
        title (str): グラフのタイトル（保存時のファイル名にも使用）。
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Rule列が文字列型の場合のみ変換を実施
    if high_ratios['Rule'].dtype == 'object':
        high_ratios['Rule'] = high_ratios['Rule'].str.replace('rule', '').astype(int)
    if low_ratios['Rule'].dtype == 'object':
        low_ratios['Rule'] = low_ratios['Rule'].str.replace('rule', '').astype(int)
    
    # グラフの作成
    plt.figure(figsize=(12, 6))
    x = high_ratios['Rule']  # 数値型に変換済みのRule列
    plt.bar(x - 0.2, high_ratios['Yes Ratio'], width=0.4, label='Highグループ', color='skyblue', align='center')
    plt.bar(x + 0.2, low_ratios['Yes Ratio'], width=0.4, label='Lowグループ', color='salmon', align='center')
    plt.xlabel('指標', fontsize=14)
    plt.ylabel('Yesの比率', fontsize=14)
    plt.title(title, fontsize=16)
    plt.legend(fontsize=12)
    plt.xticks(rotation=90)
    plt.tight_layout()
    
    # グラフの保存
    graph_path = os.path.join(output_dir, f"{title}_yes_ratio.png")
    plt.savefig(graph_path)
    print(f"Yes比率のグラフを保存しました: {graph_path}")
    plt.close()
