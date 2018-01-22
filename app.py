import time
from pprint import pprint
from enote.util import get_auth_token, get_note_store, create_resource, create_note
from github.util import query_graphql
from web.util import fullpage_screenshot
from selenium import webdriver

def main():

    # get latest gists by update time
    payload = "{\"query\":\"query {\\n  viewer {\\n    gists(last:5, privacy:ALL, orderBy: {field: UPDATED_AT, direction: ASC}) {\\n\\t\\t\\tedges {\\n\\t\\t\\t\\tnode {\\n\\t\\t\\t\\t\\tid\\n\\t\\t\\t\\t\\tdescription\\n\\t\\t\\t\\t\\tname\\n\\t\\t\\t\\t\\tpushedAt\\n\\t\\t\\t\\t}\\n\\t\\t\\t}\\n\\t\\t}\\n  }\\n}\"}"
    res = query_graphql(payload)
    gists = [e['node'] for e in res['data']['viewer']['gists']['edges']]
    pprint(gists)

    # TODO check whether gist need to be updated to evernote or not

    # TODO check whether gist had been syn to evernote or not


    # take screen shot for gists needed to be added to Evernote
    driver = webdriver.Chrome()
    gist_name = gists[0]['name']
    url = 'https://gist.github.com/{}'.format(gist_name)
    driver.get(url)
    time.sleep(5)
    image_path = 'images/gist.png'

    fullpage_screenshot(driver, image_path)
    driver.quit()

    # create new note with fetched screen shot
    auth_token = get_auth_token()
    note_store = get_note_store()

    resources = []
    resource = create_resource(image_path)
    resources.append(resource)

    create_note(auth_token, note_store,
                     'Test Note with attachments', 'Hello world', resources)


if __name__ == '__main__':
    main()
