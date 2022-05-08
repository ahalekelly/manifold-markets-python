graphQLendpoint = "https://metaforecast.org/api/graphql";

def build_query(end_cursor):
    return """{
    questions(first: 1000 {!!end_Cursor ? `after: "${endCursor}"` : ""}) {
        edges {
        node {
            id
            title
            url
            description
            options {
            name
            probability
            }
            qualityIndicators {
            numForecasts
            stars
            }
            timestamp
        }
        }
        pageInfo {
        endCursor
        startCursor
        }
    }
    }""".format(end_cursor=end_cursor)

