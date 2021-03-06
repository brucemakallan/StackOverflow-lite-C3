from flask import make_response, jsonify


class Validator(object):

    @staticmethod
    def check_for_content(entities_list, no_content_msg):
        if entities_list is not None:
            # Convert the list of objects into a list of dictionaries
            list_of_entity_dicts = [entity_obj.obj_to_dict() for entity_obj in entities_list]
            if len(list_of_entity_dicts) == 0:
                return Validator.custom_response(200, 'OK', no_content_msg)
            return jsonify(list_of_entity_dicts), 200
        else:
            return Validator.custom_response(200, 'OK', no_content_msg)

    @staticmethod
    def custom_response(status_code, status_message, friendly_message):
        """Return a response with Status Code, its corresponding message, and a friendly message"""

        response = make_response(
            jsonify({'status_code': str(status_code) + ': ' + status_message + ', ' + friendly_message}),
            status_code)
        response.headers['Status-Code'] = str(status_code) + ': ' + status_message + ', ' + friendly_message
        return response
