import tkinter as tk
from tkinter import filedialog

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["filesystem"])


class PickDirectoryResponse(BaseModel):
    path: str | None


@router.get("/pick-directory", response_model=PickDirectoryResponse)
def pick_directory() -> PickDirectoryResponse:
    """Opens a native OS folder-selection dialog on this machine, so a scan
    root can be chosen instead of typed. Only meaningful because this
    tool's backend and the browser driving it always run on the same
    machine (Principle II: Local-First) -- there is no remote-deployment
    case where this would pick a directory on the wrong computer."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    try:
        selected = filedialog.askdirectory()
    finally:
        root.destroy()
    return PickDirectoryResponse(path=selected or None)
