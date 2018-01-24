import fire
import requests
from secret import GITHUB_AUTH_TOKEN

GITHUB_GRAPHQL_URL = 'https://api.github.com/graphql'


def query_graphql(payload, token=GITHUB_AUTH_TOKEN, url=GITHUB_GRAPHQL_URL):
    """Helper to query Github GraphQL API

    Parameters
    ----------
    payload : str
        Valid GraphQL query string.
        e.g., "{\"query\":\"query {\\n  viewer {\\n    login\\n  }\\n}\"}"

    Returns
    -------
    res : dict

    """
    headers = {
        'content-type': "application/json",
        'authorization': "Bearer {}".format(token)
    }

    r = requests.request("POST", url, data=payload, headers=headers)
    return r.json()


def get_gists(cursor=None, size=100):
    """Return all gists (public & secret) and end_cursor for pagination

    Parameters
    ----------
    cursor : str
        String indicating endCursor in previous API request.
        e.g. "Y3Vyc29yOnYyOpK5MjAxOC0wMS0yM1QxMTo1NDo0MSswOTowMM4FGyp6"

    size : int
        Specify how many gists to fetch in a HTTP request to Github.
        Default set to Node limit specified by Github GraphQL resource limit.

    Returns
    -------
    gists : list of dict
        List of gists with each gist is a dict of form:
            {
                "id": "id",
                "description": "some description",
                "name": "just a name",
                "pushedAt": "2018-01-15T08:32:57Z"
            }

    total : int
        Indicate how many gists available

    end_cursor : str
        A string representing the endCursor in gists.pageInfo

    has_next_page : bool
        Indicating whether there are gists remains

    Notes
    -----
    Github GraphQL resource limit
        https://developer.github.com/v4/guides/resource-limitations/

    """
    first_payload = "{\"query\":\"query {viewer {gists(first:%d, privacy:ALL, orderBy: {field: UPDATED_AT, direction: DESC}) {totalCount edges { node { id description name pushedAt } cursor } pageInfo { endCursor hasNextPage } } } }\"}"
    payload_template = "{\"query\":\"query {viewer {gists(first:%d, privacy:ALL, orderBy: {field: UPDATED_AT, direction: DESC}, after:\\\"%s\\\") {totalCount edges { node { id description name pushedAt } cursor } pageInfo { endCursor hasNextPage } } } }\"}"

    if not cursor:
        payload = first_payload % size
    else:
        payload = payload_template % (size, cursor)

    res = query_graphql(payload)
    assert res.get('data', False), 'No data available from Github: {}'.format(res)

    # parse nested response for easier usage
    gists = res['data']['viewer']['gists']
    total = gists['totalCount']
    page_info = gists['pageInfo']
    end_cursor, has_next_page = page_info['endCursor'], page_info['hasNextPage']
    gists = [e['node'] for e in gists['edges']]

    return gists, total, end_cursor, has_next_page


if __name__ == '__main__':
    fire.Fire()
