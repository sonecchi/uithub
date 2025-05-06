from collections import Counter
from dotenv import load_dotenv
import requests
import os # 環境変数からトークンを取得するなら使う


load_dotenv()


# --- ！！！ここを設定してくれよな！！！ ---
GITHUB_OWNER = "sonecchi"  # 君のGitHubユーザー名 or Organization名だぜ！
GITHUB_REPO = "uithub" # テキスト化したいプライベートリポジトリの名前！ google-adk
GITHUB_BRANCH = "main" # ブランチ名 (デフォルトは 'main' だが、違ったら変えてくれ！)
GITHUB_PATH = "" # 特定のファイルやディレクトリだけ欲しい場合に指定 (例: 'src/main' や 'README.md')。空ならリポジトリ全体！
GITHUB_TOKEN = os.environ.get("GITHUB_PAT") # 環境変数 GITHUB_PAT から読み込む 強力な権限は不要で、repoの読み取り権限があればOKなはずだぜ！

# uithub APIのエンドポイントだぜ！s
UITHUB_BASE_URL = "https://uithub.com"


# --- ここから下がAPIのオプションだぜ！ ---
# デフォルト値でいいなら、この辞書は空っぽ {} でもOK！
# 必要に応じてコメントアウトを外したり、値を変えたりしてくれよな！🔧
api_options = {
    # --- レスポンス形式 ---
    'accept': 'text/markdown', # 返ってくる形式を指定。デフォルトは 'text/markdown'。
                                # 他に 'application/json', 'text/yaml', 'text/html' が選べるぜ！JSONとかはデータとして扱いたい時に便利だな！🤖


    # --- フィルタリング系 ---
    # 'ext': 'py,js,md',        # この拡張子のファイルだけ含めるぜ！(カンマ区切り) 例: 'py,md'
    'exclude-ext': 'svg,gitignore,sql,png,json,css,pyc,md', # この拡張子のファイルは除外するぜ！(カンマ区切り) 例: 'lock,log'
    # 'dir': '',        # このディレクトリだけ含めるぜ！(カンマ区切り) 例: 'src/app' ※現在機能しないみたい
    'exclude-dir': 'node_modules,*sample*,*sample,sample,./sample,./sample/,/sample,sample/,/sample/,sample*', # このディレクトリは除外するぜ！(カンマ区切り) node_modules とかデカいのは除外しとくと吉！👍 ※現在機能しないみたい
    # 'maxFileSize': 100000,    # ファイルサイズがこれ(バイト単位)より大きいファイルは含めないぜ！デカすぎるファイルはAIも読むの大変だからな！😅
    'maxTokens': 500000,       # AIに食わせることを考えてるなら超便利！✨ レスポンス全体のトークン数がこれ以下になるように、デカいファイルから除外してくれるぜ！(ディレクトリ構造のトークンは含まないから、ちょっと超えるかも？)

    # --- 特殊なやつ ---
    'lines': 'false',         # 'text/markdown' か 'text/html' の時、行番号を消せるぜ！デフォルトは行番号付き。
    'disableGenignore': False, # リポジトリにある `.genignore` ファイルを無視するぜ！(デフォルトは False で、.genignore に書かれたファイルは除外される)
}


def get_private_repo_content_with_uithub(owner, repo, token, branch="main", path="", options=None):
    """
    uithub APIを使ってプライベートGitHubリポジトリの内容を取得するぜ！💪

    Args:
        owner (str): リポジトリの持ち主
        repo (str): リポジトリ名
        token (str): GitHub PAT (超重要！)
        branch (str, optional): ブランチ名. Defaults to "main".
        path (str, optional): 特定のパス. Defaults to "".
        options (dict, optional): APIのクエリオプション. Defaults to None.

    Returns:
        str: 取得したリポジトリ内容(テキスト) or None (失敗した時)
    """
    print(f"よっしゃ！ {owner}/{repo} の {branch} ブランチ{(f'/{path}' if path else '')} を取得しに行くぜ！🚀")

    if not token:
        print("🚨 おいおい！そねっち！ GITHUB_TOKEN が設定されてないか、ダミーのままだぜ！ちゃんと有効な PAT を入れてくれよな！頼むぜ！🙏")
        return None

    # APIのURLを組み立てるぜ！ path があればくっつける！
    api_path = f"/tree/{branch}"
    if path:
        api_path += f"/{path.strip('/')}" # パスの前後のスラッシュは念のため除去

    url = f"{UITHUB_BASE_URL}/{owner}/{repo}{api_path}"

    # ヘッダーに認証トークンをセット！これがプライベートアクセスのお作法だぜ！🎩
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # オプション(クエリパラメータ)を準備。値がNoneのやつは除外しとくぜ！
    query_params = {k: v for k, v in (options or {}).items() if v is not None}

    print(f"📡 リクエスト送信先: {url}")
    if query_params:
        print(f"⚙️  オプション: {query_params}")
    if headers.get("Authorization"):
        print("🔑 認証ヘッダー付きでいくぜ！")

    try:
        # いざ、リクエスト！
        response = requests.get(url, headers=headers, params=query_params)

        # エラーだったら例外を発生させて、下の except で捕まえるぜ！
        response.raise_for_status()

        print("やったぜ！🎉 データ取得成功だ！😎")
        # レスポンスのテキストを返すぜ！
        return response.text

    except requests.exceptions.RequestException as e:
        print(f"😭 うわっ！エラー発生！マジかよ…")
        print(f"エラーの種類: {type(e).__name__}")
        print(f"内容: {e}")
        # レスポンスがもしあれば、ステータスコードと内容の最初だけでも見てみるか…
        if hasattr(e, 'response') and e.response is not None:
            print(f"HTTPステータスコード: {e.response.status_code}")
            print(f"サーバーからのメッセージ (一部): {e.response.text[:500]}...") # 長すぎるとアレなので先頭だけ表示
        return None



def analyze_uithub_output(output_text):
    """
    uithubの出力テキストを解析して、統計情報と拡張子カウントを出すぜ！😎
    """
    print("--- uithub 出力解析開始だぜ！🕵️‍♂️ ---")

    lines = output_text.splitlines()
    tree_lines = []
    file_content_section_lines = []  # ファイル内容部分の行を格納するリスト

    # 1. ツリー構造部分とファイル内容部分を分離する
    #    優先ルール: 「最初に連続する2つの空行」が見つかれば、その手前までをツリーとする。
    first_double_empty_line_index = -1  # 連続する空行の最初の行のインデックス
    for i in range(len(lines) - 1):  # lines[i] と lines[i+1] をチェック
        if not lines[i].strip() and not lines[i + 1].strip():  # 2行ともスペースを除去したら空か？
            first_double_empty_line_index = i
            break

    if first_double_empty_line_index != -1:
        print(
            f"🎉 連続する2つの空行を {first_double_empty_line_index + 1} 行目と {first_double_empty_line_index + 2} 行目で発見！ここを区切りにするぜ！")
        tree_lines = lines[:first_double_empty_line_index]  # 最初の空行の直前までがツリー
        file_content_section_lines = lines[first_double_empty_line_index + 2:]  # 2つの空行の次からがファイル内容
    else:
        # 連続空行が見つからない場合、従来のロジック (ファイルタイトルの直前の "---" 区切り線)
        print("🤔 連続する2つの空行は見つからなかったぜ。次に、ファイルタイトルの直前の区切り線で探してみるな！")

        first_content_separator_line_index = -1  # 最初のファイル内容ブロックの直前の区切り線のインデックス
        for i in range(len(lines) - 1):  # lines[i]が区切り線、lines[i+1]がファイルタイトルかチェック
            current_line = lines[i]
            next_line = lines[i + 1]
            # uithubのファイル内容ブロックは `---` の次に `/path:` が来るはず
            if current_line.startswith(
                "--------------------------------------------------------------------------------") and \
                next_line.startswith("/") and next_line.endswith(":"):
                first_content_separator_line_index = i
                break

        if first_content_separator_line_index != -1:
            print(
                f"🎉 ファイル内容の開始区切り線 ({first_content_separator_line_index + 1}行目) を発見！その前をツリーとみなすぜ！")
            tree_lines = lines[:first_content_separator_line_index]  # 区切り線の前までがツリー
            file_content_section_lines = lines[first_content_separator_line_index:]  # 区切り線自体からファイル内容
        else:
            # それでも見つからなければ、全体をツリーとみなす (フォールバック)
            print(
                "⚠️ ファイル内容の開始点となる明確な区切り線が見つからなかったぜ… 全体をツリー構造として処理してみるな！")
            tree_lines = lines
            # file_content_section_lines は空のまま (デフォルトで初期化済み)

    file_content_lines_count = len(file_content_section_lines)

    # ファイル内容部分から、実際のファイルタイトル行を抽出
    # uithubのファイルタイトルは `/path/to/file:` の形式で、その次の行が `---` 区切り線になっている
    file_titles_found = []
    if file_content_section_lines:
        for i, line in enumerate(file_content_section_lines):
            if line.startswith("/") and line.endswith(":"):
                # 次の行が存在し、かつそれが区切り線であるかチェック
                if (i + 1) < len(file_content_section_lines) and \
                    file_content_section_lines[i + 1].startswith(
                        "--------------------------------------------------------------------------------"):
                    file_titles_found.append(line)

    print(f"🌳 ツリー構造部分: {len(tree_lines)} 行")
    print(
        f"📄 ファイルタイトル/内容部分: {file_content_lines_count} 行 (うち、ファイルタイトルとして認識したのは {len(file_titles_found)} 個)")

    # 2. ツリー構造からファイル名を抽出して拡張子をカウント
    tree_filenames = []
    extension_counts = Counter()

    tree_structure_start_index = -1
    for i, line in enumerate(tree_lines):
        stripped_line = line.strip()
        if stripped_line.startswith("├──") or stripped_line.startswith("└──"):
            tree_structure_start_index = i
            break

    if tree_structure_start_index != -1:
        print(f"🌲 ツリー構造の実際の開始行を検出: {tree_structure_start_index + 1} 行目")
        for line in tree_lines[tree_structure_start_index:]:
            line_content = line.strip()
            name_part = ""
            last_space_index = line_content.rfind(' ')
            if last_space_index != -1:
                name_part = line_content[last_space_index + 1:]
            else:
                name_part = line_content

            if not name_part:
                continue

            if '.' in name_part:
                tree_filenames.append(name_part)
                filename_stem, raw_ext = os.path.splitext(name_part)
                ext = ""
                if raw_ext:
                    ext = raw_ext.lower()
                elif name_part.startswith('.'):
                    ext = name_part.lower()
                else:
                    ext = "(拡張子なし)"
                extension_counts[ext] += 1
        print(f"🌳 ツリーから抽出されたファイル(っぽい)名: {len(tree_filenames)} 個")
    else:
        print("⚠️ ツリー構造っぽい行が見つからなかったぜ… 拡張子カウントはスキップするな。")

    # 3. 統計情報をまとめる
    total_lines_in_input = len(lines)  # 元の入力全体の行数
    tree_part_char_count = sum(len(line) for line in tree_lines)
    content_part_char_count = sum(len(line) for line in file_content_section_lines)

    print("\n--- 📊 統計情報 📊 ---")
    print(f"📝 総行数 (入力全体): {total_lines_in_input} 行")
    print(f"  🌳 ツリー構造部分 (分離後): {len(tree_lines)} 行 (約 {tree_part_char_count} 文字)")
    print(
        f"  📄 ファイル内容部分 (分離後、区切り線含む可能性あり): {file_content_lines_count} 行 (約 {content_part_char_count} 文字)")
    print(f"  🧐 実際にタイトルとして認識されたファイル数 (内容部分から): {len(file_titles_found)}")

    if extension_counts:
        print("\n📂 拡張子ごとのファイル数 (ツリー構造から推定):")
        if not tree_filenames:
            print("  (ツリーからファイル名が抽出できなかったため、カウントできませんでした。)")
        else:
            for ext, count in extension_counts.most_common():
                print(f"  {ext}: {count} ファイル")
    else:
        print("\n  拡張子カウント (ツリー構造から) はできなかったぜ… 😥")

    title_extension_counts_for_omake = Counter()
    if file_titles_found:
        for title_line in file_titles_found:
            filename_in_title = title_line.strip('/:').split('/')[-1]
            if '.' in filename_in_title:
                _, raw_ext_title = os.path.splitext(filename_in_title)
                title_ext = ""
                if raw_ext_title:
                    title_ext = raw_ext_title.lower()
                elif filename_in_title.startswith('.'):
                    title_ext = filename_in_title.lower()
                else:
                    title_ext = "(拡張子なし)"
                title_extension_counts_for_omake[title_ext] += 1
            else:
                title_extension_counts_for_omake["(拡張子なし)"] += 1

        if title_extension_counts_for_omake:
            print("\n📂 拡張子ごとのファイル数 (ファイルタイトルから推定 - 参考):")
            for ext, count in title_extension_counts_for_omake.most_common():
                print(f"  {ext}: {count} ファイル")

    print("\n--- 解析完了だぜ！👍 ---")
    return {
        "total_lines": total_lines_in_input,
        "tree_lines_count": len(tree_lines),
        "content_lines_count": file_content_lines_count,
        "tree_char_count": tree_part_char_count,
        "content_char_count": content_part_char_count,
        "files_in_tree_count": len(tree_filenames),
        "extension_counts_from_tree": dict(extension_counts.most_common()),
        "detected_file_titles_count": len(file_titles_found),
        "extension_counts_from_titles": dict(
            title_extension_counts_for_omake.most_common()) if file_titles_found else {}
    }




# --- メインの処理はここからだぜ！ ---
if __name__ == "__main__":
    print("--- uithub プライベートリポジトリ取得スクリプト、いくぜ！🔥 ---")

    # 上で定義した関数を使って、リポジトリの内容をゲット！
    repo_content = get_private_repo_content_with_uithub(
        owner=GITHUB_OWNER,
        repo=GITHUB_REPO,
        token=GITHUB_TOKEN,
        branch=GITHUB_BRANCH,
        path=GITHUB_PATH,
        options=api_options
    )

    # 結果を表示するぜ！
    if repo_content:
        print("\n--- ↓↓↓ ここから取得した内容だぜ！↓↓↓ ---")
        print(repo_content)
        print("--- ↑↑↑ ここまでだぜ！↑↑↑ ---\n")
        print("ミッションコンプリート！👍 どうだ、そねっち！バッチリだろ？😉")

        # 統計情報を出力
        stats = analyze_uithub_output(repo_content)
    else:
        print("\n--- 取得失敗… 😭 ---")
        print("うーん、残念… GITHUB_TOKENとか、リポジトリ名とか、設定を見直してみてくれよな！🤔 ファイトだぜ！💪")
