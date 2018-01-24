# encoding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import fire
import hashlib
from evernote.api.client import EvernoteClient
from evernote.edam.error import ttypes as Errors
from evernote.edam.type import ttypes
from secret import PROD_TOKEN, DEV_TOKEN


def get_evernote_auth_token(env="prod"):
    """Return either a valid production / dev Evernote developer token.

    Parameters
    ----------
    env : str
        Indicate which environment's token to be returned.
        Valid options: ["prod", "dev"]

    Returns
    -------
    token : str

    """
    return PROD_TOKEN if env == 'prod' else DEV_TOKEN


def get_client(env="prod"):
    """Return a Evernote API client

    Parameters
    ----------
    env : str
        Indicate which environment's token to be returned.
        Valid options: ["prod", "dev"]

    Returns
    -------
    client : evernote.api.client.EvernoteClient

    """
    sandbox = False if env == 'prod' else True
    return EvernoteClient(token=get_evernote_auth_token(env), sandbox=sandbox)


def get_note_store(env="prod"):
    """Return a NoteStore used to used to manipulate notes, notebooks in a user account.

    Parameters
    ----------
    env : str
        Indicate which environment's token to be returned.
        Valid options: ["prod", "dev"]

    Returns
    -------
    NoteStore

    Notes
    -----
    Evernote documentation:
        https://dev.evernote.com/doc/start/python.php

    """
    return get_client(env).get_note_store()


def get_note(guid=None, env='prod'):
    """Return a specific Note instance by guid.

    Parameters
    ----------
    guid : str

    env : str
        Indicate which environment's token to be returned.
        Valid options: ["prod", "dev"]

    Returns
    -------
    evernote.edam.type.ttypes.Note

    """
    auth_token = get_evernote_auth_token(env)


    assert guid is not None, 'Guid is not available.'
    return get_note_store().getNote(auth_token, guid, False, False, False , False)


def get_notebook(guid=None):
    """Return a specific Notebook instance by guid.

    Parameters
    ----------
    guid : str

    Returns
    -------
    evernote.edam.type.ttypes.Notebook

    """
    assert guid is not None, 'Guid is not available.'
    return get_note_store().getNotebook(guid)


def get_notebooks(env="prod"):
    """Get all available Notebook instances in a user account.

    Parameters
    ----------
    env : str
        Indicate which environment's token to be returned.
        Valid options: ["prod", "dev"]

    Returns
    -------
    Notebooks : list of evernote.edam.type.ttypes.Notebook

    """
    client = get_client(env)

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
    """Create a new notebook with given `name`.

    Parameters
    ----------
    name : str
        Indicating the name of the notebook to be created

    Returns
    -------
    evernote.edam.type.ttypes.Notebook

    """
    assert name is not None, 'Notebook name is not specified.'
    notebook = ttypes.Notebook()
    notebook.name = name
    return get_note_store().createNotebook(notebook)


def create_resource(file_path, mime='image/png'):
    """Create a Resource instance for attaching to evernote Note instance

    Parameters
    ----------
    file_path : str
        Indicate file path of the file

    mime : str, optional
        Valid MIME type indicating type of the file

    Returns
    -------
    evernote.edam.type.ttypes.Resource
        The Resource must contain three parts:
            - MIME type
            - content: evernote.edam.type.ttypes.Data
            - hash

    Notes
    -----
    Create string of MD5 sum:
        https://stackoverflow.com/questions/5297448/how-to-get-md5-sum-of-a-string-using-python

    """

    file_data = None
    with open(file_path, 'rb') as f:
        byte_str = f.read()
        file_data = bytearray(byte_str)

    md5 = hashlib.md5()
    md5.update(file_data)
    hexhash = md5.hexdigest()
    data = ttypes.Data()

    # build Resource's necessary data
    data.size = len(file_data)
    data.bodyHash = hexhash
    data.body = file_data

    # build Resource Type
    resource = ttypes.Resource()
    resource.mime = mime
    resource.data = data
    return resource, hexhash


def create_note(note_title, note_body, resources=[], parent_notebook=None, env="prod"):
    """Create new Note with the given attachments in user's notebook

    Parameters
    ----------
    note_title : str
        Text to used as new note's title

    note_body : str
        Text to insert into note

    resources : list of evernote.edam.type.ttypes.Resource
        List of attachments to combined with the note

    parent_notebook : evernote.edam.type.ttypes.Notebook
        Notebook instance to insert new note

    env : str
        Indicate which environment's token to be returned.
        Valid options: ["prod", "dev"]

    Returns
    -------
    evernote.edam.type.ttypes.Note
        The newly created Note instance

    Notes
    -----
    Evernote error documentation:
        http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode

    """
    auth_token = get_evernote_auth_token(env)
    note_store = get_note_store(env)

    # create note object
    ourNote = ttypes.Note()
    ourNote.title = note_title

    # build body of note
    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += "<en-note>%s" % note_body

    if resources:
        # add Resource objects to note body
        nBody += "<br />" * 2
        ourNote.resources = resources
        for resource in resources:
            hexhash = resource.data.bodyHash
            nBody += "Attachment with hash %s: <br /><en-media type=\"%s\" hash=\"%s\" /><br />" % \
                     (hexhash, resource.mime, hexhash)
    nBody += "</en-note>"

    ourNote.content = nBody


    # parent_notebook is optional. if omitted, default notebook is used
    if parent_notebook and hasattr(parent_notebook, 'guid'):
        ourNote.notebookGuid = parent_notebook.guid

    # attempt to create note in Evernote account
    try:
        note = note_store.createNote(auth_token, ourNote)
    except Errors.EDAMUserException, edue:
        print("EDAMUserException:", edue)
        return None
    except Errors.EDAMNotFoundException, ednfe:
        # Parent Notebook GUID doesn't correspond to an actual notebook
        print("EDAMNotFoundException: Invalid parent notebook GUID")
        return None

    # Return created note object
    return note


def update_note(note, note_title, note_body, note_guid, resources):
    """Update existing note in Evernote identified by `note_guid`.

    Parameters
    ----------
    note : evernote.edam.type.ttypes.Note
        Note instance to be updated

    note_title : str
        Text to used as new note's title

    note_body : str
        Text to insert into note

    note_guid : str

    resources : list of evernote.edam.type.ttypes.Resource
        List of attachments to combined with the note

    Returns
    -------
    evernote.edam.type.ttypes.Note
        The updated Note instance

    Notes
    -----
    Evernote API documentation
        https://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_updateNote
    """

    auth_token = get_evernote_auth_token()
    note_store = get_note_store()

    note.guid = note_guid
    note.title = note_title

    # build body of note with new resources
    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += "<en-note>%s" % note_body

    if resources:
        # add Resource objects to note body
        nBody += "<br />" * 2
        note.resources = resources
        for resource in resources:
            hexhash = resource.data.bodyHash
            nBody += "Attachment with hash %s: <br /><en-media type=\"%s\" hash=\"%s\" /><br />" % \
                     (hexhash, resource.mime, hexhash)
    nBody += "</en-note>"

    note.content = nBody

    # attempt to update note in Evernote account
    try:
        note = note_store.updateNote(auth_token, note)
    except Errors.EDAMNotFoundException, ednfe:
        # Parent Notebook GUID doesn't correspond to an actual notebook
        print("EDAMNotFoundException: Invalid parent notebook GUID")
        return None

    # Return created note object
    return note


if __name__ == '__main__':
    fire.Fire()