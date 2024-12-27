from collections import defaultdict
from datetime import timedelta, datetime

import google


class ShopStatisticsDAO:
    @staticmethod
    def statistics_by_hour(conn: google.cloud.firestore_v1.client.Client, day: int, month: int, year: int):
        # Chuyển `date` và `time` thành `datetime` để dùng trong Firestore
        date_start = datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")
        date_end = datetime.strptime(f"{year}-{month}-{day} 23:59:59", "%Y-%m-%d %H:%M:%S")

        # Truy vấn Firestore với `where`
        results = (
            conn.collection("shop")
            .where("datetime", ">=", date_start)
            .where("datetime", "<=", date_end)
            .get()
        )

        # Dữ liệu kết quả
        hourly_data = defaultdict(lambda: {"total_customers_entering": 0, "total_customers_exiting": 0})
        for row in results:
            data = row.to_dict()
            # kiểu DatetimeWithNanoseconds
            datetime_value = data['datetime'] + timedelta(hours=7)  # chuyển sang UTC+7
            hour = datetime_value.hour
            hourly_data[hour]["total_customers_entering"] += data.get("customers_entering", 0)
            hourly_data[hour]["total_customers_exiting"] += data.get("customers_exiting", 0)

        return [
            {
                "hour": f"{hour}:00",
                "total_customers_entering": hourly_data[hour]["total_customers_entering"],
                "total_customers_exiting": hourly_data[hour]["total_customers_exiting"],
            }
            for hour in sorted(hourly_data.keys())
        ]

    @staticmethod
    def statistics_by_day(conn: google.cloud.firestore_v1.client.Client, month: int, year: int):
        # Tạo khoảng thời gian cho tháng được chỉ định
        start_date = datetime(year, month, 1, 0, 0, 0)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

        # Truy vấn Firestore
        results = (
            conn.collection("shop")
            .where("datetime", ">=", start_date)
            .where("datetime", "<=", end_date)
            .get()
        )

        # Lưu trữ dữ liệu theo ngày
        daily_data = defaultdict(lambda: {"total_customers_entering": 0, "total_customers_exiting": 0})

        # Xử lý từng bản ghi
        for row in results:
            data = row.to_dict()
            datetime_value = data["datetime"]

            day = datetime_value.day  # Lấy ngày
            daily_data[day]["total_customers_entering"] += data.get("customers_entering", 0)
            daily_data[day]["total_customers_exiting"] += data.get("customers_exiting", 0)

        # Định dạng kết quả
        return [
            {
                "day": day,
                "total_customers_entering": daily_data[day]["total_customers_entering"],
                "total_customers_exiting": daily_data[day]["total_customers_exiting"],
            }
            for day in sorted(daily_data.keys())
        ]

    @staticmethod
    def statistics_by_month(conn: google.cloud.firestore_v1.client.Client, year: int):
        # Xác định khoảng thời gian cho năm được chỉ định
        start_date = datetime(year, 1, 1, 0, 0, 0)  # Ngày đầu tiên của năm
        end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)  # Ngày cuối cùng của năm

        # Truy vấn Firestore để lấy dữ liệu trong khoảng thời gian
        results = (
            conn.collection("shop")
            .where("datetime", ">=", start_date)
            .where("datetime", "<=", end_date)
            .get()
        )

        # Lưu trữ dữ liệu theo tháng
        monthly_data = defaultdict(lambda: {"total_customers_entering": 0, "total_customers_exiting": 0})

        # Xử lý từng bản ghi
        for row in results:
            data = row.to_dict()
            datetime_value = data["datetime"]  # Giả định `datetime` là kiểu Timestamp hoặc datetime

            month = datetime_value.month  # Lấy tháng
            monthly_data[month]["total_customers_entering"] += data.get("customers_entering", 0)
            monthly_data[month]["total_customers_exiting"] += data.get("customers_exiting", 0)

        # Danh sách tháng (định dạng rút gọn)
        months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Sắp xếp và định dạng kết quả
        return [
            {
                "month": months[month],
                "total_customers_entering": monthly_data[month]["total_customers_entering"],
                "total_customers_exiting": monthly_data[month]["total_customers_exiting"],
            }
            for month in sorted(monthly_data.keys())
        ]

    @staticmethod
    def statistics_by_year(conn: google.cloud.firestore_v1.client.Client):
        # Truy vấn tất cả các bản ghi trong bộ sưu tập
        results = conn.collection("shop").get()

        # Lưu trữ dữ liệu theo năm
        yearly_data = defaultdict(lambda: {"total_customers_entering": 0, "total_customers_exiting": 0})

        # Xử lý từng bản ghi
        for row in results:
            data = row.to_dict()
            datetime_value = data["datetime"]  # Giả định `datetime` là kiểu Timestamp hoặc datetime

            year = datetime_value.year  # Lấy năm
            yearly_data[year]["total_customers_entering"] += data.get("customers_entering", 0)
            yearly_data[year]["total_customers_exiting"] += data.get("customers_exiting", 0)

        # Định dạng kết quả
        return [
            {
                "year": year,
                "total_customers_entering": yearly_data[year]["total_customers_entering"],
                "total_customers_exiting": yearly_data[year]["total_customers_exiting"],
            }
            for year in sorted(yearly_data.keys())
        ]

