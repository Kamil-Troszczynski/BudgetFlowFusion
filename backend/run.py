from src import app
from src.routes.homepage import *
import uvicorn


if __name__ == "__main__":
    uvicorn.run("run:app", host = "0.0.0.0", port = 8080, reload = True)