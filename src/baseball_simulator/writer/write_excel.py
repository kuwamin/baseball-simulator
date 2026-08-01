import pandas as pd

from baseball_simulator.data_model.data_model import Player, Team

# 逆引き用マッピング辞書
REVERSE_PITCHER_APTITUDE_MAP: dict[int, str] = {
    1: "先",
    2: "勝継",
    3: "負継",
    4: "セ",
    5: "抑",
}

REVERSE_BATTER_POSITION_MAP: dict[int, str] = {
    1: "投",
    2: "捕",
    3: "一",
    4: "二",
    5: "三",
    6: "遊",
    7: "左",
    8: "中",
    9: "右",
    10: "指",
}


def export_stats_to_excel(teams: dict[str, Team], output_file: str) -> None:
    """チーム辞書から全チームの投手・野手成績をそれぞれシート別にExcelへ書き出す

    Args:
        teams: チーム名をキーとしたTeamオブジェクトの辞書
        output_file: 出力先Excelファイルのパス

    Returns:
        None
    """
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for team_name, team in teams.items():
            # 1. 投手成績データの構築
            pitcher_rows = []
            for player in team.players:
                if player.pitcher is not None:
                    pitcher_rows.append(_build_pitcher_stat_row(team_name, player))

            if pitcher_rows:
                df_pitcher = pd.DataFrame(pitcher_rows)
                df_pitcher.to_excel(
                    writer, sheet_name=f"{team_name}_Pitcher", index=False
                )

            # 2. 野手成績データの構築
            batter_rows = []
            for player in team.players:
                if player.batter is not None:
                    batter_rows.append(_build_batter_stat_row(team_name, player))

            if batter_rows:
                df_batter = pd.DataFrame(batter_rows)
                df_batter.to_excel(
                    writer, sheet_name=f"{team_name}_Batter", index=False
                )


def _build_pitcher_stat_row(team_name: str, player: Player) -> dict[str, object]:
    """投手1人分の成績行辞書を生成する

    Args:
        team_name: プレイヤーが所属するチーム名
        player: 対象のPlayerオブジェクト

    Returns:
        dict[str, object]: Excel出力用の列名をキーとする投手成績辞書

    Raises:
        ValueError: プレイヤーが投手データ（pitcher）を保持していない場合
    """
    pitcher = player.pitcher
    if pitcher is None:
        raise ValueError(f"Player '{player.player_info.name}' has no pitcher data.")

    stats = pitcher.stats
    info = player.player_info

    # アウト数からイニング数（回数）を算出
    innings = stats.outs // 3

    return {
        "所属": team_name,
        "背番号": info.number,
        "名前": info.name,
        "適性": REVERSE_PITCHER_APTITUDE_MAP.get(pitcher.aptitude, ""),
        "登板数": stats.common_stats.games,
        "先発数": stats.starter,
        "勝利": stats.wins,
        "敗北": stats.losses,
        "セーブ": stats.saves,
        "ホールド": stats.holds,
        "イニング数": innings,
        "完投": stats.completes,
        "完封": stats.shutouts,
        "打者数": stats.bf,
        "奪三振": stats.strikeouts,
        "与四球": stats.walks_allowed,
        "与死球": stats.hbp_allowed,
        "被本塁打": stats.hr_allowed,
        "被安打": stats.hits_allowed,
        "失点": stats.run_allowed,
        "自責点": stats.earned_run,
        "QS": stats.qs,
        "HQS": stats.hqs,
        "得点圏被打数": stats.risp_batter_faces,
        "得点圏被安打": stats.risp_hit_allowed,
    }


def _build_batter_stat_row(team_name: str, player: Player) -> dict[str, object]:
    """野手1人分の成績行辞書を生成する

    Args:
        team_name: プレイヤーが所属するチーム名
        player: 対象のPlayerオブジェクト

    Returns:
        dict[str, object]: Excel出力用の列名をキーとする野手成績辞書

    Raises:
        ValueError: プレイヤーが野手データ（batter）を保持していない場合
    """
    batter = player.batter
    if batter is None:
        raise ValueError(f"Player '{player.player_info.name}' has no batter data.")

    stats = batter.stats
    info = player.player_info

    # 安打数の合計算出
    hits = stats.singles + stats.doubles + stats.triples + stats.homerun

    return {
        "所属": team_name,
        "背番号": info.number,
        "名前": info.name,
        "ポジション": REVERSE_BATTER_POSITION_MAP.get(batter.position, ""),
        "試合数": stats.common_stats.games,
        "打席": stats.pa,
        "打数": stats.ab,
        "安打": hits,
        "単打": stats.singles,
        "二塁打": stats.doubles,
        "三塁打": stats.triples,
        "本塁打": stats.homerun,
        "打点": stats.rbi,
        "四球": stats.walks,
        "死球": stats.hbp,
        "三振": stats.so,
        "犠打": stats.sac_bunt,
        "犠飛": stats.sac_fly,
        "盗塁成功": stats.steals,
        "盗塁死": stats.caught_stealing,
        "併殺打": stats.gdp,
        "得点圏打数": stats.risp_ab,
        "得点圏安打": stats.risp_hits,
    }
