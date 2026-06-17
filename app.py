"""
Example script showing how to represent todo lists and todo entries in Python
data structures and how to implement endpoint for a REST API with Flask.

Requirements:
* flask
"""

import uuid

from flask import Flask, request, jsonify


# initialize Flask server
app = Flask(__name__)

# create unique id for lists, entries
todo_list_1_id = str(uuid.uuid4())
todo_list_2_id = str(uuid.uuid4())
todo_list_3_id = str(uuid.uuid4())
todo_1_id = str(uuid.uuid4())
todo_2_id = str(uuid.uuid4())
todo_3_id = str(uuid.uuid4())
todo_4_id = str(uuid.uuid4())

# define internal data structures with example data (aligned with OpenAPI TodoList / TodoEntry)
# Hinweis: Die Daten liegen nur im Arbeitsspeicher und gehen bei jedem Neustart verloren.
todo_lists = [
    {'id': todo_list_1_id, 'name': 'Einkaufsliste'},
    {'id': todo_list_2_id, 'name': 'Arbeit'},
    {'id': todo_list_3_id, 'name': 'Privat'},
]
todos = [
    {'id': todo_1_id, 'name': 'Milch', 'description': '1 Liter Milch', 'list_id': todo_list_1_id},
    {'id': todo_2_id, 'name': 'Arbeitsblätter ausdrucken', 'description': 'Arbeitsblätter für die Schule ausdrucken', 'list_id': todo_list_2_id},
    {'id': todo_3_id, 'name': 'Kinokarten kaufen', 'description': 'Kinokarten für den Film ausdrucken', 'list_id': todo_list_3_id},
    {'id': todo_4_id, 'name': 'Eier', 'description': 'Eier für den Kuchen', 'list_id': todo_list_1_id},
]


# Hilfsfunktion: Liste anhand ihrer ID finden (oder None)
def _list_by_id(list_id):
    for item in todo_lists:
        if str(item['id']) == str(list_id):
            return item
    return None


# Hilfsfunktion: Eintrag anhand seiner ID finden (oder None)
def _entry_by_id(entry_id):
    for item in todos:
        if str(item['id']) == str(entry_id):
            return item
    return None


# Hilfsfunktion: alle Einträge zurückgeben, die zu einer Liste gehören
def _entries_json_for_list(list_id):
    return [entry for entry in todos if str(entry['list_id']) == str(list_id)]


# add some headers to allow cross origin access to the API on this server, necessary for using preview in Swagger Editor!
# CORS-Header: erlaubt dem Frontend (andere Domain) den Zugriff auf die API
@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# define endpoint for getting and deleting existing todo lists, and adding entries
@app.route('/todo-list/<list_id>', methods=['GET', 'DELETE', 'POST'])
def handle_list(list_id):
    list_item = _list_by_id(list_id)
    if not list_item:
        return jsonify({'message': 'Invalid list id'}), 404

    # GET: alle Einträge dieser Liste zurückgeben
    if request.method == 'GET':
        print('Returning todo list...')
        return jsonify(_entries_json_for_list(list_id))

    # DELETE: Liste samt zugehöriger Einträge löschen
    if request.method == 'DELETE':
        print('Deleting todo list...')
        global todos
        todos = [t for t in todos if str(t['list_id']) != str(list_id)]
        todo_lists.remove(list_item)
        return jsonify({'message': 'List was deleted'}), 204

    # POST: neuen Eintrag zu dieser Liste hinzufügen
    if request.method == 'POST':
        body = request.get_json(force=True) or {}
        name = body.get('name')
        # Validierung: 'name' ist Pflicht und muss ein String sein
        if not name or not isinstance(name, str):
            return jsonify({'name': body.get('name'), 'description': body.get('description')}), 406
        description = body.get('description', '')
        if description is not None and not isinstance(description, str):
            return jsonify({'name': body.get('name'), 'description': body.get('description')}), 406
        entry = {
            'id': str(uuid.uuid4()),
            'name': name,
            'description': description if isinstance(description, str) else '',
            'list_id': str(list_item['id']),
        }
        todos.append(entry)
        return jsonify(entry), 201


# define endpoint for getting all lists
@app.route('/todo-list', methods=['GET'])
def get_all_lists():
    return jsonify(todo_lists)


# define endpoint for adding a new list
@app.route('/todo-list', methods=['POST'])
def add_new_list():
    data = request.get_json(force=True) or {}
    print('Got new list to be added: {}'.format(data))
    name = data.get("name")
    # Validierung: 'name' ist Pflicht und muss ein String sein
    if not name or not isinstance(name, str):
        return jsonify({"name": data.get("name", "")}), 406
    # ID nur serverseitig – keine vom Client übergebene id wird übernommen.
    new_list = {"id": str(uuid.uuid4()), "name": name}
    todo_lists.append(new_list)
    return jsonify(new_list), 201


# Endpunkt zum Ändern (PATCH) oder Löschen (DELETE) eines einzelnen Eintrags
@app.route('/entry/<entry_id>', methods=['PATCH', 'DELETE'])
def handle_entry(entry_id):
    entry = _entry_by_id(entry_id)
    if not entry:
        return jsonify({'message': 'Invalid entry id'}), 404

    # DELETE: Eintrag entfernen
    if request.method == 'DELETE':
        todos.remove(entry)
        return jsonify({'message': 'Entry deleted'}), 204

    # PATCH: nur die mitgeschickten Felder aktualisieren
    body = request.get_json(force=True) or {}
    if not isinstance(body, dict):
        return jsonify({}), 406

    if 'name' in body:
        name = body['name']
        if not isinstance(name, str) or not name.strip():
            return jsonify({'name': body.get('name'), 'description': body.get('description')}), 406
        entry['name'] = name

    if 'description' in body:
        desc = body['description']
        if desc is not None and not isinstance(desc, str):
            return jsonify({'name': body.get('name'), 'description': body.get('description')}), 406
        entry['description'] = desc if desc is not None else ''

    return jsonify(entry), 200


if __name__ == '__main__':
    # start Flask server
    # host=0.0.0.0 -> von außen erreichbar, Port 5000
    app.debug = True
    app.run(host='0.0.0.0', port=5000)