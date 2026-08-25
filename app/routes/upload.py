from flask import Blueprint, current_app, jsonify, render_template, request

from ml.dataset_loader import DatasetValidationError

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")


@upload_bp.route("/api/upload", methods=["POST"])
def api_upload():
    data_service = current_app.extensions["data_service"]

    if "file" not in request.files:
        return jsonify({"error": "No file was provided."}), 400

    file_storage = request.files["file"]

    try:
        preview = data_service.process_upload(file_storage)
    except DatasetValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        current_app.logger.exception("Upload processing failed")
        return jsonify({"error": "Unable to process the uploaded file."}), 500

    # Note: we report validation results without silently switching the
    # live dashboard dataset. Making an upload the "active" dataset for
    # forecasting is an explicit, separate action a user could add a
    # confirm step for; here we surface the preview for review first.
    return jsonify({"preview": preview})
