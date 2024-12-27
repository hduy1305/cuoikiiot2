from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS

from dao.shop_dao import ShopDAO
from model.shop import Shop
from dotenv import load_dotenv

import threading
import time
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



load_dotenv()
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')

if not sender_email or not sender_password:
    raise ValueError("Sender email or password is missing. Please set environment variables.")


app = Flask(__name__)
CORS(app)
customer_in_store = 0
is_close = False
is_sending_emails = False
has_theft = False


# kiểm tra kết nối đến server
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/theft")
def theft_page():
    return render_template("theft.html")


@app.route("/monthly_statistics")
def statistic_by_month():
    return render_template("monthly_statistics.html")


# đẩy dữ liệu số lượng khách trong cửa hàng
@app.route("/send/customer_in_store", methods=["POST"])
def set_customer_in_store():
    global customer_in_store
    try:
        customer_in_store = int(request.values.get('customer_in_store'))
        return jsonify({"success": "Send successful.", "customer_in_store": customer_in_store})
    except ValueError:
        return jsonify({"error": "Wrong type of data."})


# lấy dữ liệu số lượng khách trong cửa hàng để hiển thị biểu đồ
@app.route("/get/customer_in_store")
def get_customer_in_store():
    return jsonify({"customer_in_store": customer_in_store})


# đẩy dữ liệu số lượng khách vào/ra cửa hàng
@app.route("/send/shop_info", methods=["POST"])
def add_shop_info():
    try:
        customers_entering = int(request.values.get('customers_entering'))
        customers_exiting = int(request.values.get('customers_exiting'))
        shop = Shop(customers_entering, customers_exiting)
        is_success = ShopDAO.add_info(shop)
        if is_success:
            return jsonify({"success": "Add successful."})
        else:
            return jsonify({"error": "Something was an error."})
    except ValueError:
        return jsonify({"error": "Wrong type of data."})


# lấy dữ liệu số lượng khách vào/ra cửa hàng để hiển thị biểu đồ
@app.route("/get/shop_info/", methods=["POST"])
def get_shop_info():
    date = request.values.get('date')  # date dạng yyyy-mm-dd
    time_mark = request.values.get('time_mark')
    result = None
    if date != 'null' and time_mark != 'null':
        result = ShopDAO.get_info_by_date_and_time(date, time_mark)
    elif date != 'null' and time_mark == 'null':
        result = ShopDAO.get_info_by_date(date)
    else:
        result = ShopDAO.get_all_info()

    return jsonify({"success": "Get data successful.", "result": result})


# gửi trạng thái đóng/mở cửa hàng đến server
@app.route("/send/store_open")
def set_store_open():
    global is_close
    is_close = False
    return jsonify({"success": "Send successful."})


@app.route("/send/store_close")
def set_store_close():
    global is_close
    is_close = True
    return jsonify({"success": "Send successful."})


# thống kê theo tháng
@app.route("/get/statistics", methods=["POST"])
def get_monthly_statistics():
    day = request.values.get('day')
    month = request.values.get('month')
    year = request.values.get('year')

    try:
        day = int(day)
    except Exception:
        day = None

    try:
        month = int(month)
    except Exception:
        month = None

    try:
        year = int(year)
    except Exception:
        year = None

    result = ShopDAO.get_info_by_day_month_year(day, month, year)

    return jsonify({"success": "Get data successful.", "result": result})


@app.route("/get/store_state")
def get_store_state():
    global is_close
    return jsonify({"is_close": is_close})


# Cập nhật thông tin trộm (theft)
@app.route("/update_theft", methods=["POST"])
def update_theft():
    global is_sending_emails, is_close, has_theft
    data = request.values.get("hasTheft")
    if data == "1":
        has_theft = True
    else:
        has_theft = False

    if has_theft and not is_sending_emails:
        is_close = True  # Cập nhật trạng thái cửa hàng
        with open('./templates/email.txt', 'r') as f:
            email_list = f.read().splitlines()

        is_sending_emails = True
        threading.Thread(target=send_warning_emails).start()
        return jsonify({"success": "Theft detected, starting to send warning emails."})
    elif not has_theft and is_sending_emails:
        is_close = False  # Cập nhật trạng thái cửa hàng
        is_sending_emails = False
        return jsonify({"success": "Theft status is clear, email sending stopped."})
    else:
        return jsonify({"error": "Invalid theft status or already in requested state."})


@app.route('/check_theft')
def check_theft():
    global has_theft
    return jsonify({'has_theft': has_theft})


# kt email có đang gửi ko
@app.route('/is_sending_emails')
def check_sending_emails():
    return jsonify({'is_sending_emails': is_sending_emails})


def send_warning_emails():
    while is_sending_emails:
        send_email()
        time.sleep(120)  # Gửi email mỗi 2 phút



# Gui bao cao
@app.route('/send_report')
def send_report():
    data = ShopDAO.get_info_by_day_month_year(year=datetime.now().year,day=None, month=None)
    print(data)
    
    with open('./templates/email.txt', 'r') as f:
        email_list = f.read().splitlines()

    # Đọc nội dung từ file HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Báo cáo Khách Hàng Theo Tháng</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 20px;
            }
            h2 {
                text-align: center;
                color: #333;
            }
            .month-container {
                margin: 15px 0;
            }
            .month {
                font-weight: bold;
                color: #2f2f2f;
            }
            .bar {
                display: inline-block;
                height: 30px;
                background-color: #2f2f2f;
                vertical-align: middle;
                margin-right: 10px;
                border-radius: 5px;
            }
            .bar-text {
                display: inline-block;
                vertical-align: middle;
                color: #ffffff;
                font-weight: bold;
            }
        </style>
    </head>
    <body>

    <h2>Monthly Customer Statistics</h2>
    """
    for d in data:

        html_content = html_content +  f"""<div class="month-container">
            <span class="month">{d['month']}:</span>
            <div class="bar" style="width: {d['total_customers_entering']/10}px;"></div>
            <span class="bar-text" style="color: #000;">{d['total_customers_entering']} customers</span>
        </div>
        """

    html_content = html_content + """</body>
    </html>

    """
    
    # Tạo kết nối tới server SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    for email in email_list:
        # Tạo email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Warning: Theft Detected"
        msg["From"] = sender_email
        msg["To"] = email

        # Đính kèm nội dung HTML
        msg.attach(MIMEText(html_content, "html"))

        try:
            # Kết nối tới SMTP server và gửi email
            server.sendmail(sender_email, email, msg.as_string())
            print("Email đã được gửi thành công!")
        except Exception as e:
            print("Đã xảy ra lỗi khi gửi email:", str(e))
    server.quit()
    return Response(status=200)


# Kiểm tra email và dừng gửi email nếu có trong danh sách
@app.route("/check_email", methods=["POST"])
def check_email():
    global is_sending_emails, is_close
    data = request.get_json()
    email_to_check = data.get("email")
    with open('./templates/email.txt', 'r') as f:
        email_list = f.read().splitlines()
    if email_to_check in email_list:
        is_sending_emails = False
        is_close = False  # Cập nhật trạng thái an toàn
        return jsonify({"success": "Email found, stopped sending warning emails."})
    else:
        return jsonify({"error": "Email not found."})

def send_email():
    with open('./templates/email.txt', 'r') as f:
        email_list = f.read().splitlines()

    # Đọc nội dung từ file HTML
    html_file_path = "./templates/email_content.html"
    try:
        with open(html_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
    except Exception as e:
        print("Lỗi khi đọc file HTML:", str(e))
        return

    # Tạo kết nối tới server SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    for email in email_list:
        # Tạo email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Warning: Theft Detected"
        msg["From"] = sender_email
        msg["To"] = email

        # Đính kèm nội dung HTML
        msg.attach(MIMEText(html_content, "html"))

        try:
            # Kết nối tới SMTP server và gửi email
            server.sendmail(sender_email, email, msg.as_string())
            print("Email đã được gửi thành công!")
        except Exception as e:
            print("Đã xảy ra lỗi khi gửi email:", str(e))
    server.quit()
   

if __name__ == "__main__":
    app.run(
        debug=False,
        # host='0.0.0.0',
        port=5000
    )

