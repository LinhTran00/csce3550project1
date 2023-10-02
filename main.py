from flask import Flask, request, jsonify
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import time
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Generate RSA key pair for the current key
current_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

current_public_key = current_private_key.public_key()

# Define Key IDs for the current and expired keys
current_key_id = "e68d2830-60c9-11ee-8c99-0242ac120002"

# Initialize an empty list for the JWKS
jwks = []

# Define the JWKS URL
jwks_url = (
    "http://localhost:8080/.well-known/jwks.json"  # Replace with your actual URL
)


# Function to generate the JWKS dynamically with only the current key
def generate_jwks():
    return jsonify(
        keys=[
            {
                "kid": current_key_id,  # Use the Key ID for the current key
                "alg": "RS256",
                "kty": "RSA",
                "use": "sig",
                "n": current_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
                .decode()
                .replace("\n", "")
                .encode(),
                "e": 65537,  # Exponent (usually a constant value)
            }
        ]
    )


# RESTful JWKS endpoint
@app.route('/.well-known/jwks.json', methods=['GET'])
def get_jwks():
    return generate_jwks()


# /auth endpoint with username and password in the request body
@app.route('/auth', methods=['POST'])
def authenticate():
    try:
        # Check if the "expired" query parameter is present
        if 'expired' in request.args:
            # Use the current key even for expired tokens
            private_key = current_private_key
            kid = current_key_id  # Use the Key ID for the current key
            exp = int(time.time()) - 3600  # Token expired 1 hour ago
        else:
            private_key = current_private_key
            kid = current_key_id  # Use the Key ID for the current key
            exp = int(time.time()) + 3600  # Token expires in 1 hour

        # Create a JWT payload with the specified expiration
        payload = {
            "username": "example_user",  # Replace with the actual username
            "exp": exp,
            "jwks_uri": jwks_url,  # Include the JWKS URL in the JWT header
        }

        # Set the Key ID (kid) in the JWT header
        headers = {"kid": kid}

        # Sign the JWT token with the selected private key
        token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)

        # Return the JWT token as a string
        return token

    except Exception as e:
        logging.error(f"Error in /auth endpoint: {str(e)}")
        return jsonify(error='An error occurred during token generation.'), 500


if __name__ == '__main__':
    app.run(port=8080)
