from flask import Blueprint, request, jsonify
import pandas as pd
import requests
from app.helpers import validate_excel_file, upload_image_to_storage, upload_document_to_firestore, validate_row, REQUIRED_COLUMNS
from app.auth.authMiddleware import verify_token
from app.auth.authorization import authorize

room_service_blueprint = Blueprint('room_service', __name__)

@room_service_blueprint.route('/upload_excel', methods=['POST'])
@verify_token
@authorize(['manager'])
def upload_excel():
    try:
        org_id = request.form.get('orgId')
        menu_id = request.form.get('menuId')

        if not org_id or not menu_id:
            return jsonify({"error": "Missing required parameters 'orgId' or 'menuId'."}), 400

        # Validate and read the file
        file = request.files.get('file')
        validate_excel_file(file)
        df = pd.read_excel(file)

        # Validate required columns
        if not set(REQUIRED_COLUMNS).issubset(df.columns):
            return jsonify({"error": f"Invalid file format. Required columns: {REQUIRED_COLUMNS}"}), 400

        # Check if the file is empty
        if df.empty:
            return jsonify({"error": "Uploaded file is empty."}), 400

        # Initialize success and error tracking
        uploaded_ids = []
        errors = []
        valid_indices = []
        invalid_indices = []

        # Process each row with validation
        for idx, row in df.iterrows():
            # Convert row to dictionary for easier handling
            row_data = row.to_dict()

            # Validate the row
            row_errors = validate_row(row_data, idx)
            if row_errors:
                errors.extend(row_errors)
                invalid_indices.append(idx + 1)  # Track invalid row indices
                continue  # Skip this row

            try:
                # Upload the image to Firebase Storage
                uploaded_image_url = upload_image_to_storage(row_data["imageURL"], row_data["name"])
                if not uploaded_image_url:
                    errors.append({
                        "row": idx + 1,
                        "name": row_data["name"],
                        "error": "Invalid image URL"
                    })
                    invalid_indices.append(idx + 1)  # Track invalid row indices
                    continue  # Skip this row

                # Prepare Firestore document data
                doc_data = {
                    "name": row_data["name"],
                    "categoryId": row_data["categoryId"],
                    "cost": row_data["cost"],
                    "maxDiscount": row_data.get("maxDiscount", 0),  # Default to 0 if missing
                    "description": row_data["description"],
                    "imageURL": uploaded_image_url,
                    "isAvailable": row_data["isAvailable"],
                    "isVeg": row_data["isVeg"],
                    "extraDescription": row_data["extraDescription"]
                }
                
                # Upload the document to Firestore (overwrite if exists)
                document_id = upload_document_to_firestore(org_id, menu_id, doc_data)
                uploaded_ids.append({"row": idx + 1, "documentId": document_id})
                valid_indices.append(idx + 1)  # Track valid row indices


            except requests.exceptions.RequestException as e:
                errors.append({
                    "row": idx + 1,
                    "name": row_data["name"],
                    "error": f"Image upload error: {str(e)}"
                })
                invalid_indices.append(idx + 1)  # Track invalid row indices
                continue  # Skip this row
            except Exception as e:
                errors.append({
                    "row": idx + 1,
                    "name": row_data["name"],
                    "error": f"Data upload error: {str(e)}"
                })
                invalid_indices.append(idx + 1)  # Track invalid row indices
                continue  # Skip this row

        # Construct response
        response = {
            "message": "File processed with some errors" if errors else "File processed successfully",
            "uploadedDocumentIds": uploaded_ids,
            "errors": errors,
            "processedCounts": {
                "validRows": len(valid_indices),
                "invalidRows": len(invalid_indices),
                "validIndices": valid_indices,
                "invalidIndices": invalid_indices
            }
        }

        # If no rows were successfully uploaded
        if not uploaded_ids:
            response["message"] = "No rows were successfully uploaded."
            return jsonify(response), 400

        # Return successful rows and errors
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500