import os
from io import BytesIO
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from audio_analysis.acr_api_requests import identify_audio, upload_audio
from Invites.invites import fetch_user_invites, process_invite, insert_user_invite
from Workspaces.workspaces import *
from Users.users import fetch_users, add_user, fetch_user_workspaces
from audiokey_api.audiokey import add_audio_key
from login.get_logged_in import fetch_user_details

app = Flask(__name__, template_folder='testflask/templates')
CORS(app)


# @app.route("/")
# def homeDummy():
#     return 'Hello'
#
#
# @app.route("/encryptFile", methods=['POST'])
# def post_encrypted_file():
#     return encrypt_file(request.files['file'])
#
#
#
# @app.route("/decryptFile", methods=['GET'])
# def download_decrypted_file():
#     return decrypt_file(request.json)
#
#
# @app.route('/api/login', methods=['GET'])
# def login():
#     username = request.json['username']
#     password = request.json['password']
#     res = fetch_user_details(username, password)
#     res_json = jsonify(res)
#
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 200
#
#
@app.route("/api/users")
def get_users():
    res = fetch_users()
    res_json = jsonify(res)

    if ("error" in res):
        return res_json, 404
    else:
        return res_json, 200

#
# @app.route("/api/users", methods=['POST'])
# def post_user():
#     username = request.json['username']
#     password = request.json['password']
#     res = add_user(username, password)
#     res_json = jsonify(res)
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 201
#
#
# @app.route('/api/users/<username>', methods=["GET"])
# def get_user_workspaces(username):
#     res = fetch_user_workspaces(username)
#     res_json = jsonify(res)
#
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 200
#
#
# @app.route("/api/deleteUser", methods=['DELETE'])
# def delete_user():
#     if (not request.json) | ('username' not in request.json) | ('admin_username' not in request.json) | (
#             'workspace_name' not in request.json):
#         abort(400)
#
#     res = delete_user_from_workspace(request.json)
#     res_json = jsonify(res)
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 204
#
#
# @app.route("/api/invites", methods=["POST"])
# def invite_user():
#     if (not request.json) | ('username' not in request.json) \
#             | ('workspace' not in request.json) | ('invitedBy' not in request.json):
#         abort(400)
#
#     res = insert_user_invite(request.json)
#     res_json = jsonify(res)
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 201
#
#
# @app.route("/api/invites/<username>", methods=["GET"])
# def get_user_invites(username):
#     res = fetch_user_invites(username)
#     res_json = jsonify(res)
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 200
#
#
# @app.route("/api/invites/<username>", methods=["POST"])
# def update_invite(username):
#     if (not request.json) | ('accept' not in request.json) | ('workspace' not in request.json):
#         abort(400)
#
#     res = process_invite(username, request.json)
#     res_json = jsonify(res);
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 201
#
#
# @app.route('/api/workspaces', methods=['POST'])
# def handle_create_workspace():
#     if (not request.json) | ('name' not in request.json) | ('admin' not in request.json):
#         abort(400)
#     else:
#         if ('users' in request.json):
#             res = create_workspace_with_users(request.json)
#         else:
#             res = create_workspace_only(request.json)
#
#         res_json = jsonify(res);
#         if ("error" in res):
#             return res_json, 404
#         else:
#             return res_json, 201
#         return jsonify(res_json);
#
#
# @app.route("/api/workspaces", methods=["DELETE"])
# def handle_delete_workspace():
#     if (not request.json) | ('workspace' not in request.json) | ('deleted_by' not in request.json):
#         abort(400)
#
#     res = delete_workspace(request.json)
#     res_json = jsonify(res)
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 204
#
#
# @app.route("/api/workspaces/<name>", methods=["GET"])
# def get_workspace_file(name):
#     res = fetch_workspace_files(name)
#     res_json = jsonify(res);
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 200
#
#
# @app.route("/api/workspaces/<workspace_name>", methods=["PUT"])
# def handle_update_workspace(workspace_name):
#     if (not request.json) | ('username' not in request.json) \
#             | ('admin_username' not in request.json) | ('make_admin' not in request.json):
#         abort(400)
#
#     res = update_admin(workspace_name, request.json)
#     res_json = jsonify(res);
#     if ("error" in res):
#         return res_json, 404
#     else:
#         return res_json, 201
#
#     print(res)
#     res_json = {'workspace_admin_updated': res}
#     if (res == False): res_json['error'] = 'Could not update workspace. ' \
#                                            'Check admin user is an admin'
#
#     return jsonify(res_json);
#
#
# @app.route("/api/audiokey", methods=["POST"])
# def post_audio_key():
#     if (not request.files) | ("session_id" not in request.values) | ("filename" not in request.values):
#         abort(400)
#
#     file = request.files["file"].read()
#     audio_file_copy1 = BytesIO(file)
#     audio_file_copy2 = BytesIO(file)
#     sample_bytes = len(file)
#     session_id = request.values.get("session_id")
#     file_name = request.values.get("filename")
#     acr_response = identify_audio(audio_file_copy1, sample_bytes)
#     if acr_response["status"]["msg"] == 'No result':
#         acr_upload_response = upload_audio(audio_file_copy2, file_name, session_id)
#         add_audio_key(acr_upload_response["acr_id"], session_id)
#         return jsonify({"notRecognised": True})
#     if 'custom_files' in acr_response["metadata"].keys():
#         return jsonify({"fileError": True})
#     if acr_response["status"]["msg"] == 'Success':
#         add_audio_key(acr_response["metadata"]["music"][0]["acrid"], session_id)
#         return jsonify({"title": acr_response["metadata"]["music"][0]["title"],
#                         "artist": acr_response["metadata"]["music"][0]["artists"][0]["name"]})
#
#     return jsonify('Error check')


if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run()
