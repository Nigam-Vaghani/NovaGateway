import asyncio
import uvicorn
from app.config import settings

async def main():
    if settings.is_https_active:
        from fastapi import FastAPI, Request
        from fastapi.responses import RedirectResponse
        import logging

        logger = logging.getLogger("uvicorn.error")
        logger.info(f"Starting HTTPS server on port {settings.HTTPS_PORT} and HTTP redirect server on port {settings.HTTP_REDIRECT_PORT}")

        redirect_app = FastAPI()

        @redirect_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
        async def redirect_to_https(request: Request, path: str):
            url = request.url.replace(scheme="https", port=settings.HTTPS_PORT)
            return RedirectResponse(url=str(url), status_code=301)

        config_redirect = uvicorn.Config(
            redirect_app, host="0.0.0.0", port=settings.HTTP_REDIRECT_PORT, log_level="warning"
        )
        config_main = uvicorn.Config(
            "app.main:app",
            host="0.0.0.0",
            port=settings.HTTPS_PORT,
            ssl_keyfile=settings.SSL_KEYFILE,
            ssl_certfile=settings.SSL_CERTFILE,
            log_level="info"
        )

        server_redirect = uvicorn.Server(config_redirect)
        server_main = uvicorn.Server(config_main)

        await asyncio.gather(
            server_redirect.serve(),
            server_main.serve()
        )
    else:
        import logging
        logger = logging.getLogger("uvicorn.error")
        logger.info("Starting HTTP server on port 8000")
        
        config = uvicorn.Config("app.main:app", host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
