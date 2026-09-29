import threading

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["filesystem"])

# The dialog runs a nested Tk event loop that blocks its worker thread until
# a human clicks something. Starlette runs sync endpoints on a bounded
# thread pool, so letting these stack up would exhaust it and hang every
# other endpoint behind a pile of undismissed dialogs.
_dialog_lock = threading.Lock()


class PickDirectoryResponse(BaseModel):
    path: str | None


@router.post("/pick-directory", response_model=PickDirectoryResponse)
def pick_directory() -> PickDirectoryResponse:
    """Opens a native OS folder-selection dialog on this machine, so a scan
    root can be chosen instead of typed. Only meaningful because this
    tool's backend and the browser driving it always run on the same
    machine (Principle II: Local-First).

    POST rather than GET because it has a side effect on the user's physical
    desktop: as a GET, any page the user happened to visit could pop a
    modal dialog on their screen with a bare `<img src=...>`.

    tkinter is imported here rather than at module scope on purpose. It is
    the one dependency that cannot be declared in requirements.txt, and a
    module-level import made the whole API fail to start on any host without
    Tk -- a slim container, or a Linux box missing python3-tk -- taking
    twelve unrelated endpoints down with it.
    """
    if not _dialog_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="A folder dialog is already open.")
    try:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except ImportError as exc:
            raise HTTPException(
                status_code=501,
                detail="No folder picker on this host (tkinter is unavailable). Type the path instead.",
            ) from exc

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            # Tk is installed but there is no display to draw on: a headless
            # server, or a Windows service in a non-interactive session.
            raise HTTPException(
                status_code=501,
                detail="No display available for a folder dialog. Type the path instead.",
            ) from exc

        root.withdraw()
        root.attributes("-topmost", True)
        try:
            selected = filedialog.askdirectory()
        finally:
            root.destroy()
        return PickDirectoryResponse(path=selected or None)
    finally:
        _dialog_lock.release()
