from fastapi.routing import APIRouter

from imdb_api.web.api import movies, flops, plots, preview

api_router = APIRouter()
#api_router.include_router(monitoring.router)
#api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(movies.router, prefix="/movies", tags=["echo"])
api_router.include_router(flops.router, prefix="/flops", tags=["echo"])
api_router.include_router(plots.router, prefix="/plots", tags=["echo"])
api_router.include_router(preview.router, prefix="/preview", tags=["echo"])


