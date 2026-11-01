import os

from quart import Quart, render_template, request, abort
from tinydb import TinyDB

app = Quart(__name__)
db = TinyDB("kanban.json")
cards = db.table("cards")

COLUMNS = [("todo", "To do"), ("doing", "In progress"), ("done", "Done")]
VALID = {key for key, _ in COLUMNS}


def board_context():
    grouped = {key: [] for key in VALID}
    for doc in cards.all():
        grouped.setdefault(doc["status"], []).append({**doc, "id": doc.doc_id})
    return {"columns": COLUMNS, "grouped": grouped}


async def render_board():
    return await render_template("_board.html", **board_context())


@app.get("/")
async def index():
    return await render_template("index.html", **board_context())


@app.post("/cards")
async def create_card():
    form = await request.form
    title = form.get("title", "").strip()
    status = form.get("status", "todo")
    if title and status in VALID:
        cards.insert({
            "title": title,
            "description": form.get("description", "").strip(),
            "status": status,
        })
    return await render_board()


@app.post("/cards/<int:card_id>/move")
async def move_card(card_id: int):
    form = await request.form
    status = form.get("status")
    if status not in VALID or not cards.contains(doc_id=card_id):
        abort(400)
    cards.update({"status": status}, doc_ids=[card_id])
    return await render_board()


@app.delete("/cards/<int:card_id>")
async def delete_card(card_id: int):
    if cards.contains(doc_id=card_id):
        cards.remove(doc_ids=[card_id])
    return await render_board()


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
