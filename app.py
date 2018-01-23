# encoding: utf-8
import os
import time
from multiprocessing import Pool, cpu_count
from selenium import webdriver
from datetime import datetime
from dateutil import parser
from enote.util import get_notebook, get_notebooks, create_resource, create_note, create_notebook
from github.util import get_gists
from web.util import fullpage_screenshot
from settings import NOTEBOOK_TO_SYNC
from db import get_db


GIST_BASE_URL = 'https://gist.github.com'
notebook = None


def main():
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

    # get all gists to sync later
    end_cursor = None
    gists = []
    while True:
        cur_gists, total, end_cursor, has_next_page = get_gists(end_cursor, size=1)
        gists += cur_gists

        # debug
        break

        if not has_next_page:
            break
    print("Total number of gists to be synchronized: %d" % len(gists))

    print(gists)

    db = get_db()
    if db.is_empty() or db.start_from_scratch():
        for gist in gists:
            note, gist_hash = sync_gist(gist)
            gist['hash'] = gist_hash
            db.save_gist(gist)


    #
    #
    #
    # else:
    #     # filter those gists which hasn't changed after last synchronization
    #     last_sync_date = db.get_last_sync_date()
    #     gists = [gist for gist in gists \
    #              if parser.parse(gist['pushedAt']) > last_sync_date]
    #
    #     for gist in gists:
    #         if gist




    # setup multiple selenium drivers in parallel to speed up if multiple cpu available
    # num_processes = min(4, cpu_count() - 1) if cpu_count() > 1 else 1
    # print("Number of %d processes being created" % num_processes)
    # pool = Pool(num_processes)
    #
    # notes = pool.map(sync_gist, gists)
    #
    # pool.terminate()
    # pool.join()




    # TODO check whether gist need to be updated to evernote or not

    # TODO check whether gist had been syn to evernote or not




def sync_gist(gist):
    """Sync the Github gist to the corresponding Evernote note.

    Create a new Evernote note if there is no corresponding one with the gist.
    Overwrite existing note's content if exist.

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

    Returns
    -------
    note : evernote.edam.type.ttpyes.Note

    gist_hash
        hash value of given gist

    """
    global notebook

    driver = webdriver.Chrome()
    gist_url = '/'.join((GIST_BASE_URL, gist['name']))
    driver.get(gist_url)

    # TODO tune time
    time.sleep(2)

    # take screen shot for the gist and save it temporally
    image_path = 'images/{}.png'.format(gist['name'])
    fullpage_screenshot(driver, image_path)


    # create new note with fetched screen shot attacthed
    resource, gist_hash = create_resource(image_path)
    note_title = gist['description'][:15] if gist['description'] else 'Note'
    note_body = '{}'.format(gist_url)
    note = create_note(note_title, note_body, [resource], parentNotebook=notebook)
    os.remove(image_path)
    driver.quit()
    return note, gist_hash



if __name__ == '__main__':
    main()


