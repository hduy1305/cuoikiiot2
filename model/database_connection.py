import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client


class DatabaseConnection:
    _connection = None

    def __init__(self):
        # Đường dẫn đến tệp JSON
        json_path = "freeshop-3157a-firebase-adminsdk-1weix-4e5281752f.json"

        # Khởi tạo Firebase nếu chưa khởi tạo
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(json_path)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized successfully!")
            except FileNotFoundError:
                raise FileNotFoundError(f"Firebase configuration file not found at {json_path}")
            except Exception as e:
                raise Exception(f"Failed to initialize Firebase: {e}")

        # Thiết lập kết nối Firestore
        if DatabaseConnection._connection is None:
            try:
                DatabaseConnection._connection = firestore.client()
                print("Database connection established!")
            except Exception as e:
                raise Exception(f"Failed to connect to Firestore: {e}")

    @staticmethod
    def get_connection() -> Client:
        if DatabaseConnection._connection:
            return DatabaseConnection._connection
        else:
            raise Exception("Database connection not established!")


if __name__ == '__main__':
    try:
        # Khởi tạo kết nối tới Firestore
        db = DatabaseConnection()

        # Truy vấn dữ liệu từ collection 'shop'
        ref = db.get_connection().collection('shop')
        docs = ref.stream()

        # Hiển thị kết quả
        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')
    except Exception as e:
        print(f"Error: {e}")
