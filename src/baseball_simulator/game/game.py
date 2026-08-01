# baseball_simulator/game/game.py

from baseball_simulator.data_model.data_model import Team
from baseball_simulator.data_model.game_model import GameState, StartingLineup
from baseball_simulator.game.lineup_selector import build_starting_lineup


def init_game(
    home_team: Team,
    away_team: Team,
    game_number: int,
    is_fatigue_considered: bool = True,
) -> GameState:
    """試合の初期状態（GameState）を構築し、出場選手の試合数カウントを1増やす"""
    home_lineup = build_starting_lineup(home_team, game_number, is_fatigue_considered)
    away_lineup = build_starting_lineup(away_team, game_number, is_fatigue_considered)

    # 出場選手の通算出場数（games）をインクリメント
    _increment_appearance_stats(home_lineup)
    _increment_appearance_stats(away_lineup)

    return GameState(
        home_lineup=home_lineup,
        away_lineup=away_lineup,
        inning=1,
        is_top=True,
        home_score=0,
        away_score=0,
        out_count=0,
    )


def _increment_appearance_stats(lineup: StartingLineup) -> None:
    """スタメン出場選手および先発投手の試合数（games）・先発数（starter）を加算する"""
    # 野手陣の試合数更新
    for player in lineup.lineup:
        if player.batter:
            player.batter.stats.common_stats.games += 1

    # 先発投手の登板数・先発数更新
    starter = lineup.starter_pitcher
    if starter.pitcher:
        starter.pitcher.stats.common_stats.games += 1
        starter.pitcher.stats.starter += 1


def play_game(
    home_team: Team,
    away_team: Team,
    game_number: int,
    is_fatigue_considered: bool = True,
) -> GameState:
    """1試合のシミュレーションを最後まで実行する（メインループ）"""
    game_state = init_game(home_team, away_team, game_number, is_fatigue_considered)

    return game_state
