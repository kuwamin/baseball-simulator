"""特殊能力および能力補正計算ロジック"""

from __future__ import annotations

from baseball_simulator.common.const import (
    BATTER_RANK_MAP,
    PITCHER_LEFT_MAP,
    PITCHER_NOBI_MAP,
    PITCHER_RISP_MAP,
)
from baseball_simulator.data_model.data_model import Batter, Pitcher


def calculate_pitcher_special_ability(
    pitcher: Pitcher, batter: Batter, is_risp: bool
) -> tuple[int, int, int]:
    """投手の特殊能力（ピンチ、対左、ノビ）による能力補正値を計算する

    Args:
        pitcher (Player): 投手 Player インスタンス
        batter (Player): 打者 Player インスタンス
        is_risp (bool): 得点圏の場合 True

    Returns:
        tuple[int, int, int]: (球速補正, コントロール補正, 変化球補正)
    """
    p_special = pitcher.ability.special_ability
    b_info = batter.player_info

    velocity_corr = 0
    control_corr = 0
    breaking_ball_corr = 0

    # 対ピンチ (clutch_pitching)
    if is_risp:
        v, c, b = PITCHER_RISP_MAP.get(p_special.clutch_pitching, (0, 0, 0))
        velocity_corr += v
        control_corr += c
        breaking_ball_corr += b

    # 対左打者 (vs_left_batter)
    if b_info.dominant_hitting == "左":
        v, c, b = PITCHER_LEFT_MAP.get(p_special.vs_left_batter, (0, 0, 0))
        velocity_corr += v
        control_corr += c
        breaking_ball_corr += b

    # ノビ (fastball_life)
    v, c, b = PITCHER_NOBI_MAP.get(p_special.fastball_life, (0, 0, 0))
    velocity_corr += v
    control_corr += c
    breaking_ball_corr += b

    return velocity_corr, control_corr, breaking_ball_corr


def calculate_batter_special_ability(
    pitcher: Pitcher, batter: Batter, is_risp: bool
) -> tuple[int, int]:
    """打者の特殊能力（チャンス、対左）による能力補正値を計算する

    Args:
        pitcher (Player): 投手 Player インスタンス
        batter (Player): 打者 Player インスタンス
        is_risp (bool): 得点圏の場合 True

    Returns:
        tuple[int, int]: (ミート補正, パワー補正)
    """

    b_special = batter.ability.special_ability
    p_info = pitcher.player_info

    meet_corr = 0
    power_corr = 0

    # チャンス (clutch_batting)
    if is_risp:
        m, p = BATTER_RANK_MAP.get(b_special.clutch_batting, (0, 0))
        meet_corr += m
        power_corr += p

    # 対左投手 (vs_left_pitcher)
    if p_info.dominant_arm == "左":
        m, p = BATTER_RANK_MAP.get(b_special.vs_left_pitcher, (0, 0))
        meet_corr += m
        power_corr += p

    return meet_corr, power_corr
