from __future__ import annotations

from baseball_simulator.common.const import POS_FATIGUE_MAP, RECOVERY_MAP
from baseball_simulator.data_model.data_model import Player
from baseball_simulator.data_model.game_model import GameState, StartingLineup


def update_game_fatigue(game_state: GameState) -> None:
    """試合終了後の全出場・ベンチ選手の疲労度（スタミナ消費・蓄積疲労）を更新する

    Args:
        game_state (GameState): 現在のゲーム状態インスタンス
    """
    _update_team_fatigue(game_state.home_lineup)
    _update_team_fatigue(game_state.away_lineup)


def _update_team_fatigue(starting_lineup: StartingLineup) -> None:
    """チームごとの投手・野手の疲労度更新処理

    Args:
        starting_lineup (StartingLineup): チームのスタメン・出場選手情報
    """
    _update_pitcher_fatigue(starting_lineup)
    _update_batter_fatigue(starting_lineup)


def _update_pitcher_fatigue(starting_lineup: StartingLineup) -> None:
    """投手のスタミナ消費および蓄積疲労の計算

    Args:
        starting_lineup (StartingLineup): チームのスタメン・出場選手情報
    """
    # チームに所属する全選手から投手を抽出
    team_pitchers: list[Player] = [
        p for p in starting_lineup.team.players if p.pitcher is not None
    ]

    for p in team_pitchers:
        pitcher_obj = p.pitcher
        if pitcher_obj is None:
            continue

        # 回復力の参照
        recovery_code: str = (
            pitcher_obj.ability.special_ability.common_special_ability.recovery
        )
        base_recover: float = float(RECOVERY_MAP.get(recovery_code, 15))
        barometer = p.barometer

        # 当日の対戦打者数を取得
        today_bf: int = pitcher_obj.stats.game_bf

        if today_bf > 0:
            # --- 当日登板した投手 ---
            # 1試合中のスタミナ消費量（当日の打者数に応じた負荷を設定）
            pitcher_obj.fatugue_stamina = int(today_bf * 2.5)

            # 蓄積疲労の加算
            fatigue_add = (today_bf * 0.25) - (base_recover * 0.1)
            barometer.accumulates_fatigue += max(1, round(fatigue_add))
        else:
            # --- 当日登板しなかった投手：回復 ---
            # 1試合中のスタミナ消費量を回復（リセット）
            pitcher_obj.fatugue_stamina = max(
                0, pitcher_obj.fatugue_stamina - int(base_recover * 2.0)
            )

            # 先発起用（登板なし＝中○日のローテ消化中）かどうかで回復量を分岐
            is_starter: bool = pitcher_obj.aptitude == "先"
            recovery_weight: float = 0.35 if is_starter else 0.15

            recovered_fatigue = round(base_recover * recovery_weight)
            barometer.accumulates_fatigue -= max(1, recovered_fatigue)

        # 蓄積疲労の底打ち処理
        barometer.accumulates_fatigue = max(0, barometer.accumulates_fatigue)

        # 当日の打者数をリセットして次の試合に備える
        pitcher_obj.stats.game_bf = 0


def _update_batter_fatigue(starting_lineup: StartingLineup) -> None:
    """野手の蓄積疲労の計算

    Args:
        starting_lineup (StartingLineup): チームのスタメン・出場選手情報
    """
    positions_map: dict[Player, str] = starting_lineup.positions
    starter_set: set[Player] = set(starting_lineup.lineup)

    # チーム所属の全野手
    all_batter_players: list[Player] = [
        p for p in starting_lineup.team.players if p.batter is not None
    ]

    for batter_player in all_batter_players:
        batter_obj = batter_player.batter
        if batter_obj is None:
            continue

        # 回復力の参照 (common_special_ability -> recovery)
        recovery_code: str = (
            batter_obj.ability.special_ability.common_special_ability.recovery
        )
        base_recover: float = float(RECOVERY_MAP.get(recovery_code, 15))
        barometer = batter_player.barometer

        if batter_player in starter_set:
            # 出場野手：守備位置に応じた負荷計算
            pos: str = positions_map.get(batter_player, "")
            fatigue_weight: float = float(POS_FATIGUE_MAP.get(pos, 1.0))
            fatigue_add = fatigue_weight - (base_recover * 0.02)
            barometer.accumulates_fatigue += max(0, round(fatigue_add))
        else:
            # 不出場野手：回復
            recovered = round(base_recover * 0.1)
            barometer.accumulates_fatigue -= max(1, recovered)

        # 蓄積疲労の底打ち処理
        barometer.accumulates_fatigue = max(0, barometer.accumulates_fatigue)
