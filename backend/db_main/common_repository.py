from backend.utils.db_utils import fetch_all_dict

def get_regions():
    """
    C001 - 시도 목록 조회
    Returns: list(dict) -> [{} sido_name}, ...]
    """
    query = """
        SELECT
            sido_name
        FROM dim_region_sido;
    """

    rows = fetch_all_dict(query)

    return [
        {
            "sido_name": row["sido_name"]
        }
        for row in rows
    ]

"""------------------------------------------------"""




def get_fuel_types():
    """
    D101 - 연료 기준정보 조회
    Returns: list(dict) — fuel_id, fuel_name, is_eco
    """
    query = """
        SELECT 
            fuel_id,
            fuel_name,
            is_eco
        FROM dim_fuel
        ORDER BY fuel_id;
    """

    rows = fetch_all_dict(query)

    # Decimal → int 변환 포함
    return [
        {
            "fuel_id": int(r["fuel_id"]),
            "fuel_name": r["fuel_name"],
            "is_eco": r["is_eco"]
        }
        for r in rows
    ]

"""------------------------------------------------"""



def get_sido_list():
    """
    D106 - 시도 목록 조회
    Returns: list(dict) — sido_name
    """
    query = """
        SELECT 
            sido_name
        FROM dim_region_sido
        ORDER BY sido_name;
    """

    rows = fetch_all_dict(query)

    return [
        {"sido_name": r["sido_name"]}
        for r in rows
    ]