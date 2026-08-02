from baseball_simulator.common.const import POSITION_WEIGHT
from baseball_simulator.data_model.data_model import Batter, Pitcher, Team
from baseball_simulator.data_model.game_model import StartingLineup


def build_starting_lineup(team: Team) -> StartingLineup:
    """チームデータと試合番号から StartingLineup オブジェクトを組み上げる"""
    starter_pitcher = decide_pitcher(team)
    starter_batters = decide_fielders(team)
    lineup, pos_map = decide_order(starter_batters)

    return StartingLineup(
        team=team,
        starter_pitcher=starter_pitcher,
        lineup=lineup,
        positions=pos_map,
    )


def decide_pitcher(team: Team) -> Pitcher:
    """残りのスタミナ（スタミナ - 蓄積疲労）が最も高い先発投手を決定する"""
    # チーム内の適性 "先" のPitcherを抽出
    starters: list[Pitcher] = [
        player.pitcher
        for player in team.players
        if player.pitcher is not None and player.pitcher.aptitude == "先"
    ]

    # 適性 "先" が不在の場合は全投手から選出
    if not starters:
        starters = [
            player.pitcher for player in team.players if player.pitcher is not None
        ]

    # 投手自体がいない場合、ValueError
    if not starters:
        raise ValueError(f"Team {team.team_name} has no available pitchers.")

    # 残りスタミナが最も高い選手を選出
    starter = max(starters, key=_get_remaining_stamina)

    return starter


def _get_remaining_stamina(pitcher: Pitcher) -> float:
    """減少スタミナを考慮して実効スタミナを算出する"""
    stamina = pitcher.ability.basic_ability.stamina
    fatigue_stamina = pitcher.fatugue_stamina

    return float(stamina - fatigue_stamina)


def decide_fielders(team: Team) -> list[tuple[str, Batter]]:
    """守備位置ごとに最適な野手（9名）を選出する"""

    # チーム内のBatterを抽出
    batters: list[Batter] = [
        player.batter for player in team.players if player.batter is not None
    ]
    selected_batters: list[tuple[str, Batter]] = []

    for pos, weight in POSITION_WEIGHT.items():
        pos_batters = [batter for batter in batters if batter.position == pos]
        # 該当ポジションの選手が残っていない場合は野手全員から選出
        if not pos_batters:
            pos_batters = batters

        best_batter = max(
            pos_batters,
            key=lambda batter: calculate_batter_score(batter, weight),
        )
        selected_batters.append((pos, best_batter))
        batters.remove(best_batter)

    # 指名打者 (指) の選出
    dh_batter = max(batters, key=lambda batter: calculate_batter_score(batter, 0.0))
    selected_batters.append(("指", dh_batter))

    return selected_batters


def calculate_batter_score(batter: Batter, position_weight: float) -> float:
    """野手の選出スコアを計算する"""

    ability = batter.ability.basic_ability
    # 総合打力 + 守備力（守備位置重み付き）
    batting_score = ability.meet * 1.0 + ability.power * 1.2 + ability.speed * 0.8
    fielding_score = (ability.fielding * 1.5 + ability.arm * 1.0) * position_weight
    base_score = batting_score + fielding_score

    # 疲労考慮ペナルティ
    fatigue_penalty = batter.barometer.accumulates_fatigue * 0.5
    batter_score = max(0.0, base_score - fatigue_penalty)

    return batter_score


def decide_order(
    starter_batters: list[tuple[str, Batter]],
) -> tuple[list[Batter], dict[Batter, str]]:
    """スタメン野手（9名）から 1〜9 番の打順リストと守備位置マップを作成する"""
    working_list = [batter for _, batter in starter_batters]
    pos_map = {batter: pos for pos, batter in starter_batters}

    lineup: list[Batter | None] = [None] * 9

    # 総合打力が高い上位6名と下位3名に分ける
    working_list.sort(key=_get_total_batting_skill, reverse=True)
    top_candidates = working_list[:6]
    bottom_candidates = working_list[6:]

    # 4番：最強パワー
    top_candidates.sort(key=_get_power, reverse=True)
    lineup[3] = top_candidates.pop(0)

    # 1番：最強走力
    top_candidates.sort(key=_get_speed, reverse=True)
    lineup[0] = top_candidates.pop(0)

    # 3番：総合打力
    top_candidates.sort(key=_get_total_batting_skill, reverse=True)
    lineup[2] = top_candidates.pop(0)

    # 2番：ミート
    top_candidates.sort(key=_get_meet, reverse=True)
    lineup[1] = top_candidates.pop(0)

    # 5〜6番：残りの上位候補 + 下位候補をパワー順
    remaining = top_candidates + bottom_candidates
    remaining.sort(key=_get_power, reverse=True)
    lineup[4] = remaining.pop(0)
    lineup[5] = remaining.pop(0)

    # 7〜9番：残りをミート順
    remaining.sort(key=_get_meet, reverse=True)
    lineup[6] = remaining.pop(0)
    lineup[7] = remaining.pop(0)
    lineup[8] = remaining.pop(0)

    # 型チェック用
    final_lineup = [b for b in lineup if b is not None]
    return final_lineup, pos_map


def _get_total_batting_skill(batter: Batter) -> int:
    ability = batter.ability.basic_ability
    return ability.meet + ability.power + ability.speed


def _get_power(batter: Batter) -> int:
    return batter.ability.basic_ability.power


def _get_speed(batter: Batter) -> int:
    return batter.ability.basic_ability.speed


def _get_meet(batter: Batter) -> int:
    return batter.ability.basic_ability.meet
