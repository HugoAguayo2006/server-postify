from fastapi import FastAPI
import socketio
import asyncpg

DATABASE_URL = "postgresql://andresramirezruiz:0803062006@localhost:5432/Chatify"

#Las salas que existen.
rooms = ["General", "Tech Talk", "Random", "Gaming"]
db_pool = None
app = FastAPI()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)
socket_app = socketio.ASGIApp(sio, app)

@app.get("/")
async def home():
    return {"message": "Servidor de Chatify funcionando", "rooms": rooms}

@app.on_event("startup")
async def startup():
    global db_pool
    #Conecta a la base cuando prende el server.
    db_pool = await asyncpg.create_pool(DATABASE_URL)

@sio.event
async def connect(sid, environ):
    print("Usuario conectado:", sid)

@sio.event
async def disconnect(sid):
    print("Usuario desconectado:", sid)

def format_message(message):
    message = dict(message)
    #La fecha se manda mas facil como texto.
    message["created_at"] = str(message["created_at"])
    return message

@sio.on("join room")
async def join_room(sid, data):
    #Agarra lo que mando React.
    username = data.get("username")
    room = data.get("room")

    #Por si intentan entrar a una sala rara.
    if room not in rooms:
        await sio.emit("error", {"message": "Room no válida"}, to=sid)
        return

    #Lo mete a esa sala.
    await sio.enter_room(sid, room)

    #Busca mensajes viejos de esa sala.
    async with db_pool.acquire() as conn:
        messages = await conn.fetch(
            """
            SELECT id, content, username, room, created_at
            FROM messages
            WHERE room = $1
            ORDER BY created_at ASC
            """,
            room
        )

    history = [format_message(message) for message in messages]

    # Le manda el historial solo al que entro.
    await sio.emit("message history", history, to=sid)
    await sio.emit("user joined", {"username": username, "room": room}, room=room)

@sio.on("leave room")
async def leave_room(sid, data):
    room = data.get("room")

    # Lo saca de la sala actual.
    await sio.leave_room(sid, room)
    await sio.emit("user left", {"room": room}, room=room)

@sio.on("chat message")
async def chat_message(sid, data):
    #Datos del mensaje que viene del frontend.
    username = data.get("username")
    room = data.get("room")
    content = data.get("content")

    if room not in rooms:
        await sio.emit("error", {"message": "Room no válida"}, to=sid)
        return

    #Primero se guarda en PostgreSQL.
    async with db_pool.acquire() as conn:
        saved_message = await conn.fetchrow(
            """
            INSERT INTO messages (content, username, room)
            VALUES ($1, $2, $3)
            RETURNING id, content, username, room, created_at
            """,
            content,
            username,
            room
        )
    message = format_message(saved_message)

    #Ahora si se lo manda a todos en esa sala.
    await sio.emit("chat message", message, room=room)
