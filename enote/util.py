# encoding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import fire
import hashlib
import binascii
from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes
from secret import EVERNOTE_AUTH_TOKEN
from evernote.edam.error import ttypes as Errors

def get_evernote_auth_token():
    return EVERNOTE_AUTH_TOKEN


def get_client():
    return EvernoteClient(token=get_evernote_auth_token(), sandbox=False)


def get_note_store():
    client = get_client()
    return client.get_note_store()


def get_notebook(guid=None):
    assert guid is not None, 'Guid is not available.'
    return get_note_store().getNotebook(guid)


def get_notebooks():
    client = get_client()

    # get information about current user
    userStore = client.get_user_store()
    user = userStore.getUser()
    print('Current user:', user.username)

    # get information about notes
    noteStore = client.get_note_store()
    notebooks = noteStore.listNotebooks()
    # for n in notebooks:
    #     print(n.name, n.guid)
    return notebooks


def create_notebook(name=None):
    assert name is not None, 'Notebook name is not specified.'
    notebook = ttypes.Notebook()
    notebook.name = name
    return get_note_store().createNotebook(notebook)


def create_resource(file_name):
    """Create a Resource type for attaching to evernote Note"""

    image_data = None
    with open(file_name, 'rb') as f:
        byte_str = f.read()
        image_data = bytearray(byte_str)

    md5 = hashlib.md5()
    md5.update(image_data)
    gist_hash = md5.digest()
    hash_str = md5.hexdigest()
    # https://stackoverflow.com/questions/5297448/how-to-get-md5-sum-of-a-string-using-python
    data = ttypes.Data()

    # build Resource's necessary data
    data.size = len(image_data)
    data.bodyHash = gist_hash
    data.body = image_data

    # build Resource Type
    resource = ttypes.Resource()
    resource.mime = "image/png"
    resource.data = data
    return resource, hash_str


def create_note(noteTitle, noteBody, resources=[], parentNotebook=None):
    """Create a Note instance with title, body and send the Note object to user's account
    """
    authToken = get_evernote_auth_token()
    noteStore = get_note_store()

    # Create note object
    ourNote = ttypes.Note()
    ourNote.title = noteTitle

    # Build body of note
    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += "<en-note>%s" % noteBody

    if resources:
        # Add Resource objects to note body
        nBody += "<br />" * 2
        ourNote.resources = resources
        for resource in resources:
            hexhash = binascii.hexlify(resource.data.bodyHash)
            nBody += "Attachment with hash %s: <br /><en-media type=\"%s\" hash=\"%s\" /><br />" % \
                     (hexhash, resource.mime, hexhash)
    nBody += "</en-note>"

    ourNote.content = nBody


    # parentNotebook is optional; if omitted, default notebook is used
    if parentNotebook and hasattr(parentNotebook, 'guid'):
        ourNote.notebookGuid = parentNotebook.guid

    # Attempt to create note in Evernote account
    try:
        note = noteStore.createNote(authToken, ourNote)
    except Errors.EDAMUserException, edue:
        # Something was wrong with the note data
        # See EDAMErrorCode enumeration for error code explanation
        # http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        print("EDAMUserException:", edue)
        return None
    except Errors.EDAMNotFoundException, ednfe:
        # Parent Notebook GUID doesn't correspond to an actual notebook
        print("EDAMNotFoundException: Invalid parent notebook GUID")
        return None

    # Return created note object
    return note


if __name__ == '__main__':
    fire.Fire()