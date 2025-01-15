from flask import Flask, request, jsonify
import jwt.exceptions
import jwt.jws
import jwt.utils
from minio import Minio
from minio.error import S3Error
import jwt
import os

app = Flask(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "files")

JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")

minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        file = request.files["file"]
        minio_client.put_object(MINIO_BUCKET, file.filename, file.stream, length=-1, part_size=10*1024*1024)

        return jsonify({"message": "File uploaded successfully", "file_name": file.filename}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        response = minio_client.get_object(MINIO_BUCKET, file_id)
        return response.data, 200, {
            "Content-Disposition": f"attachment; filename={file_id}"
        }
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 404

@app.route("/update/<file_id>", methods=["PUT"])
def update_file(file_id):
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        file = request.files["file"]
        minio_client.put_object(
            MINIO_BUCKET, file_id, file.stream, length=-1, part_size=10*1024*1024
        )
        return jsonify({"message": "File updated successfully", "file_name": file_id}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        minio_client.remove_object(MINIO_BUCKET, file_id)
        return jsonify({"message": "File deleted successfully", "file_name": file_id}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)