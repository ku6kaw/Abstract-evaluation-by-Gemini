import os

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