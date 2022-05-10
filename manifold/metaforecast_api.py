from distutils.command.build import build
from typing import Optional
import requests


GRAPH_QL_ENDPOINT = "https://metaforecast.org/api/graphql"


def build_query(end_cursor: Optional[str]=None):
    end_str = f"after: \"{end_cursor}\"" if end_cursor is not None else ""
    return """{{
    questions(first: 1000 {end_str}) {{
        edges {{
        node {{
            id
            history {{
            id
            options {{
            name
            probability
            }}
            timestamp
            }}
            title
            url
            description
            options {{
            name
            probability
            }}
            qualityIndicators {{
            numForecasts
            stars
            }}
            timestamp
        }}
        }}
        pageInfo {{
        endCursor
        startCursor
        }}
    }}
    }}""".format(end_str=end_str)


def get_all_questions():
    all_results = []
    first_result = requests.post(GRAPH_QL_ENDPOINT, json={"query": build_query(None)}).json()
    import pdb
    pdb.set_trace()
    end_cursor = first_result['data']['questions']['pageInfo']['endCursor']
    all_results.extend([x['node'] for x in first_result['data']['questions']['edges']])
    while end_cursor:
        new_res = requests.post(GRAPH_QL_ENDPOINT, json={"query": build_query(end_cursor)}).json()
        end_cursor = new_res['data']['questions']['pageInfo']['endCursor']
        all_results.extend([x['node'] for x in new_res['data']['questions']['edges']])
    manifold = [x for x in all_results if x['id'].split('-')[0] == 'manifold']
    return manifold


get_all_questions()
