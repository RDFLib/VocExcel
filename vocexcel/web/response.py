from fastapi.responses import Response


class TurtleResponse(Response):
    media_type = "text/turtle"

    def render(self, content: str) -> bytes:
        return content.encode("utf-8")
