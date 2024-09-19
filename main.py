import uvicorn
import sys

sys.dont_write_bytecode = True

if __name__ == "__main__":
    PYTHONDONTWRITEBYTECODE=1, uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
