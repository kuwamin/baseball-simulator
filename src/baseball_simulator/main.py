from pathlib import Path

from baseball_simulator.common.const import OPPOSITE_TEAM_LIST, TOTAL_GAME_NUMBER
from baseball_simulator.data_model.data_model import Team
from baseball_simulator.game.game import play_game
from baseball_simulator.io.load_excel import load_player_list_file
from baseball_simulator.io.write_excel import export_stats_to_excel


def main() -> None:
    # パスの定義
    input_file_path = Path("data/input/player_list.xlsx")
    output_dir = Path("data/output")
    output_file_path = output_dir / "stats_list.xlsx"

    # 出力先ディレクトリが存在しない場合は作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # Excelファイルの読み込み（型は dict[str, Team]）
    teams: dict[str, Team] = load_player_list_file(str(input_file_path))

    # 試合ロジック（シーズンペナント回し）
    for i in range(TOTAL_GAME_NUMBER):
        game_number = i + 1

        ## 対戦カード決定
        team_1 = teams[OPPOSITE_TEAM_LIST[i % 5]]
        team_2 = teams["Hawks"]

        ## 1試合実行
        play_game(team_1, team_2, game_number)

    # 成績結果をExcelへ出力
    export_stats_to_excel(teams, str(output_file_path))


if __name__ == "__main__":
    main()
