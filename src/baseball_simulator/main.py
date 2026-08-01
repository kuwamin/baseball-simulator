from pathlib import Path

from baseball_simulator.data_model.data_model import Team
from baseball_simulator.loader.load_excel import load_player_list_file
from baseball_simulator.writer.write_excel import export_stats_to_excel


def main() -> None:
    # パスの定義
    input_file_path = Path("data/input/player_list.xlsx")
    output_dir = Path("data/output")
    output_file_path = output_dir / "stats_list.xlsx"

    # Excelファイルの読み込み（型は dict[str, Team]）
    teams: dict[str, Team] = load_player_list_file(str(input_file_path))

    # 試合ロジック

    # Excelファイルの出力
    export_stats_to_excel(teams, str(output_file_path))


if __name__ == "__main__":
    main()
