from __future__ import annotations

import random

from baseball_simulator.data_model.data_model import Pitcher, Team
from baseball_simulator.data_model.game_model import GameState, StartingLineup
from baseball_simulator.game.at_bat_rules import AtBatResult, determine_at_bat_result
from baseball_simulator.game.fatigue_rules import update_game_fatigue
from baseball_simulator.game.lineup_selector import build_starting_lineup
from baseball_simulator.game.runner_rules import advance_runners


def play_game(
    home_team: Team,
    away_team: Team,
) -> GameState:
    """1試合のシミュレーションを最後まで実行する（メインループ）"""
    # スタメン、先発決定
    game_state = init_game(home_team, away_team)

    # 試合終了まで打席を回す
    while not game_state.is_game_over:
        execute_at_bat(game_state)

    # 出場選手の試合数をインクリメント
    _increment_appearance_stats(game_state)

    # 試合終了後に疲労度・回復の更新を実行
    update_game_fatigue(game_state)

    return game_state


def init_game(
    home_team: Team,
    away_team: Team,
) -> GameState:
    """試合の初期状態（GameState）を構築し、出場選手の試合数カウントを1増やす"""
    home_lineup = build_starting_lineup(home_team)
    away_lineup = build_starting_lineup(away_team)

    game_state = GameState(
        home_lineup=home_lineup,
        away_lineup=away_lineup,
        inning=1,
        is_top=True,
        home_score=0,
        away_score=0,
        out_count=0,
    )

    # 両チームの先発投手のスタミナをそれぞれ独立して初期化
    game_state.home_pitcher_stamina = _init_stamina(
        home_lineup.starter_pitcher, is_starter=True
    )
    game_state.away_pitcher_stamina = _init_stamina(
        away_lineup.starter_pitcher, is_starter=True
    )

    return game_state


def _init_stamina(pitcher: Pitcher, is_starter: bool) -> float:
    """投手の登板時スタミナ初期値を計算する"""

    base = float(pitcher.ability.basic_ability.stamina - pitcher.fatugue_stamina)
    if is_starter:
        init_stamina = base * 1.5
    else:
        init_stamina = base * 0.2
    return init_stamina


def execute_at_bat(game_state: GameState) -> None:
    """1打席を実行し、打席結果に基づいて打者・投手の成績とゲーム状態を更新する"""

    batter = game_state.get_current_batter()
    pitcher = game_state.get_current_pitcher()

    # 得点圏の判定
    is_risp = False

    # 打席結果の判定
    result = determine_at_bat_result(pitcher, batter, is_risp)

    # 打撃成績の更新
    b_stats = batter.stats
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
    p_stats = pitcher.stats
    p_stats.bf += 1
    p_stats.game_bf += 1
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

    # 1打席ごとのスタミナ減算 (1~7のランダム値)
    game_state.current_pitcher_stamina -= random.randint(1, 7)

    # 進塁処理と得点・打点・失点の記録
    if result not in (AtBatResult.OUT, AtBatResult.STRIKEOUT):
        runs = advance_runners(result, batter, game_state.bases)
        if runs > 0:
            game_state.add_score(runs)

            # 打者の打点(rbi)を加算
            batter.stats.rbi += runs

            # 投手の失点・自責点を加算
            pitcher.stats.run_allowed += runs
            pitcher.stats.earned_run += runs

    # アウトカウントとゲーム状態の更新
    if result in (AtBatResult.OUT, AtBatResult.STRIKEOUT):
        game_state.out_count += 1

    # 3アウトならチェンジ、継続なら次の打者へ
    if game_state.out_count >= 3:
        game_state.change_possession()
        # チェンジ後に新しい守備側の投手スタミナをチェック＆必要なら交代
        check_and_change_pitcher(game_state)
    else:
        game_state.advance_next_batter()


def check_and_change_pitcher(game_state: GameState) -> None:
    """イニング開始時（out_count == 0）に投手のスタミナをチェックし、切れ（<=0）ていればリリーフへ交代する"""

    current_pitcher = game_state.get_current_pitcher()

    # スタミナ切れ判定（スタミナが0以下の場合に交代を検討）
    if game_state.current_pitcher_stamina <= 0:
        # 点差の計算（自チームの得点 - 相手チームの得点）
        if game_state.is_top:
            score_diff = game_state.home_score - game_state.away_score
        else:
            score_diff = game_state.away_score - game_state.home_score

        # リリーフの選出
        reliever = decide_relief(game_state, game_state.inning, score_diff)

        # 選出された投手が現在登板中の投手と同じ場合（続投）は交代処理を行わない
        if reliever == current_pitcher:
            return

        # 成績の更新（交代時のみ登板数を+1）
        reliever.stats.common_stats.games += 1

        # 投手交代
        game_state.change_pitcher(reliever)

        # リリーフのスタミナ初期化
        game_state.current_pitcher_stamina = _init_stamina(reliever, is_starter=False)


def decide_relief(
    game_state: GameState,
    inning: int,
    score_diff: int,
) -> Pitcher:
    """現在のイニング・点差・登板状況に応じて継投するリリーフ投手を選出する。

    Args:
        game_state (GameState): 現在の試合状態（守備側の現在登板中投手やラインナップを取得するために使用）
        inning (int): 現在のイニング (1〜)
        score_diff (int): 点差（自チームの得点 - 相手チームの得点）

    Returns:
        Pitcher: 選出された投手。交代可能なリリーフがいない場合は現在登板中の投手をそのまま返す。
    """
    # 守備側の StartingLineup と現在登板中の投手を自動取得
    current_lineup = (
        game_state.home_lineup if game_state.is_top else game_state.away_lineup
    )
    current_pitcher = game_state.get_current_pitcher()

    # チームに所属する全 Pitcher オブジェクトを取得
    pitchers: list[Pitcher] = [
        player.pitcher
        for player in current_lineup.team.players
        if player.pitcher is not None
    ]

    # すでに登板済みの投手（打者対戦数 game_bf > 0 の選手）
    already_played_list: list[Pitcher] = [
        pitcher for pitcher in pitchers if pitcher.stats.game_bf > 0
    ]

    # 未登板の投手リスト
    available_pitchers: list[Pitcher] = [
        pitcher for pitcher in pitchers if pitcher not in already_played_list
    ]

    # 未登板の投手が誰もいない場合、現在登板中の投手をそのまま返して続投
    if not available_pitchers:
        return current_pitcher

    # イニング・点差に応じた role_target の設定
    if inning >= 9:
        if 0 <= score_diff <= 3:
            role_target = ["抑"]
        elif score_diff == -1 or score_diff >= 4:
            role_target = ["セ", "勝継"]
        else:
            role_target = ["負継"]
    elif inning >= 7:
        if -1 <= score_diff <= 3:
            role_target = ["セ"]
        elif score_diff >= 4:
            role_target = ["勝継", "セ"]
        else:
            role_target = ["負継", "勝継"]
    else:
        if score_diff >= 0:
            role_target = ["勝継"]
        else:
            role_target = ["負継"]

    # 役割条件 ＆ 体力フィルターによる抽出
    candidates: list[Pitcher] = []
    for pitcher in available_pitchers:
        # 役割(aptitude)が合致し、スタミナ余裕があるかチェック
        is_role_matched = pitcher.aptitude in role_target
        has_stamina = (
            pitcher.ability.basic_ability.stamina - pitcher.fatugue_stamina * 2
        ) > 0

        if is_role_matched and has_stamina:
            candidates.append(pitcher)

    # 1つ目の条件（役割＋スタミナ）に合致する選手がいれば先頭を返す
    if candidates:
        return candidates[0]

    # すべての条件から外れた場合、現在登板中の投手を返す
    return current_pitcher


def _increment_appearance_stats(game_state: GameState) -> None:
    _increment_team_appearance_stats(game_state.home_lineup)
    _increment_team_appearance_stats(game_state.away_lineup)


def _increment_team_appearance_stats(lineup: StartingLineup) -> None:
    """スタメン出場選手および先発投手の試合数（games）・先発数（starter）を加算する"""
    # 野手陣の試合数更新
    for batter in lineup.lineup:
        batter.stats.common_stats.games += 1

    # 先発投手の登板数・先発数更新
    starter = lineup.starter_pitcher
    starter.stats.common_stats.games += 1
    starter.stats.starter += 1
