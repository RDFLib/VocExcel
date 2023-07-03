import webbrowser

import uvicorn


if __name__ == "__main__":
    webbrowser.open("http://localhost:8000", new=2)
    uvicorn.run("vocexcel.web.app:create_app", host="0.0.0.0", port=8000, reload=True)
