from db_main.car_repository import get_vehicle_stock_search

res = get_vehicle_stock_search(
    year=2025,
    month=10,
    sido_id=11,
    vehicle_kind="승용",
    limit=20
)

print(res)