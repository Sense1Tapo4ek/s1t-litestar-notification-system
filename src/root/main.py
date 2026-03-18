"""
Entry point for development: ``uv run uvicorn root.entrypoints.api:create_app --factory --reload``

Or use the installed script: ``notification-system``
"""
import uvicorn


def main() -> None:
    uvicorn.run(
        "root.entrypoints.api:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
    )


if __name__ == "__main__":
    main()
