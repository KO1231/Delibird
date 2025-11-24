from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


def queried_origin(origin: str, data: dict[str, list[str]], query_whitelist: set[str]) -> str:
    """クエリパラメータを付与したURLを返す"""
    parsed_url = urlparse(origin)

    existing_query_pairs = [(k, v) for k, v in parse_qsl(parsed_url.query, strict_parsing=True)]
    new_query_pairs = [(k, v) for k, v_l in data.items() for v in v_l]

    query_pairs = existing_query_pairs + new_query_pairs
    if len(query_whitelist) > 0:
        query_pairs = [(k, v) for k, v in query_pairs if k in query_whitelist]

    query_string = urlencode(query_pairs, doseq=False)
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        query_string,
        parsed_url.fragment
    ))
