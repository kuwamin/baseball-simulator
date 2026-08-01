from __future__ import annotations

from baseball_simulator.data_model.data_model import Player, Team
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
    game_state = init_game(home_team, away_team)

    # 試合終了まで打席を回す
    while not game_state.is_game_over:
        execute_at_bat(game_state)

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
    # 打席前に投手交代の必要性を確認・実行
    check_and_change_pitcher(game_state)

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


def check_and_change_pitcher(game_state: GameState) -> None:
    """現在のイニング・投手の疲労状態・点差に応じて継投チェックを行い、必要なら投手を交代する"""
    current_pitcher = game_state.get_current_pitcher()
    pitcher_obj = current_pitcher.pitcher

    if pitcher_obj is None:
        return

    # 現在の守備側チームのラインナップを取得
    defending_lineup = (
        game_state.away_lineup if game_state.is_top else game_state.home_lineup
    )

    # スタミナ限界チェック: (stamina - fatugue_stamina * 2) <= 0 または イニングに応じた継投判断
    stamina_margin = pitcher_obj.ability.basic_ability.stamina - (
        pitcher_obj.fatugue_stamina * 2
    )

    # 交代条件: スタミナ切れ、または7回以降で降板判定
    need_change = stamina_margin <= 0 or game_state.inning >= 7

    if need_change:
        # 点差の計算（自チームの得点 - 相手チームの得点）
        if game_state.is_top:
            # アウェイ（先攻）守備時：away_score - home_score
            score_diff = game_state.away_score - game_state.home_score
        else:
            # ホーム（後攻）守備時：home_score - away_score
            score_diff = game_state.home_score - game_state.away_score

        reliever = decide_relief(
            starting_lineup=defending_lineup,
            inning=game_state.inning,
            score_diff=score_diff,
        )

        # 交代可能な継投投手が存在し、現在の投手と異なる場合に交代を実行
        if reliever is not None and reliever is not current_pitcher:
            # 登板数（games）をインクリメント
            if reliever.pitcher:
                reliever.pitcher.stats.common_stats.games += 1

            # GameState 内の現在投手を更新するメソッドを呼び出し
            game_state.change_pitcher(reliever)


def decide_relief(
    starting_lineup: StartingLineup,
    inning: int,
    score_diff: int,
) -> Player | None:
    """現在のイニング・点差・登板状況に応じて継投するリリーフ投手を選出する。

    Args:
        starting_lineup (StartingLineup): チームのスタメン・出場選手情報
        inning (int): 現在のイニング (1〜)
        score_diff (int): 点差（自チームの得点 - 相手チームの得点）

    Returns:
        Player | None: 選出された投手（Playerオブジェクト）。登板可能選手がいない場合は None。
    """
    # チームに所属する全投手
    all_pitchers: list[Player] = [
        p for p in starting_lineup.team.players if p.pitcher is not None
    ]

    # すでに登板済みの投手（打者対戦数 bf > 0 の選手）
    already_played_list: list[Player] = [
        p for p in all_pitchers if p.pitcher is not None and p.pitcher.stats.bf > 0
    ]

    # 未登板の投手リスト
    available_pitchers = [p for p in all_pitchers if p not in already_played_list]

    if not available_pitchers:
        return None

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
    candidates: list[Player] = []
    for p in available_pitchers:
        pitcher_obj = p.pitcher
        if pitcher_obj is None:
            continue

        # 役割(aptitude)が合致し、スタミナ余裕があるかチェック
        # (basic_ability.stamina - fatugue_stamina * 2) > 0
        is_role_matched = pitcher_obj.aptitude in role_target
        has_stamina = (
            pitcher_obj.ability.basic_ability.stamina - pitcher_obj.fatugue_stamina * 2
        ) > 0

        if is_role_matched and has_stamina:
            candidates.append(p)

    # 1つ目の条件（役割＋スタミナ）に合致する選手がいれば先頭を返す
    if candidates:
        return candidates[0]

    # 3. フォールバック処理
    # 先発("先")以外で未登板の投手を抽出
    fallback_candidates = [
        p
        for p in available_pitchers
        if p.pitcher is not None and p.pitcher.aptitude != "先"
    ]

    if fallback_candidates:
        # fatugue_stamina が最も小さい選手を選出
        return min(
            fallback_candidates,
            key=lambda p: p.pitcher.fatugue_stamina if p.pitcher else 9999,
        )

    # 先発以外も残っていない場合は、未登板の中で最も疲労度が少ない選手を返す
    return min(
        available_pitchers,
        key=lambda p: p.pitcher.fatugue_stamina if p.pitcher else 9999,
    )
