import sys
import jaconv
import json
import MeCab
import csv
import re

# -Oyomi 読みのみの出力
# -d 辞書のパス指定
mecab_dictionary_dir = "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"
mecab_tagger = MeCab.Tagger("-d {0}".format(mecab_dictionary_dir))
mecab_yomi = MeCab.Tagger("-Oyomi -d {0}".format(mecab_dictionary_dir))

def load_csv(filename, skip_header=True, delimiter='\t', encoding='utf-8'):
    """ CSVファイルを読み込み、その内容をリストとして返却する """
    data = []
    with open(filename, newline='', encoding=encoding) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        if skip_header:
            # ヘッダー行をスキップ
            next(csv_reader, None)
        for row in csv_reader:
            data.append(row)
    return data

def replace_text(text, replacements):
    """ 指定された文字列に対して、置換ルールに従って文字列を置換する """
    for target, replacement in replacements:
        text = text.replace(target, replacement)
    return text

def custom_replace(text, replacements):
    """ 指定された文字列に対して、置換ルールに従って文字列を置換する。 """
    is_replaced = False
    for target, replacement in replacements:
        if text.startswith(target):
            text = text.replace(target, replacement)
            is_replaced = True
            break
    return is_replaced, text

def is_alpha_num_symbol(text):
    """
    文字列がアルファベット、数字、および記号のみで構成されているかどうかを判定する。
    記号は一般的に使用されるものに限定される。
    """
    # アルファベット、数字、一部の記号のみにマッチする正規表現パターン
    pattern = re.compile(r'^[a-zA-Z0-9\s!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?~`]+$')
    # 文字列がパターンにマッチするかどうかを判定
    return bool(pattern.match(text))


def henkan(value, custom_replacements, replacements):
    # アルファベットが中途半端に変換されるため、完全一致で手動置換
    is_replaced, pre_value = custom_replace(value, custom_replacements)
    # 読み方が違うものがあるため、単語単位で辞書置換
    pre_value = replace_text(pre_value, replacements)

    pre_value_original = pre_value
    replaces = [["\t","@t"], [" ","@s"], ["%","@p"]]
    for replace in replaces:
        pre_value = pre_value.replace(replace[0], replace[1])
    parsed = mecab_tagger.parse(pre_value)
    result = ""
    for parsed_word in parsed.split('\n'):
        # EOSや空行を無視
        if parsed_word == 'EOS' or parsed_word == '':
            continue
        # 行をタブで分割して、表層形と素性情報を取得
        surface, feature = parsed_word.split('\t')
        features = feature.split(',')
        # 素性情報から読みを取得（カタカナで）
        # アルファベットや記号を無視するために品詞をチェック
        # features[0]は品詞、features[8]は読み（カタカナ）
        try:
            if is_alpha_num_symbol(surface) or features[0] in ["記号", "アルファベット"]:
                result += surface
            elif len(features) >= 8 and features[7] != "*":
                result += features[7]
            else:
                result += mecab_yomi.parse(surface).strip()
        except Exception as e:
            result += surface
    for replace in replaces:
        result = result.replace(replace[1], replace[0])

    hiragana_value = jaconv.kata2hira(result)
    katakana_value = jaconv.hira2kata(hiragana_value)
    return hiragana_value, katakana_value

def main():
    # 置換対象文字列
    replacements = load_csv('./dictionary/katakana/replacements.csv', skip_header=False)
    custom_replacements = load_csv('./dictionary/katakana/custom_replacements.csv', skip_header=False)

    src_lang_file_path = './texts/ja_JP.lang'
    dst_katakana_lang_file_path = './katakana_resourcepack/texts/katakana_JP.lang'
    dst_hiragana_lang_file_path = './hiragana_resourcepack/texts/hiragana_JP.lang'

    with open(src_lang_file_path, "r", encoding="utf-8-sig", newline='') as src_file:
        with open(dst_katakana_lang_file_path, 'w', encoding="utf-8-sig", newline='\n') as dst_katakana_file:
            with open(dst_hiragana_lang_file_path, 'w', encoding="utf-8-sig", newline='\n') as dst_hiragana_file:
                for line in src_file:
                    line = line.strip()
                    print(line)

                    line_split = line.split("=")
                    hiragana_line = line
                    katakana_line = line
                    if len(line_split) == 2:
                        key = line_split[0]
                        value = line_split[1]
                        hiragana_value, katakana_value = henkan(value, custom_replacements, replacements)
                        hiragana_line = f"{key}={hiragana_value}"
                        katakana_line = f"{key}={katakana_value}"
                    print(hiragana_line)
                    print(katakana_line)
                    dst_hiragana_file.write(hiragana_line + '\n')
                    dst_katakana_file.write(katakana_line + '\n')

if __name__ == "__main__":
    main()

