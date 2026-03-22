from rest_framework.renderers import JSONRenderer

def _format_pagination(data):
    return {
        "total": data.get("count"),
        "limit": len(data.get("results", [])),
        "data": data.get("results"),
    }


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        status_code = response.status_code if response else 200
        success = 200 <= status_code < 300

        # if Formated
        if isinstance(data, dict) and "success" in data and "status" in data:
            return super().render(data, accepted_media_type, renderer_context)

        formatted = {
            "success": success,
            "status": status_code,
        }

        if not success:
            error_message = data
            formatted.update({"error_message": error_message})
            return super().render(formatted, accepted_media_type, renderer_context)


        # If there is pagination
        if isinstance(data, dict) and "results" in data:
            formatted.update(_format_pagination(data))
        else:
            formatted["data"] = data if not isinstance(data, dict) else data.get("data", data)

        # extra maydonlarni olish
        if isinstance(data, dict) and "extra" in data:
            formatted["extra"] = data["extra"]

        return super().render(formatted, accepted_media_type, renderer_context)
