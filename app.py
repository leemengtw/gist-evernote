# encoding: utf-8
import os
import time
from multiprocessing import Pool, cpu_count
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from enote.util import get_note, get_notebook, get_notebooks, \
    create_resource, create_note, create_notebook, update_note
from github.util import get_user_name, get_all_gists
from web.util import fullpage_screenshot, get_gist_hash, create_chrome_driver
from settings import NOTEBOOK_TO_SYNC
from db import get_db

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
GIST_BASE_URL = 'https://gist.github.com'

notebook = None
github_user = get_user_name() # get current login github user for fetching gist content
db = get_db()  # database to store synchronization info


def app():
    start = time.time()
    global notebook

    # find notebook to put new notes
    notebooks = get_notebooks()
    for n in notebooks:
        if n.name == NOTEBOOK_TO_SYNC:
            notebook = get_notebook(n.guid)

    # create notebook with the specified name if not found
    if not notebook:
        notebook = create_notebook(NOTEBOOK_TO_SYNC)
    print('Using notebook: %s' % notebook.name)

    # initialize, get all available gists
    if db.is_empty() or db.is_cold_start():
        gists = get_all_gists()
    # sync only gists that were pushed after last synchronization
    else:
        last_sync_date = db.get_last_sync()
        print("Find gists that are updated after last sync (UTC): {}".format(last_sync_date))
        gists = get_all_gists(after_date=last_sync_date)

    print("Total number of gists to be synchronized: %d" % len(gists))

    # headless mode to reduce overhead and distraction
    driver = create_chrome_driver() if gists else None
    for gist in gists:
        _ = sync_gist(gist, driver=driver)
    if driver:
        driver.quit()

    # TODO multi-processes + mysql
    # setup multiple selenium drivers to speed up if multiple cpu available
    # num_processes = min(4, cpu_count() - 1) if cpu_count() > 1 else 1
    # print("Number of %d processes being created" % num_processes)
    # pool = Pool(num_processes)
    #
    # notes = pool.map(sync_gist, gists)
    #
    # pool.terminate()
    # pool.close()
    # pool.join()

    # sync all gists successfully, set to warm-start mode
    if db.is_cold_start():
        db.toggle_cold_start()

    print("Synchronization took {:.0f} seconds.".format(time.time() - start))


def sync_gist(gist, driver):
    """Sync the Github gist to the corresponding Evernote note.

    Create a new Evernote note if there is no corresponding one with the gist.
    Overwrite existing note's content if gist has been changed.

    Parameters
    ----------
    gist : dict
        A Gist acquired by Github GraphQL API with format like:
            {
                'id': 'gist_id',
                'name': 'gist_name',
                'description': 'description',
                'pushAt': '2018-01-15T00:48:23Z'

            }

    driver : selenium.webdriver
        The web driver used to access gist url

    Returns
    -------
    note : evernote.edam.type.ttpyes.Note
        None if no new note created or updated

    """
    note_exist = False
    gist_url = '/'.join((GIST_BASE_URL, gist['name']))

    # check existing gist hash before fetch if available
    prev_hash = db.get_hash_by_id(gist['id'])
    if prev_hash:
        note_exist = True
        cur_hash = get_gist_hash(github_user, gist['name'])
        if prev_hash == cur_hash:
            print('Gist {} remain the same, ignore.'.format(gist_url))
            db.update_gist(gist)
            return None



    driver.get(gist_url)
    # wait at most x seconds for Github rendering gist context
    delay_seconds = 10
    try:
        WebDriverWait(driver, delay_seconds).until(EC.presence_of_element_located((By.CLASS_NAME, 'is-render-ready')))
    except TimeoutException:
        print("Take longer than {} seconds to load page.".format(delay_seconds))

    # get first file name as default note title
    gist_title = driver.find_element(By.CLASS_NAME, 'gist-header-title>a').text

    # take screen shot for the gist and save it temporally
    image_path = 'images/{}.png'.format(gist['name'])
    fullpage_screenshot(driver, image_path)

    # build skeleton for note (including screenshot)
    resource, _ = create_resource(image_path)
    note_title = gist['description'] if gist['description'] else gist_title
    note_body = format_note_body(gist)

    # get hash of raw gist content and save gist info to database
    gist['hash'] = get_gist_hash(github_user, gist['name'])

    # create new note / update existing note
    if not note_exist:
        note = create_note(note_title, note_body, [resource], parent_notebook=notebook)
        gist['note_guid'] = note.guid
        db.save_gist(gist)
    else:
        note_guid = db.get_note_guid_by_id(gist['id'])
        note = get_note(note_guid)
        update_note(note, note_title, note_body, note_guid, [resource])
        db.update_gist(gist)

    os.remove(image_path)
    print("Finish creating note for gist {}".format(gist_url))
    return note


def format_note_body(gist):
    """Create the note content that will be shown before attachments.

    Parameters
    ----------
    gist : dict
        Dict that contains all information of the gist

    Returns
    -------
    note_body : str

    """
    blocks = []

    desc = gist['description']
    if desc:
        blocks.append(desc)

    gist_url = '/'.join((GIST_BASE_URL, gist['name']))
    blocks.append('<a href="{}">Gist on Github</a>'.format(gist_url))
    note_body = '<br/>'.join(blocks)

    return note_body


if __name__ == '__main__':
    app()
