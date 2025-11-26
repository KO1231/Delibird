import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

# クエリパラメータの最大長制限
_MAX_QUERY_KEY_LENGTH = int(os.environ["MAX_QUERY_KEY_LENGTH"])
_MAX_QUERY_VALUE_LENGTH = int(os.environ["MAX_QUERY_VALUE_LENGTH"])
_MAX_TOTAL_QUERY_PARAMS = int(os.environ["MAX_TOTAL_QUERY_PARAMS"])


def queried_origin(origin: str, data: dict[str, list[str]], query_whitelist: set[str]) -> str:
    """クエリパラメータを付与したURLを返す"""
    parsed_url = urlparse(origin)
    existing_query_pairs = [(k, v) for k, v in parse_qsl(parsed_url.query, strict_parsing=True)]

    # 新しいクエリパラメータの検証とフィルタリング
    if ((new_query_length := len(data)) > _MAX_TOTAL_QUERY_PARAMS) or (
            (new_query_length := sum(len(v) for v in data.values())) > _MAX_TOTAL_QUERY_PARAMS):
        raise ValueError(f"Amount of new query parameters exceeds limit: count={new_query_length}")

    new_query_pairs = []
    for k, v_l in data.items():
        # キーの長さチェック
        if len(k) > _MAX_QUERY_KEY_LENGTH:
            raise ValueError(f"Query parameter key length exceeds limit: length={len(k)}")
        for v in v_l:
            if len(v) > _MAX_QUERY_VALUE_LENGTH:
                raise ValueError(f"Query parameter value length exceeds limit: length={len(v)}")
            new_query_pairs.append((k, v))

    query_pairs = existing_query_pairs + new_query_pairs
    if len(query_whitelist) > 0:
        # ホワイトリストフィルタリング
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
