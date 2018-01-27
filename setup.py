# encoding: utf-8
GITHUB_SECRET_FILE = 'github/secret.py'
EVERNOTE_SECRET_FILE = 'enote/secret.py'
SETTING_FILE = 'settings.py'
NOTEBOOK = 'gist-evernote'

def initialize():
    """Use settings.py to setup/update environment"""
    from settings import GITHUB_AUTH_TOKEN, \
        EVERNOTE_PROD_TOKEN, EVERNOTE_SANDBOX_TOKEN

    setting_str = ''

    # setup github credential
    while not GITHUB_AUTH_TOKEN:
        GITHUB_AUTH_TOKEN = raw_input("Github Personal Access Token: ")

    with open(GITHUB_SECRET_FILE, 'w') as f:
        string = "GITHUB_AUTH_TOKEN = \"{}\"\n".format(GITHUB_AUTH_TOKEN)
        f.write(string)
        setting_str += string

    # setup evernote credential
    while not EVERNOTE_PROD_TOKEN:
        EVERNOTE_PROD_TOKEN = raw_input("Evernote Production Developer Token: ")

    with open(EVERNOTE_SECRET_FILE, 'w') as f:
        string = "EVERNOTE_PROD_TOKEN = \"{}\"\n".format(EVERNOTE_PROD_TOKEN)
        f.write(string)
        setting_str += string

        # optional for local debug
        string = "EVERNOTE_SANDBOX_TOKEN = \"{}\"\n".format(EVERNOTE_SANDBOX_TOKEN)
        f.write(string)
        setting_str += string

    # setup notebook
    notebook = raw_input("Evernote notebook name you want to put gists (default set to {}): ".format(NOTEBOOK))
    notebook = notebook if notebook else NOTEBOOK
    setting_str += "NOTEBOOK_TO_SYNC = \"{}\"\n".format(notebook)

    # update setting
    with open(SETTING_FILE, "w") as f:
        f.write(setting_str)

    print("You're all set! run\n\n python app.py\n\nto start synchronization :) ")

    return True


if __name__ == '__main__':
    initialize()
