import secrets
from typing import Any
from database import DatabaseAgent
from itsdangerous import URLSafeSerializer, BadSignature
from flask import Flask, request, make_response, jsonify, current_app
from flask_cors import CORS #added by paul
import json

app = Flask(__name__)
CORS(app, supports_credentials=True) #added by paul
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
agent = DatabaseAgent("database.json")


@app.route("/api/login", methods=['POST'])
def login():
	""" User Login Authentication, pass argument in request body in JSON format. """
	# parse the request parameter
	data = request.get_json(silent=True)
	if not data: return jsonify({"status": "Invalid Format, Expected JSON."}), 400
	username = data.get("user_id")
	password = data.get("password")

	# attempt to login with the database agent
	if not agent.verify_user(username, password):
		return jsonify({"status": "Invalid Login Credential."}), 401

	# verification passed, give out session key
	agent.terminate_all_sessions(username)
	token, expire = agent.create_session(username)

	# set the CYK authentication token
	response = make_response({"status": "Login Success."}, 200)
	serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
	signed_token = serializer.dumps({
		"user_id": username,
		"token": token
	})

	# set the CYK authentication token to client's browser
	response.set_cookie(
		key = "cyk_token",
		value = signed_token,
		expires = expire,
		httponly = True,
		secure = True,
		samesite = "Strict"
	)
	return response


@app.route("/api/logout", methods=['POST'])
def logout():
	""" Logout the current user """
	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# logout user
		if agent.terminate_session(user_id, token):
			return jsonify({"status": "Logout Success."}), 200
		else:
			return jsonify({"status": "Logout Failed."}), 403

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception:
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/register", methods=['POST'])
def register():
	""" Register a new user on site """
	# parse the request parameter
	data = request.get_json(silent=True)
	if not data: return jsonify({"status": "Invalid Format, Expected JSON."}), 400
	email = data.get("email")
	username = data.get("user_id")
	password = data.get("password")

	# proceed on the user registration
	if agent.register_user(username, email, password):
		return jsonify({"status": "Register Success."}), 200
	else: 
		return jsonify({"status": "Register Failed."}), 409


@app.route("/api/folders", methods=['GET'])
def get_folders():
	""" Receive the user's chats and folders """
	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# verify whether the token is valid
		if not agent.verify_session(user_id, token):
			return jsonify({"status": "Invalid Access Token."}), 403

		# receive the user folder if token is valid
		folders = agent.get_folders(user_id)
		return jsonify(folders), 200

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception:
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/organize", methods=['POST'])
def organize_chat():
	""" Organize the chat into a specifc folder """
	# parse the request parameter
	data = request.get_json(silent=True)
	if not data: return jsonify({"status": "Invalid Format, Expected JSON."}), 400
	chat_id = data.get("chat_id")
	folder = data.get("folder")

	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# verify whether the token is valid
		if not agent.verify_session(user_id, token):
			return jsonify({"status": "Invalid Access Token."}), 403

		# organize chat into target folder
		if agent.organize_chat(chat_id, folder):
			return jsonify({"status": "Organize Success."}), 200
		else:
			return jsonify({"status": "Organize Failed."}), 404

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception as ex:
		print(ex)
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/new_chat", methods=['POST'])
def new_chat():
	""" Create a new chat for the logged in user """
	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# verify whether the token is valid
		if not agent.verify_session(user_id, token):
			return jsonify({"status": "Invalid Access Token."}), 403

		# create a new chat for the user
		chat_id = agent.create_chat(user_id)
		return jsonify({"chat_id": chat_id}), 200

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception as ex:
		print(ex)
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/chat", methods=['GET'])
def get_chat():
	""" Receive the chat history of a specific chat, pass argument as: /api/chat?id=<UUID-V4> """
	# parse the request parameter
	chat_id = request.args.get("id")
	if not chat_id: return jsonify({"error": "Missing chat id parameter"}), 400

	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# verify whether the token is valid
		if not agent.verify_session(user_id, token):
			return jsonify({"status": "Invalid Access Token."}), 403

		# retrieve chat information
		chat_info = agent.get_chat_history(chat_id)
		if not chat_info: return jsonify({"status": "Invalid Chat ID"}), 400
		return jsonify(chat_info), 200

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception:
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/chat", methods=['POST'])
def log_chat():
	""" Log a message in the chat, pass argument in request body in JSON format. """
	# parse the request parameter
	data = request.get_json(silent=True)
	if not data: return jsonify({"status": "Invalid Format, Expected JSON."}), 400
	chat_id = data.get("chat_id")
	sender = data.get("sender")
	message = data.get("message")

	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# verify whether the token is valid
		if not agent.verify_session(user_id, token):
			return jsonify({"status": "Invalid Access Token."}), 403

		# log the entry in database
		if agent.log_chat(chat_id, sender, message):
			return jsonify({"status": "Log Success."}), 200
		else:
			return jsonify({"status": "Log Failed."}), 404

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception:
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/chat", methods=['DELETE'])
def delete_chat():
	""" Delete a specific chat_id, pass argument in request body in JSON format. """
	# parse the request parameter
	data = request.get_json(silent=True)
	if not data: return jsonify({"status": "Invalid Format, Expected JSON."}), 400
	chat_id = data.get("chat_id")

	try:
		# extract the authentication token
		cookie = request.cookies.get("cyk_token")
		serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
		token = serializer.loads(cookie)
		user_id = token.get("user_id")
		token = token.get("token")

		# verify whether the token is valid
		if not agent.verify_session(user_id, token):
			return jsonify({"status": "Invalid Access Token."}), 403

		# delete the chat
		if agent.delete_chat(chat_id):
			return jsonify({"status": "Deletion Success."}), 200
		else:
			return jsonify({"status": "Deletion Failed."}), 404

	except BadSignature:
		return jsonify({"status": "Tampered or Invalid Signature in Token."}), 401

	except Exception:
		return jsonify({"status": "Unexpected Error while Verifying Token."}), 400


@app.route("/api/delete-user", methods=["DELETE"])
def delete_user():
    data = request.get_json(silent=True)
    if not data or "user_id" not in data:
        return jsonify({"status": "Invalid Format, expected user_id in JSON."}), 400

    user_to_delete = data["user_id"]

    try:
        with open("database.json", "r") as f:
            db = json.load(f)

        users = db.get("users", {})
        user_found = None

        # Find the matching user entry
        for key, user in users.items():
            if user.get("user_id") == user_to_delete:
                user_found = key
                break

        if user_found is None:
            return jsonify({"status": "User not found."}), 404

        # Delete user entry
        del db["users"][user_found]

        # Delete associated sessions
        db["sessions"] = {k: v for k, v in db.get("sessions", {}).items() if v.get("user_id") != user_to_delete}

        # Delete chat folders
        db["chat_folders"] = {k: v for k, v in db.get("chat_folders", {}).items() if v.get("user_id") != user_to_delete}

        # Delete chat logs
        db["chat_logs"] = {k: v for k, v in db.get("chat_logs", {}).items() if v.get("user_id") != user_to_delete}

        with open("database.json", "w") as f:
            json.dump(db, f, indent=2)

        return jsonify({"status": "User deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": f"Error occurred: {str(e)}"}), 500



if __name__ == "__main__":
	app.run(port=8888)
