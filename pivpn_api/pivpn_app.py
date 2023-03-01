"""fastapi app to call shell commands from pivpn"""

import subprocess
from typing import Literal

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasicCredentials

try:
    from pivpn_api import auth, shell_commands
except ImportError:
    import auth
    import shell_commands

app = FastAPI()


# for each shell command from shell_commands.py create a route with the same name


def handle_exeption(result: Exception) -> JSONResponse:
    if isinstance(result, subprocess.TimeoutExpired):
        return JSONResponse(status_code=408, content={"stdout": str(result)})
    return JSONResponse(status_code=400, content={"stdout": str(result)})


@app.get(
    "/",
    include_in_schema=False,
)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/whoami")
async def whoami(credentials: HTTPBasicCredentials = Depends(auth.security)):
    """get the name of the user who called the command"""
    auth.check_credentials(credentials)
    result = shell_commands.run_pipe_shell_command(shell_commands.whoami)
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.get("/get_all_clients")
async def get_all_clients(
    credentials: HTTPBasicCredentials = Depends(auth.security),
):
    """get all the clients from the server"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.get_all_clients
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.post("/add_client")
async def add_client(
    user_name: str, credentials: HTTPBasicCredentials = Depends(auth.security)
):
    """add a new client to the server"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.add_client + [user_name]
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.get("/qr_client")
async def qr_client(
    user_name: str, credentials: HTTPBasicCredentials = Depends(auth.security)
):
    """get the qr code for a client"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.qr_client + [user_name]
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.post("/disable_client")
async def disable_client(
    user_name: str, credentials: HTTPBasicCredentials = Depends(auth.security)
):
    """disable a client"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.disable_client + [user_name]
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.post("/enable_client")
async def enable_client(
    user_name: str, credentials: HTTPBasicCredentials = Depends(auth.security)
):
    """enable a client"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.enable_client + [user_name]
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.delete("/delete_client")
async def delete_client(
    user_name: str, credentials: HTTPBasicCredentials = Depends(auth.security)
):
    """delete a client"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.delete_client + [user_name]
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.get("/list_clients")
async def list_clients(
    credentials: HTTPBasicCredentials = Depends(auth.security),
):
    """list all the clients"""
    result = shell_commands.run_pipe_shell_command(shell_commands.list_clients)
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.post("/backup_clients")
async def backup_clients(
    credentials: HTTPBasicCredentials = Depends(auth.security),
):
    """backup all the clients"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.backup_clients
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.get("/speed_test")
async def speed_test(type: Literal["full", ""] = ""):
    """run a speed test"""
    # run speedtest inside container NOT via pipe
    result = shell_commands.run_shell_command(
        shell_commands.speed_test + ["--simple"]
        if type == ""
        else shell_commands.speed_test
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


@app.get("/get_config_by_filepath")
async def get_config_by_filepath(
    filepath: str, credentials: HTTPBasicCredentials = Depends(auth.security)
):
    """get the config file by filepath"""
    result = shell_commands.run_pipe_shell_command(
        shell_commands.get_config_by_filepath + [filepath]
    )
    if isinstance(result, Exception):
        return handle_exeption(result)
    return {"stdout": result}


# main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7070)
