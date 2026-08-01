from baseball_simulator.data_model.data_model import Player, Team
from baseball_simulator.data_model.game_model import StartingLineup


def build_starting_lineup(
    team: Team, game_number: int, is_fatigue_considered: bool = True
) -> StartingLineup:
    """チームデータと試合番号から StartingLineup オブジェクトを組み上げる"""
    starter_pitcher = decide_pitcher(team, game_number)
    fielders = decide_fielders(team, is_fatigue_considered)
    lineup, pos_map = decide_order(fielders)

    return StartingLineup(
        team=team,
        starter_pitcher=starter_pitcher,
        lineup=lineup,
        positions=pos_map,
    )


def decide_pitcher(team: Team, game_number: int) -> Player:
    """ローテーションと疲労に基づき、試合の先発投手を決定する"""
    # 投手データがあり、適性が "先" の Player を抽出
    starters = [
        p for p in team.players if p.pitcher is not None and p.pitcher.aptitude == "先"
    ]
    if not starters:
        # 適性 "先" が不在の場合は全投手から選出
        starters = [p for p in team.players if p.pitcher is not None]

    num_starters = len(starters)
    start_idx = (game_number - 1) % num_starters

    for i in range(num_starters):
        current_idx = (start_idx + i) % num_starters
        candidate = starters[current_idx]

        # mypy 対策: pitcher が None でないことを確定させる
        assert candidate.pitcher is not None
        stamina = candidate.pitcher.ability.basic_ability.stamina
        fatigue = candidate.barometer.accumulates_fatigue

        # 疲労がスタミナの30%未満（残りスタミナ70%以上）なら採用
        if fatigue < (stamina * 0.30):
            return candidate

    return starters[start_idx]


def decide_fielders(
    team: Team, is_fatigue_considered: bool = True
) -> list[tuple[str, Player]]:
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
        # mypy 対策: batter が None でないことをガード
        pos_candidates = [
            p for p in candidates if p.batter is not None and p.batter.position == pos
        ]
        # 該当ポジションの選手が残っていない場合は野手全員から選出
        if not pos_candidates:
            pos_candidates = candidates

        best_player = max(
            pos_candidates,
            key=lambda p: calculate_score(p, weight, is_fatigue_considered),
        )
        selected_players.append((pos, best_player))
        candidates.remove(best_player)

    # 指名打者 (指) の選出（守備重み 0）
    dh_player = max(
        candidates, key=lambda p: calculate_score(p, 0.0, is_fatigue_considered)
    )
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

    # 型チェック用（全て Player で埋まっていることを確定させる）
    final_lineup = [p for p in lineup if p is not None]
    return final_lineup, pos_map


def calculate_score(
    player: Player, position_weight: float, is_fatigue_considered: bool
) -> float:
    """野手の選出スコアを計算する"""
    if not player.batter:
        return 0.0

    b = player.batter.ability.basic_ability
    # 総合打力 + 守備力（守備位置重み付き）
    base_score = (b.meet * 1.0 + b.power * 1.2 + b.speed * 0.8) + (
        b.fielding * 1.5 + b.arm * 1.0
    ) * position_weight

    # 疲労考慮ペナルティ
    if is_fatigue_considered and player.barometer:
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
