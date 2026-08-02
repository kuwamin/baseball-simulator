from __future__ import annotations

from baseball_simulator.common.const import POS_FATIGUE_MAP, RECOVERY_MAP
from baseball_simulator.data_model.data_model import Batter, Pitcher
from baseball_simulator.data_model.game_model import GameState, StartingLineup


def pitcher_fatigue_correction(accumulates_fatigue: int) -> tuple[int, int, int]:
    velocity_corr = int(-5 * accumulates_fatigue / 100)
    control_corr = int(-10 * accumulates_fatigue / 100)
    breaking_ball_corr = int(-5 * accumulates_fatigue / 100)

    return velocity_corr, control_corr, breaking_ball_corr


def batter_fatigue_correction(accumulates_fatigue: int) -> tuple[int, int, int]:
    meet_corr = int(-10 * accumulates_fatigue / 100)
    power_corr = int(-10 * accumulates_fatigue / 100)
    speed_corr = int(-10 * accumulates_fatigue / 100)

    return meet_corr, power_corr, speed_corr


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
    # チーム所属の全投手
    pitchers: list[Pitcher] = [
        player.pitcher
        for player in starting_lineup.team.players
        if player.pitcher is not None
    ]

    for pitcher in pitchers:
        barometer = pitcher.barometer

        # 回復力の参照
        recovery_code: str = (
            pitcher.ability.special_ability.common_special_ability.recovery
        )
        base_recover: float = float(RECOVERY_MAP.get(recovery_code, 15))

        # 本日の対打者数
        today_bf: int = pitcher.stats.game_bf

        if today_bf > 0:
            # 本日登板した投手
            # 打者1人あたり3.5ポイントのスタミナ消費
            pitch_load = today_bf * 3.5
            pitcher.fatugue_stamina += round(pitch_load)

            # 蓄積疲労の計算：投球負荷から回復力の一部を差し引いた値を加算
            fatigue_add = (pitch_load * 0.15) - (base_recover * 0.05)
            if fatigue_add > 0:
                barometer.accumulates_fatigue += round(fatigue_add)

        else:
            # 2. 本日登板しなかった投手（休養）
            # 減少体力の回復
            pitcher.fatugue_stamina -= round(base_recover)

            # 蓄積疲労の回復
            recovery_weight = 0.2 if pitcher.aptitude == "先" else 0.05
            recovered_fatigue = round(base_recover * recovery_weight)
            barometer.accumulates_fatigue -= max(1, recovered_fatigue)

        # 値の標準化（底打ち）とクリーンアップ
        pitcher.fatugue_stamina = max(0, pitcher.fatugue_stamina)
        barometer.accumulates_fatigue = max(0, barometer.accumulates_fatigue)

        # 当日打者数のリセット（次の試合へ向けてクリア）
        pitcher.stats.game_bf = 0


def _update_batter_fatigue(starting_lineup: StartingLineup) -> None:
    """野手の蓄積疲労の計算

    Args:
        starting_lineup (StartingLineup): チームのスタメン・出場選手情報
    """
    positions_map: dict[Batter, str] = starting_lineup.positions
    starter_set: set[Batter] = set(starting_lineup.lineup)

    # チーム所属の全野手
    batters: list[Batter] = [
        player.batter
        for player in starting_lineup.team.players
        if player.batter is not None
    ]

    for batter in batters:
        # 回復力の参照 (common_special_ability -> recovery)
        recovery_code: str = (
            batter.ability.special_ability.common_special_ability.recovery
        )
        base_recover: float = float(RECOVERY_MAP.get(recovery_code, 15))
        barometer = batter.barometer

        if batter in starter_set:
            # 出場野手：守備位置に応じた負荷計算
            pos: str = positions_map.get(batter, "")
            fatigue_weight: float = float(POS_FATIGUE_MAP.get(pos, 1.0))
            fatigue_add = fatigue_weight - (base_recover * 0.02)
            barometer.accumulates_fatigue += max(0, round(fatigue_add))
        else:
            # 不出場野手：回復
            recovered = round(base_recover * 0.1)
            barometer.accumulates_fatigue -= max(1, recovered)

        # 蓄積疲労の底打ち処理
        barometer.accumulates_fatigue = max(0, barometer.accumulates_fatigue)
