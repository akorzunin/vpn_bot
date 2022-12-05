"""fastapi app to call shell commands from pivpn"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import shell_commands

app = FastAPI()


# for each shell command from shell_commands.py create a route with the same name


@app.get("/whoami")
async def whoami():
    """get the name of the user who called the command"""
    result = shell_commands.run_shell_command(shell_commands.whoami)
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.get("/get_all_clients")
async def get_all_clients():
    """get all the clients from the server"""
    result = shell_commands.run_shell_command(shell_commands.get_all_clients)
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.post("/add_client")
async def add_client(user_name: str):
    """add a new client to the server"""
    result = shell_commands.run_shell_command(
        shell_commands.add_client + [user_name]
    )
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.get("/qr_client")
async def qr_client(user_name: str):
    """get the qr code for a client"""
    result = shell_commands.run_shell_command(
        shell_commands.qr_client + [user_name]
    )
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.post("/disable_client")
async def disable_client(user_name: str):
    """disable a client"""
    result = shell_commands.run_shell_command(
        shell_commands.disable_client + [user_name]
    )
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.post("/enable_client")
async def enable_client(user_name: str):
    """enable a client"""
    result = shell_commands.run_shell_command(
        shell_commands.enable_client + [user_name]
    )
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.post("/list_clients")
async def list_clients():
    """list all the clients"""
    result = shell_commands.run_shell_command(shell_commands.list_clients)
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


@app.post("/backup_clients")
async def backup_clients():
    """backup all the clients"""
    result = shell_commands.run_shell_command(shell_commands.backup_clients)
    if isinstance(result, Exception):
        return JSONResponse(status_code=400, content={"stdout": str(result)})
    return {"stdout": result}


# main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7070)
