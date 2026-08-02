from baseball_simulator.common.const import BATTER_CONDITION_MAP, PITCHER_CONDITION_MAP


def pitcher_condition_correction(condition: int) -> tuple[int, int, int]:
    """投手の調子による能力補正（絶好調:2 〜 絶不調:-2）"""
    velocity_corr = 0
    control_corr = 0
    breaking_ball_corr = 0

    # デフォルト値を 0 から (0, 0, 0) に修正
    v, c, b = PITCHER_CONDITION_MAP.get(condition, (0, 0, 0))
    velocity_corr += v
    control_corr += c
    breaking_ball_corr += b

    return velocity_corr, control_corr, breaking_ball_corr


def batter_condition_correction(condition: int) -> tuple[int, int]:
    """野手の調子による能力補正（絶好調:2 〜 絶不調:-2）"""
    meet_corr = 0
    power_corr = 0

    m, p = BATTER_CONDITION_MAP.get(condition, (0, 0))
    meet_corr += m
    power_corr += p

    return meet_corr, power_corr
