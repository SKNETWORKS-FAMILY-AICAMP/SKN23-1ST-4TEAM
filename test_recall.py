from backend.db_main.recall_repository import (
    get_recall_list,
    get_recall_count_by_maker,
    get_recall_by_car_name,
    get_recall_monthly,
    get_recall_reason_count,
    calc_recall_growth_rate,
    get_top_makers,
    get_top_recall_reasons,
)


print("\n===== 최신 리콜 목록 (limit=5) =====")
rows = get_recall_list(5,0)
print(rows)


