from baseball_simulator.data_model.data_model import Player, Team
from baseball_simulator.data_model.game_model import StartingLineup


def build_starting_lineup(team: Team) -> StartingLineup:
    """チームデータと試合番号から StartingLineup オブジェクトを組み上げる"""
    starter_pitcher = decide_pitcher(team)
    fielders = decide_fielders(team)
    lineup, pos_map = decide_order(fielders)

    return StartingLineup(
        team=team,
        starter_pitcher=starter_pitcher,
        lineup=lineup,
        positions=pos_map,
    )


def decide_pitcher(team: Team) -> Player:
    """残りのスタミナ（スタミナ - 蓄積疲労）が最も高い先発投手を決定する"""
    starters = [
        p for p in team.players if p.pitcher is not None and p.pitcher.aptitude == "先"
    ]
    if not starters:
        # 適性 "先" が不在の場合は全投手から選出
        starters = [p for p in team.players if p.pitcher is not None]

    if not starters:
        raise ValueError(f"Team {team.team_name} has no available pitchers.")

    # 残りスタミナが最も高い選手を選出
    return max(starters, key=_get_remaining_stamina)


def _get_remaining_stamina(p: Player) -> float:
    # mypy 対策: pitcher が None でないことを保証
    assert p.pitcher is not None
    stamina = p.pitcher.ability.basic_ability.stamina
    fatigue = p.barometer.accumulates_fatigue
    return stamina - fatigue


def decide_fielders(team: Team) -> list[tuple[str, Player]]:
    """守備位置ごとに最適な野手（9名）を選出する"""
    position_weights = {
        "捕": 1.0,
        "遊": 0.9,
        "二": 0.9,
        "中": 0.6,
        "三": 0.4,
        "右": 0.3,
        "左": 0.1,
        "一": 0.1,
    }

    candidates = [p for p in team.players if p.batter is not None]
    selected_players: list[tuple[str, Player]] = []

    for pos, weight in position_weights.items():
        pos_candidates = [
            p for p in candidates if p.batter is not None and p.batter.position == pos
        ]
        # 該当ポジションの選手が残っていない場合は野手全員から選出
        if not pos_candidates:
            pos_candidates = candidates

        best_player = max(
            pos_candidates,
            key=lambda p: calculate_score(p, weight),
        )
        selected_players.append((pos, best_player))
        candidates.remove(best_player)

    # 指名打者 (指) の選出
    dh_player = max(candidates, key=lambda p: calculate_score(p, 0.0))
    selected_players.append(("指", dh_player))

    return selected_players


def decide_order(
    fielders: list[tuple[str, Player]],
) -> tuple[list[Player], dict[Player, str]]:
    """スタメン野手（9名）から 1〜9 番の打順リストと守備位置マップを作成する"""
    working_list = [player for _, player in fielders]
    pos_map = {player: pos for pos, player in fielders}

    lineup: list[Player | None] = [None] * 9

    # 総合打力が高い上位6名と下位3名に分ける
    working_list.sort(key=_get_total_hit_skill, reverse=True)
    top_candidates = working_list[:6]
    bottom_candidates = working_list[6:]

    # 4番：最強パワー
    top_candidates.sort(key=_get_power, reverse=True)
    lineup[3] = top_candidates.pop(0)

    # 1番：最強走力
    top_candidates.sort(key=_get_speed, reverse=True)
    lineup[0] = top_candidates.pop(0)

    # 3番：総合打力
    top_candidates.sort(key=_get_total_hit_skill, reverse=True)
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
    final_lineup = [p for p in lineup if p is not None]
    return final_lineup, pos_map


def calculate_score(player: Player, position_weight: float) -> float:
    """野手の選出スコアを計算する"""
    if not player.batter:
        return 0.0

    b = player.batter.ability.basic_ability
    # 総合打力 + 守備力（守備位置重み付き）
    base_score = (b.meet * 1.0 + b.power * 1.2 + b.speed * 0.8) + (
        b.fielding * 1.5 + b.arm * 1.0
    ) * position_weight

    # 疲労考慮ペナルティ
    fatigue_penalty = player.barometer.accumulates_fatigue * 0.5
    base_score = max(0.0, base_score - fatigue_penalty)

    return base_score


def _get_power(p: Player) -> int:
    return p.batter.ability.basic_ability.power if p.batter else 0


def _get_speed(p: Player) -> int:
    return p.batter.ability.basic_ability.speed if p.batter else 0


def _get_meet(p: Player) -> int:
    return p.batter.ability.basic_ability.meet if p.batter else 0


def _get_total_hit_skill(p: Player) -> int:
    if not p.batter:
        return 0
    b = p.batter.ability.basic_ability
    return b.meet + b.power + b.speed
