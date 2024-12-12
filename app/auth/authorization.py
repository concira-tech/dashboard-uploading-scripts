from flask import request, jsonify
from functools import wraps
from app.helpers import get_employee_permissions  # Import the permissions service


def authorize(required_permissions):

    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            try:
                # Fetch employee permissions
                user = getattr(request, 'user', None)
                if not user:
                    return jsonify({'message': 'Unauthorized Access!!!'}), 403
                
                employee_permissions = get_employee_permissions(user)

                # Check if the user has all required permissions or a wildcard permission '*'
                has_permission = all(
                    employee_permissions.get(permission, False) or employee_permissions.get('*', False)
                    for permission in required_permissions
                )

                if not has_permission:
                    return jsonify({'message': 'Unauthorized Access!!!'}), 403

                # If all permissions are satisfied, proceed to the next function
                return f(*args, **kwargs)
            except Exception as error:
                print("Error in authorization middleware:", error)
                return jsonify({'message': 'Internal Server Error'}), 500

        return wrapped_function
    return decorator
