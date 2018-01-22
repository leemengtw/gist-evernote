import fire
import requests
from secret import BEARER_TOKEN


def query_graphql(payload, token=BEARER_TOKEN, url='https://api.github.com/graphql'):
    headers = {
        'content-type': "application/json",
        'authorization': "Bearer {}".format(BEARER_TOKEN)
    }

    r = requests.request("POST", url, data=payload, headers=headers)
    return r.json()


if __name__ == '__main__':
    fire.Fire()