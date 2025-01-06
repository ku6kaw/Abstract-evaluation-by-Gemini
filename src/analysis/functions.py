import pandas as pd

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
