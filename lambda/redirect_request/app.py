from util.redirect_util import redirect_response


def lambda_handler(event, context):
    return redirect_response("https://kazutech.jp/")
