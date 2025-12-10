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
rows = get_recall_list(5,0,"해외")
print(rows)

print("\n===== 제조사별 리콜 건수 =====")
df_maker = get_recall_count_by_maker()
print(df_maker)


print("\n===== 차량명별 리콜 건수 =====")
df_car = get_recall_by_car_name()
print(df_car)


print("\n===== 월별 리콜 건수 =====")
df_month = get_recall_monthly(1,0)
print(df_month)


print("\n===== 리콜 사유별 통계 =====")
df_reason = get_recall_reason_count()
print(df_reason)


print("\n===== 리콜 증가율 계산 =====")
df_growth = calc_recall_growth_rate(df_month.copy())
print(df_growth)


print("\n===== TOP 5 제조사 =====")
print(get_top_makers(df_maker, n=5))


print("\n===== TOP 5 리콜 사유 =====")
print(get_top_recall_reasons(df_reason, n=5))