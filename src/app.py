from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
import jwt
import requests
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

app = Flask(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "files")

KEYCLOAK_URL = "http://host.docker.internal:8081"
REALM = os.getenv("REALM", "VotHw")
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

def b64_to_int(data):
    return int.from_bytes(base64.urlsafe_b64decode(data + "=="), "big")

def get_public_key(token):
    try:
        jwks_response = requests.get(JWKS_URL)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()["keys"]
        
        unverified_header = jwt.get_unverified_header(token)
        if "kid" not in unverified_header:
            raise jwt.InvalidTokenError("Token header missing 'kid' field")
        
        kid = unverified_header["kid"]

        for key in jwks:
            if key["kid"] == kid:
                public_key = rsa.RSAPublicNumbers(
                    e=b64_to_int(key["e"]),
                    n=b64_to_int(key["n"])
                ).public_key(default_backend())
                
                return public_key

        raise jwt.InvalidTokenError("Public key not found in JWKS")
    except Exception as e:
        raise jwt.InvalidTokenError(f"Failed to fetch JWKS: {str(e)}")

def validate_token(token):
    public_key = get_public_key(token)
    return jwt.decode(token, public_key, algorithms=["RS256"], audience="account")

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        validate_token(token)

        file = request.files["file"]
        minio_client.put_object(MINIO_BUCKET, file.filename, file.stream, length=-1, part_size=10 * 1024 * 1024)

        return jsonify({"message": "File uploaded successfully", "file_name": file.filename}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        validate_token(token)

        response = minio_client.get_object(MINIO_BUCKET, file_id)
        return response.data, 200, {
            "Content-Disposition": f"attachment; filename={file_id}"
        }
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update/<file_id>", methods=["PUT"])
def update_file(file_id):
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        validate_token(token)
        
        file = request.files["file"]
        minio_client.put_object(MINIO_BUCKET, file_id, file.stream, length=-1, part_size=10 * 1024 * 1024)
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
        validate_token(token)

        minio_client.remove_object(MINIO_BUCKET, file_id)
        return jsonify({"message": "File deleted successfully", "file_name": file_id}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)