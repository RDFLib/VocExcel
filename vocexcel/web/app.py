from textwrap import dedent
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from vocexcel.web import router
from vocexcel.web.settings import Settings


def register_routers(app: FastAPI) -> None:
    app.include_router(router.router, prefix="/api/v1", tags=["VocExcel"])

    @app.get("/{path:path}", include_in_schema=False)
    def all_path_route(path):
        """Catch-all route for SPA."""
        index_html_path = Path(f"{Settings.VOCEXCEL_WEB_STATIC_DIR}/index.html")

        path = (
            Path(f"{Settings.VOCEXCEL_WEB_STATIC_DIR}/{path}")
            if path != ""
            else index_html_path
        )

        if path.is_file():
            return FileResponse(path)

        return FileResponse(index_html_path)


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="VocExcel",
        description=dedent(
            """
            Another Excel-to-RDF converter for SKOS vocabs, but one that:
    
            * uses fixed templates to keep it simple
            * meets particular SKOS profile outcomes such as [VocPub](https://w3id.org/profile/vocpub)
            * is under active development, production use, and is commercially supported
            
            Source repository: [https://github.com/RDFLib/VocExcel](https://github.com/RDFLib/VocExcel)
        """
        ),
    )

    register_routers(app)
    register_middlewares(app)

    return app
