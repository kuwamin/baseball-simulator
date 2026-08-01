import pandas as pd

from baseball_simulator.data_model.data_model import (
    Batter,
    BatterAbility,
    BatterBasicAbility,
    BatterSpecialAbility,
    CommonInformation,
    CommonSpecialAbility,
    Pitcher,
    PitcherAbility,
    PitcherBasicAbility,
    PitcherSpecialAbility,
    Player,
    Team,
)

# --- 変換用マッピング辞書 ---
DOMINANT_MAP: dict[str, int] = {"右": 1, "左": 2, "両": 3}

RANK_MAP: dict[str, int] = {
    "A": 7,
    "B": 6,
    "C": 5,
    "D": 4,
    "E": 3,
    "F": 2,
    "G": 1,
}

PITCHER_APTITUDE_MAP: dict[str, int] = {
    "先": 1,
    "勝継": 2,
    "負継": 3,
    "セ": 4,
    "抑": 5,
}

BATTER_POSITION_MAP: dict[str, int] = {
    "投": 1,
    "捕": 2,
    "一": 3,
    "二": 4,
    "三": 5,
    "遊": 6,
    "左": 7,
    "中": 8,
    "右": 9,
    "指": 10,
}


def _rank_to_int(val: object) -> int:
    """アルファベットのランク文字列(A~G)を数値に変換する

    Args:
        val: ランクを表す文字列または値（例: "A", "b" など）

    Returns:
        int: 対応する数値（7~1）。変換不可の場合は 0。
    """
    s = str(val).strip().upper()
    return RANK_MAP.get(s, 0)


def load_player_list_file(file_path: str) -> dict[str, Team]:
    """Excelファイルを読み込み、チーム名をキーとした Team オブジェクトの辞書を返す

    Args:
        file_path: 読み込む Excel ファイルのパス

    Returns:
        dict[str, Team]: チーム名をキー、Team オブジェクトを値とする辞書
    """
    excel_data: dict[str, pd.DataFrame] = pd.read_excel(file_path, sheet_name=None)

    teams: dict[str, Team] = {}
    for sheet_name, df in excel_data.items():
        if sheet_name == "Pitcher":
            add_pitchers_from_dataframe(df, teams)
        elif sheet_name == "Batter":
            add_batters_from_dataframe(df, teams)

    return teams


def add_pitchers_from_dataframe(df: pd.DataFrame, teams: dict[str, Team]) -> None:
    """Pitcher シートのデータから Player/Pitcher を構築し、該当する Team に追加する

    Args:
        df: 投手情報が含まれる pandas DataFrame
        teams: プレイヤーを追加先のチーム辞書（破壊的に更新される）

    Returns:
        None
    """
    for _, row in df.iterrows():
        common_info = CommonInformation(
            number=str(row["背番号"]),
            dominant_hitting=DOMINANT_MAP.get(str(row["打"]).strip(), 1),
            dominant_arm=DOMINANT_MAP.get(str(row["投"]).strip(), 1),
            name=str(row["名前"]),
        )

        common_special = CommonSpecialAbility(
            injury_res=_rank_to_int(row["ケガしにくさ"]),
            recovery=_rank_to_int(row["回復"]),
        )

        pitcher_basic = PitcherBasicAbility(
            velocity=int(row["球速"]),
            control=int(row["制球"]),
            stamina=int(row["スタミナ"]),
            breaking_ball_level=int(row["変化量"]),
            breaking_ball_number=int(row["球種数"]),
        )

        pitcher_special = PitcherSpecialAbility(
            clutch_pitching=_rank_to_int(row["対ピンチ"]),
            vs_left_batter=_rank_to_int(row["対左打者"]),
            quick=_rank_to_int(row["クイック"]),
            fastball_life=_rank_to_int(row["ノビ"]),
            toughness=_rank_to_int(row["打たれ強さ"]),
            common_special_ability=common_special,
        )

        pitcher_ability = PitcherAbility(
            basic_ability=pitcher_basic,
            special_ability=pitcher_special,
        )

        pitcher = Pitcher(
            aptitude=PITCHER_APTITUDE_MAP.get(str(row["適性"]).strip(), 1),
            ability=pitcher_ability,
        )

        player = Player(
            player_info=common_info,
            pitcher=pitcher,
            batter=None,
        )

        team_name = str(row["所属"]).strip()
        if team_name not in teams:
            teams[team_name] = Team(team_name=team_name)
        teams[team_name].players.append(player)


def add_batters_from_dataframe(df: pd.DataFrame, teams: dict[str, Team]) -> None:
    """Batter シートのデータから Player/Batter を構築し、該当する Team に追加する

    Args:
        df: 野手情報が含まれる pandas DataFrame
        teams: プレイヤーを追加先のチーム辞書（破壊的に更新される）

    Returns:
        None
    """
    for _, row in df.iterrows():
        common_info = CommonInformation(
            number=str(row["背番号"]),
            dominant_hitting=DOMINANT_MAP.get(str(row["打"]).strip(), 1),
            dominant_arm=DOMINANT_MAP.get(str(row["投"]).strip(), 1),
            name=str(row["名前"]),
        )

        common_special = CommonSpecialAbility(
            injury_res=_rank_to_int(row["ケガしにくさ"]),
            recovery=_rank_to_int(row["回復"]),
        )

        batter_basic = BatterBasicAbility(
            trajectory=int(row["弾道"]),
            meet=int(row["ミート"]),
            power=int(row["パワー"]),
            speed=int(row["走力"]),
            arm=int(row["肩力"]),
            fielding=int(row["守備"]),
            catching=int(row["捕球"]),
        )

        batter_special = BatterSpecialAbility(
            clutch_batting=_rank_to_int(row["チャンス"]),
            vs_left_pitcher=_rank_to_int(row["対左投手"]),
            stealing=_rank_to_int(row["盗塁"]),
            base_running=_rank_to_int(row["走塁"]),
            throwing=_rank_to_int(row["送球"]),
            eye=_rank_to_int(row["選球眼"]),
            common_special_ability=common_special,
        )

        batter_ability = BatterAbility(
            basic_ability=batter_basic,
            special_ability=batter_special,
        )

        batter = Batter(
            position=BATTER_POSITION_MAP.get(str(row["ポジション"]).strip(), 10),
            ability=batter_ability,
        )

        player = Player(
            player_info=common_info,
            batter=batter,
            pitcher=None,
        )

        team_name = str(row["所属"]).strip()
        if team_name not in teams:
            teams[team_name] = Team(team_name=team_name)
        teams[team_name].players.append(player)
