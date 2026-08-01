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
            number=str(row["背番号"]).strip(),
            dominant_hitting=str(row["打"]).strip(),
            dominant_arm=str(row["投"]).strip(),
            name=str(row["名前"]).strip(),
        )

        common_special = CommonSpecialAbility(
            injury_res=str(row["ケガしにくさ"]).strip(),
            recovery=str(row["回復"]).strip(),
        )

        pitcher_basic = PitcherBasicAbility(
            velocity=int(row["球速"]),
            control=int(row["制球"]),
            stamina=int(row["スタミナ"]),
            breaking_ball_level=int(row["変化量"]),
            breaking_ball_number=int(row["球種数"]),
        )

        pitcher_special = PitcherSpecialAbility(
            clutch_pitching=str(row["対ピンチ"]).strip(),
            vs_left_batter=str(row["対左打者"]).strip(),
            quick=str(row["クイック"]).strip(),
            fastball_life=str(row["ノビ"]).strip(),
            toughness=str(row["打たれ強さ"]).strip(),
            common_special_ability=common_special,
        )

        pitcher_ability = PitcherAbility(
            basic_ability=pitcher_basic,
            special_ability=pitcher_special,
        )

        pitcher = Pitcher(
            aptitude=str(row["適性"]).strip(),
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
            number=str(row["背番号"]).strip(),
            dominant_hitting=str(row["打"]).strip(),
            dominant_arm=str(row["投"]).strip(),
            name=str(row["名前"]).strip(),
        )

        common_special = CommonSpecialAbility(
            injury_res=str(row["ケガしにくさ"]).strip(),
            recovery=str(row["回復"]).strip(),
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
            clutch_batting=str(row["チャンス"]).strip(),
            vs_left_pitcher=str(row["対左投手"]).strip(),
            stealing=str(row["盗塁"]).strip(),
            base_running=str(row["走塁"]).strip(),
            throwing=str(row["送球"]).strip(),
            eye=str(row["選球眼"]).strip(),
            common_special_ability=common_special,
        )

        batter_ability = BatterAbility(
            basic_ability=batter_basic,
            special_ability=batter_special,
        )

        batter = Batter(
            position=str(row["ポジション"]).strip(),
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
