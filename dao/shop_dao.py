from datetime import datetime, timedelta

from firebase_admin import firestore
from dao.shop_statistics_dao import ShopStatisticsDAO
from model.database_connection import DatabaseConnection
from model.shop import Shop


def get_cursor():
    database = DatabaseConnection()
    conn = database.get_connection()
    return conn


class ShopDAO:
    @classmethod
    def get_all_info(cls):
        conn = get_cursor()
        try:
            results = conn.collection("shop").get()
            # Đóng gói dữ liệu vào list các object Shop
            shops = []
            for row in results:
                row = row.to_dict()
                shop = Shop(row['customers_entering'], row['customers_exiting'])
                # kiểu DatetimeWithNanoseconds
                datetime_value = row['datetime'] + timedelta(hours=7)  # chuyển sang UTC+7
                date = datetime_value.strftime(f'{datetime_value.year}-{datetime_value.month}-{datetime_value.day}')
                time = datetime_value.strftime(f'{datetime_value.hour}:{datetime_value.minute}:{datetime_value.second}')
                shop.set_date(date)
                shop.set_time(time)
                shops.append(shop.to_dict())
            return shops
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    @classmethod
    def add_info(cls, shop: Shop) -> bool:
        conn = get_cursor()
        try:
            data = {
                'customers_entering': shop.customers_entering,
                'customers_exiting': shop.customers_exiting,
                'datetime': firestore.SERVER_TIMESTAMP
            }
            conn.collection("shop").add(data)
            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    @classmethod
    def get_info_by_date_and_time(cls, date: str, time_mark: str):
        conn = get_cursor()
        time_from = None
        time_to = None

        if time_mark == '1':
            time_from = "06:00:00"
            time_to = "12:00:00"
        elif time_mark == '2':
            time_from = "12:00:00"
            time_to = "18:00:00"
        elif time_mark == '3':
            time_from = "18:00:00"
            time_to = "23:59:59"

        try:
            # Chuyển `date` và `time` thành `datetime` để dùng trong Firestore
            date_start = datetime.strptime(f"{date} {time_from}", "%Y-%m-%d %H:%M:%S")
            date_end = datetime.strptime(f"{date} {time_to}", "%Y-%m-%d %H:%M:%S")

            # Truy vấn Firestore với `where`
            results = (
                conn.collection("shop")
                .where("datetime", ">=", date_start - timedelta(hours=7))
                .where("datetime", "<=", date_end - timedelta(hours=7))
                .get()
            )

            # Đóng gói dữ liệu vào list các object Shop
            shops = []
            for row in results:
                row = row.to_dict()
                shop = Shop(row['customers_entering'], row['customers_exiting'])
                # kiểu DatetimeWithNanoseconds
                datetime_value = row['datetime'] + timedelta(hours=7)  # chuyển sang UTC+7
                date = datetime_value.strftime(f'{datetime_value.year}-{datetime_value.month}-{datetime_value.day}')
                time = datetime_value.strftime(f'{datetime_value.hour}:{datetime_value.minute}:{datetime_value.second}')
                shop.set_date(date)
                shop.set_time(time)
                shops.append(shop.to_dict())
            return shops  # Trả về danh sách các Shop
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    @classmethod
    def get_info_by_date(cls, date: str):
        conn = get_cursor()
        try:
            # Chuyển `date` và `time` thành `datetime` để dùng trong Firestore
            date_start = datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            date_end = datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S")

            # Truy vấn Firestore với `where`
            results = (
                conn.collection("shop")
                .where("datetime", ">=", date_start)
                .where("datetime", "<=", date_end)
                .get()
            )

            # Đóng gói dữ liệu vào list các object Shop
            shops = []
            for row in results:
                row = row.to_dict()
                shop = Shop(row['customers_entering'], row['customers_exiting'])
                # kiểu DatetimeWithNanoseconds
                datetime_value = row['datetime'] + timedelta(hours=7)  # chuyển sang UTC+7
                date = datetime_value.strftime(f'{datetime_value.year}-{datetime_value.month}-{datetime_value.day}')
                time = datetime_value.strftime(f'{datetime_value.hour}:{datetime_value.minute}:{datetime_value.second}')
                shop.set_date(date)
                shop.set_time(time)
                shops.append(shop.to_dict())
            return shops  # Trả về danh sách các Shop
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    @classmethod
    def get_info_by_day_month_year(cls, day: int, month: int, year: int):
        conn = get_cursor()
        try:
            # Câu lệnh SQL để lấy dữ liệu theo time
            if day is not None and month is not None and year is not None:
                return ShopStatisticsDAO.statistics_by_hour(conn, day, month, year)
            elif month is not None and year is not None:
                return ShopStatisticsDAO.statistics_by_day(conn, month, year)
            elif year is not None:
                return ShopStatisticsDAO.statistics_by_month(conn, year)
            else:
                return ShopStatisticsDAO.statistics_by_year(conn)
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False
