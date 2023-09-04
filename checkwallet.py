import requests
import json

verus_explorer_url = "https://explorer.verus.io/ext/getaddress/"


def search_wallet(wallet):
    if wallet == "":
        print("Please provide a wallet address")
        return

    wallet_url = verus_explorer_url + wallet
    req = requests.get(wallet_url)
    response = json.loads(req.text)
    try:
        balance = response["balance"]
        if balance == 0:
            return "Wallet Found"
    except:
        return "Error"
