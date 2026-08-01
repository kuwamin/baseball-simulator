"""試合前後の疲労度・コンディション更新ロジック"""

from __future__ import annotations

from baseball_simulator.common.const import POS_FATIGUE_MAP, RECOVERY_MAP
from baseball_simulator.data_model.data_model import Player
from baseball_simulator.data_model.game_model import GameState, StartingLineup


def pitcher_condition_correction(condition: int) -> dict[str, float]:
    """投手の調子による能力補正（絶好調:2 〜 絶不調:-2）"""
    return {
        "velocity": condition * 1.0,
        "control": condition * 3.0,
        "breaking_ball": condition * 0.5,
    }


def batter_condition_correction(condition: int) -> dict[str, float]:
    """野手の調子による能力補正（絶好調:2 〜 絶不調:-2）"""
    return {
        "meet": condition * 3.0,
        "power": condition * 3.0,
    }


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

    # 実際に登板した投手（打者対戦数 bf > 0 の選手）
    played_pitchers: list[Player] = [
        p for p in team_pitchers if p.pitcher is not None and p.pitcher.stats.bf > 0
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

        if p in played_pitchers:
            # 登板した投手：打者数に応じた負荷
            pitch_load: float = float(pitcher_obj.stats.bf * 4)

            pitcher_obj.fatugue_stamina += int(pitch_load)
            barometer.accumulates_fatigue += int(
                (pitch_load * 0.2) - (base_recover * 0.01)
            )
        else:
            # 登板しなかった投手：回復
            pitcher_obj.fatugue_stamina = max(
                0, pitcher_obj.fatugue_stamina - int(base_recover)
            )

            # 先発起用かどうかで回復量を分岐
            is_starter: bool = p is starting_lineup.starter_pitcher
            recovery_weight: float = 0.2 if is_starter else 0.02
            barometer.accumulates_fatigue -= int(base_recover * recovery_weight)

        # 蓄積疲労の底打ち処理
        barometer.accumulates_fatigue = max(0, barometer.accumulates_fatigue)


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
            barometer.accumulates_fatigue += int(fatigue_weight - (base_recover * 0.01))
        else:
            # 不出場野手：回復
            barometer.accumulates_fatigue -= int(base_recover * 0.05)

        # 蓄積疲労の底打ち処理
        barometer.accumulates_fatigue = max(0, barometer.accumulates_fatigue)
