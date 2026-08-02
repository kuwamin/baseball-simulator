from baseball_simulator.data_model.data_model import Batter
from baseball_simulator.data_model.game_model import Bases
from baseball_simulator.game.at_bat_rules import AtBatResult


def advance_runners(
    result: AtBatResult,
    batter: Batter,
    bases: Bases,
) -> int:
    """
    打席結果と打者に応じて走者を移動させ、生還した人数（得点/打点）を返す。
    """
    runs = 0

    if result == AtBatResult.WALK:
        runs = _advance_walk(batter, bases)
    elif result == AtBatResult.SINGLE:
        runs = _advance_single(batter, bases)
    elif result == AtBatResult.DOUBLE:
        runs = _advance_double(batter, bases)
    elif result == AtBatResult.TRIPLE:
        runs = _advance_triple(batter, bases)
    elif result == AtBatResult.HOME_RUN:
        runs = _advance_home_run(batter, bases)

    return runs


def _advance_walk(batter: Batter, bases: Bases) -> int:
    """四球（フォアボール）：押し出しのみ進塁"""
    runs = 0
    if bases.first is not None:
        if bases.second is not None:
            if bases.third is not None:
                # 満塁フォアボール（押し出し）
                runs += 1
            bases.third = bases.second
        bases.second = bases.first

    bases.first = batter
    return runs


def _advance_single(batter: Batter, bases: Bases) -> int:
    """単打：走者は基本的に1ベース進塁"""
    runs = 0
    if bases.third is not None:
        runs += 1
        bases.third = None

    bases.third = bases.second
    bases.second = bases.first
    bases.first = batter
    return runs


def _advance_double(batter: Batter, bases: Bases) -> int:
    """二塁打：走者は基本的に2ベース進塁"""
    runs = 0
    if bases.third is not None:
        runs += 1
        bases.third = None

    if bases.second is not None:
        runs += 1
        bases.second = None

    bases.third = bases.first
    bases.second = batter
    bases.first = None
    return runs


def _advance_triple(batter: Batter, bases: Bases) -> int:
    """三塁打：全走者生還、打者は三塁へ"""
    runs = 0
    for runner in (bases.first, bases.second, bases.third):
        if runner is not None:
            runs += 1

    bases.first = None
    bases.second = None
    bases.third = batter
    return runs


def _advance_home_run(batter: Batter, bases: Bases) -> int:
    """本塁打：全走者＋打者自身が全員生還"""
    runs = 1  # 打者自身の得点
    for runner in (bases.first, bases.second, bases.third):
        if runner is not None:
            runs += 1

    bases.first = None
    bases.second = None
    bases.third = None
    return runs
