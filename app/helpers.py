import requests
from firebase_admin import credentials, firestore, initialize_app, storage
import pandas as pd

REQUIRED_COLUMNS = [
    "name", "categoryId", "cost", "maxDiscount",
    "description", "imageURL", "isAvailable", "isVeg", "extraDescription"
]

def validate_excel_file(file):
    """Validate the uploaded file format and content."""
    if not file:
        raise ValueError("No file part in the request")
    if file.filename == '':
        raise ValueError("No file selected")
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise ValueError("Invalid file format. Only Excel files are allowed.")
    
def upload_image_to_storage(image_url, image_name):
    """Download an image from a URL and upload it to Firebase Storage."""
    try:
        bucket = storage.bucket()
        response = requests.get(image_url)
        response.raise_for_status()  # Raise error for HTTP issues
        blob = bucket.blob(f"imagesss/{image_name}.jpg")
        blob.upload_from_string(response.content, content_type="image/jpeg")
        blob.make_public()
        return blob.public_url
    except requests.exceptions.RequestException as e:
        # Log and skip invalid URLs
        print(f"Error downloading image for {image_name}: {e}")
        return None
    
def upload_document_to_firestore(org_id, menu_id, data):
    """
    Upload a document to Firestore. If the document already exists (based on 'name'), overwrite it.
    """
    collection_path = f"organization/{org_id}/menus/{menu_id}/items"
    db = firestore.client()

    # Use 'name' as the unique key for the document ID
    # Sanitize the name to create a valid Firestore document ID
    doc_id = data["name"].strip().replace(" ", "_").lower()  # Generate a unique ID based on the name
    doc_ref = db.collection(collection_path).document(doc_id)
    
    print(f"Generated doc_id: {doc_id}")


    # Set (overwrite or add) the document
    doc_ref.set(data)  # Firestore's set() overwrites the document if it exists

    return doc_id

def validate_row(row, index):
    """Validate a single row of data."""
    errors = []

    # Validate 'name' (required, text, not purely numeric)
    name = row.get("name")
    if pd.isna(name) or not isinstance(name, str) or name.isdigit():
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'name' must be a non-empty text field and not a pure number."
        })

    # Validate 'categoryId' (required, integer)
    category_id = row.get("categoryId")
    if pd.isna(category_id) or not isinstance(category_id, (int, float)) or not float(category_id).is_integer():
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'categoryId' must be a non-empty integer."
        })

    # Validate 'cost' (required, float or int)
    cost = row.get("cost")
    if pd.isna(cost) or not isinstance(cost, (int, float)):
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'cost' must be a non-empty number (int or float)."
        })

    # Validate 'description' (required, text)
    description = row.get("description")
    if pd.isna(description) or not isinstance(description, str):
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'description' must be a non-empty text field."
        })

    # Validate 'imageURL' (required, text)
    image_url = row.get("imageURL")
    if pd.isna(image_url) or not isinstance(image_url, str):
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'imageURL' must be a non-empty text field."
        })

    # Validate 'isAvailable' (required, boolean-like: true/false, 0/1)
    is_available = row.get("isAvailable")
    if pd.isna(is_available) or not (is_available in [True, False, 0, 1, "true", "false", "TRUE", "FALSE"]):
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'isAvailable' must be a boolean-like value (true/false, 0/1)."
        })

    # Validate 'isVeg' (required, boolean-like: true/false, 0/1)
    is_veg = row.get("isVeg")
    if pd.isna(is_veg) or not (is_veg in [True, False, 0, 1, "true", "false", "TRUE", "FALSE"]):
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'isVeg' must be a boolean-like value (true/false, 0/1)."
        })

    # Validate 'extraDescription' (required, text)
    extra_description = row.get("extraDescription")
    if pd.isna(extra_description) or not isinstance(extra_description, str):
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": "'extraDescription' must be a non-empty text field."
        })

    # Check for unexpected columns
    unexpected_columns = set(row.keys()) - set(REQUIRED_COLUMNS)
    if unexpected_columns:
        errors.append({
            "row": index + 1,
            "name": name or "Unknown",
            "error": f"Unexpected columns present: {unexpected_columns}"
        })

    return errors