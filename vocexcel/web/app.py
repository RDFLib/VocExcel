from textwrap import dedent

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from vocexcel.web import router, settings


def register_routers(app: FastAPI) -> None:
    app.include_router(router.router, prefix="/api/v1")
    app.mount(
        "/",
        StaticFiles(directory=settings.VOCEXCEL_WEB_STATIC_DIR, html=True),
        name="static",
    )


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
