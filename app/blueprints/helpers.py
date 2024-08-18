import os
import pathlib
from flask import make_response, jsonify, current_app as app
from app import db
from typing import Any
import requests

def create_response(data, status_code):
    """
    Create a JSON response with a given payload and status code.
    """
    response = make_response(jsonify({'data': data}), status_code)
    return response

def validate_fields(json_data, required_fields):
    """
    Check for missing fields in the provided JSON data.
    """
    missing_fields = [field for field in required_fields if field not in json_data]
    return missing_fields

def make_error_response(error_message, status_code=400):
    """
    Create an error JSON response with a given error message and status code.
    """
    response = make_response(jsonify({'error': {'message': error_message}}), status_code)
    return response

def handle_general_exception(e):
    """ Handle exceptions raised during a request. """
    app.logger.error(str(e), exc_info=True)
    response = {
        "error": str(e),
        "message": "An error occurred."
        }
    
    return jsonify(response), 500

def handle_exceptions(func) -> dict:
    """ Handle the errors that may arise 
    args: func (function): The function to execute
    returns: 
    None: If the function is executed successfully and no errors are raised
    dict: If an error is raised, it returns a dictionary with the error message
    """
    try:
        return func()
    except ValueError as e:
        app.logger.error('ValueError: %s', e, exc_info=True)
        db.session.rollback()
        return make_error_response(str(e), 400)
    except TypeError as e:
        app.logger.error('TypeError: %s', e, exc_info=True)
        return make_error_response(str(e), 400)
    except AttributeError as e:
        app.logger.error('AttributeError: %s', e, exc_info=True)
        return make_error_response(str(e), 400)
    except KeyError as e:
        app.logger.error('KeyError: %s', e, exc_info=True)
        return make_error_response(str(e), 400)
    except IOError as e:
        app.logger.error('IOError: %s', e, exc_info=True)
        return make_error_response(str(e), 400)
    except RuntimeError as e:
        app.logger.error('RuntimeError: %s', e, exc_info=True)
        return make_error_response(str(e), 400)
    except ZeroDivisionError as e:
        app.logger.error('ZeroDivisionError: %s', e, exc_info=True)
        return make_error_response(str(e), 400)
    except Exception as e:
        app.logger.error('An error occurred: %s', e, exc_info=True)
        db.session.rollback()
        return make_error_response(str(e), 500)


def get_attribute(obj, attr) -> Any:
    """ 
    Safely get the attribute value from the object, if it does not exist log the error and raise an exception 
    
    args: 
            obj (object): The object to get the attribute value from
            attr (str): The attribute name to get the value from the object
    returns:
            value: The attribute value from the object
    """

    # Get the attribute value from the object
    value = getattr(obj, attr, None)

    # If the value is None, log the error and raise an exception
    if not value:
        app.logger.error(f'{attr} not found', exc_info=True)
        raise ValueError(f'{attr} no encontrado')
    
    return value