import os
from skf import settings
from shutil import copyfile
from flask import Flask
from sqlite3 import dbapi2 as sqlite3


app = Flask(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(os.path.join(app.root_path, settings.DATABASE))
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    os.remove(os.path.join(app.root_path, 'db.sqlite'))
    os.remove(os.path.join(app.root_path, 'db.sqlite_schema'))
    copyfile(os.path.join(app.root_path, "schema.sql"), os.path.join(app.root_path, 'db.sqlite_schema'))
    init_md_checklists()
    init_md_knowledge_base()
    init_md_code_examples()
    db = connect_db()
    with app.open_resource(os.path.join(app.root_path, 'db.sqlite_schema'), mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g, settings.DATABASE):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_md_knowledge_base():
    """Converts markdown knowledge-base items to DB."""
    kb_dir = os.path.join(app.root_path, 'markdown/knowledge_base')
    for filename in os.listdir(kb_dir):
        if filename.endswith(".md"):
            name_raw = filename.split("-")
            title = name_raw[3].replace("_", " ")
            file = os.path.join(kb_dir, filename)
            data = open(file, 'r')
            file_content = data.read()
            data.close()
            content_escaped = file_content.translate(str.maketrans({"'":  r"''", "-":  r"", "#":  r""}))
            query = "INSERT OR REPLACE INTO kb_items (content, title) VALUES ('"+content_escaped+"', '"+title+"'); \n"
            with open(os.path.join(app.root_path, 'db.sqlite_schema'), 'a') as myfile:
                    myfile.write(query)
    print('Initialized the markdown knowledge-base items to database.')


def init_md_code_examples():
    """Converts markdown code-example items to DB."""
    kb_dir = os.path.join(app.root_path, 'markdown/code_examples/')
    code_langs = ['asp', 'java', 'php', 'python']
    for lang in code_langs:
        for filename in os.listdir(kb_dir+lang):
            if filename.endswith(".md"):
                name_raw = filename.split("-")
                title = name_raw[3].replace("_", " ")
                file = os.path.join(kb_dir+lang, filename)
                data = open(file, 'r')
                file_content = data.read()
                data.close()
                content_escaped = file_content.translate(str.maketrans({"'":  r"''", "-":  r"", "#":  r""}))
                query = "INSERT OR REPLACE INTO code_items (content, title, code_lang) VALUES ('"+content_escaped+"', '"+title+"', '"+lang+"'); \n"
                with open(os.path.join(app.root_path, 'db.sqlite_schema'), 'a') as myfile:
                        myfile.write(query)
    print('Initialized the markdown code-example items to database.')


def init_md_checklists():
    """Converts markdown checklists items to DB."""
    kb_dir = os.path.join(app.root_path, 'markdown/checklists')
    for filename in os.listdir(kb_dir):
        if filename.endswith(".md"):
            name_raw = filename.split("-")
            level = name_raw[4].replace("_", " ")
            if level == "0":
                # For the ASVS categories
                file = os.path.join(kb_dir, filename)
                data = open(file, 'r')
                file_content = data.read()
                data.close()
                checklistID_raw = file_content.split(":")
                checklistID = checklistID_raw[0]
                checklistID = checklistID.lstrip('V')
                checklistID = checklistID+".0"
            else :
                # For the ASVS items
                file = os.path.join(kb_dir, filename)
                data = open(file, 'r')
                file_content = data.read()
                data.close()
                checklistID_raw = file_content.split(" ")
                checklistID = checklistID_raw[0]             
            file = os.path.join(kb_dir, filename)
            data = open(file, 'r')
            file_content = data.read()
            data.close()
            content = file_content.split(' ', 1)[1]
            content_escaped = content.translate(str.maketrans({"'":  r"''", "-":  r"", "#":  r""}))
            query = "INSERT OR REPLACE INTO checklists (checklistID, content, level) VALUES ('"+checklistID+"', '"+content_escaped+"', '"+level+"'); \n"
            with open(os.path.join(app.root_path, 'db.sqlite_schema'), 'a') as myfile:
                    myfile.write(query)
    print('Initialized the markdown checklist items to database.')