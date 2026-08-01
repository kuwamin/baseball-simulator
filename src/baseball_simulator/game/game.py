# baseball_simulator/game/game.py

from baseball_simulator.data_model.data_model import Team
from baseball_simulator.data_model.game_model import GameState, StartingLineup
from baseball_simulator.game.lineup_selector import build_starting_lineup


def play_game(
    home_team: Team,
    away_team: Team,
) -> GameState:
    """1試合のシミュレーションを最後まで実行する（メインループ）"""
    game_state = init_game(home_team, away_team)

    # 9回裏が終わるまで打席を回す
    while not game_state.is_game_over:
        execute_at_bat(game_state)

    return game_state


def init_game(
    home_team: Team,
    away_team: Team,
) -> GameState:
    """試合の初期状態（GameState）を構築し、出場選手の試合数カウントを1増やす"""
    home_lineup = build_starting_lineup(home_team)
    away_lineup = build_starting_lineup(away_team)

    # 出場選手の試合数をインクリメント
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


def execute_at_bat(game_state: GameState) -> None:
    """【モック】全打席凡退（アウト）として処理し、打者・投手の成績とゲーム状態を更新する"""
    batter_player = game_state.get_current_batter()
    pitcher_player = game_state.get_current_pitcher()

    # カウント・ゲーム状態の更新
    game_state.out_count += 1

    # 打撃成績の更新 ( Batter 側の Player )
    if batter_player.batter:
        batter_player.batter.stats.pa += 1  # 打席数
        batter_player.batter.stats.ab += 1  # 打数

    # 投手成績の更新 ( Pitcher 側の Player )
    if pitcher_player.pitcher:
        pitcher_player.pitcher.stats.bf += 1  # 対戦打者数
        pitcher_player.pitcher.stats.outs += 1  # 取得アウト数

    # 3アウトならチェンジ、継続なら次の打者へ
    if game_state.out_count >= 3:
        game_state.change_possession()
    else:
        game_state.advance_next_batter()


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
