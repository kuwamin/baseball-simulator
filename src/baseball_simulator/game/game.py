from baseball_simulator.data_model.data_model import Team
from baseball_simulator.data_model.game_model import GameState, StartingLineup
from baseball_simulator.game.at_bat_rules import AtBatResult, determine_at_bat_result
from baseball_simulator.game.lineup_selector import build_starting_lineup
from baseball_simulator.game.runner_rules import advance_runners


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
    """1打席を実行し、打席結果に基づいて打者・投手の成績とゲーム状態を更新する"""
    batter_player = game_state.get_current_batter()
    pitcher_player = game_state.get_current_pitcher()

    # 打席結果の判定
    result = determine_at_bat_result(pitcher_player, batter_player)

    # 打撃成績の更新
    if batter_player.batter:
        b_stats = batter_player.batter.stats
        b_stats.pa += 1

        if result == AtBatResult.SINGLE:
            b_stats.ab += 1
            b_stats.singles += 1
        elif result == AtBatResult.DOUBLE:
            b_stats.ab += 1
            b_stats.doubles += 1
        elif result == AtBatResult.TRIPLE:
            b_stats.ab += 1
            b_stats.triples += 1
        elif result == AtBatResult.HOME_RUN:
            b_stats.ab += 1
            b_stats.homerun += 1
        elif result == AtBatResult.WALK:
            b_stats.walks += 1
        elif result == AtBatResult.STRIKEOUT:
            b_stats.ab += 1
            b_stats.so += 1
        elif result == AtBatResult.OUT:
            b_stats.ab += 1

    # 投手成績の更新
    if pitcher_player.pitcher:
        p_stats = pitcher_player.pitcher.stats
        p_stats.bf += 1

        if result in (
            AtBatResult.SINGLE,
            AtBatResult.DOUBLE,
            AtBatResult.TRIPLE,
            AtBatResult.HOME_RUN,
        ):
            p_stats.hits_allowed += 1
            if result == AtBatResult.HOME_RUN:
                p_stats.hr_allowed += 1
        elif result == AtBatResult.WALK:
            p_stats.walks_allowed += 1
        elif result == AtBatResult.STRIKEOUT:
            p_stats.strikeouts += 1
            p_stats.outs += 1
        elif result == AtBatResult.OUT:
            p_stats.outs += 1

    # 進塁処理と得点・打点・失点の記録
    if result not in (AtBatResult.OUT, AtBatResult.STRIKEOUT):
        runs = advance_runners(result, batter_player, game_state.bases)
        if runs > 0:
            game_state.add_score(runs)

            # 打者の打点(rbi)を加算
            if batter_player.batter:
                batter_player.batter.stats.rbi += runs

            # 投手の失点・自責点を加算
            if pitcher_player.pitcher:
                pitcher_player.pitcher.stats.run_allowed += runs
                pitcher_player.pitcher.stats.earned_run += runs

    # アウトカウントとゲーム状態の更新
    if result in (AtBatResult.OUT, AtBatResult.STRIKEOUT):
        game_state.out_count += 1

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
