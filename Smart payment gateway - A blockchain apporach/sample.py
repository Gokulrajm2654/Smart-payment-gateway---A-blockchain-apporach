from web3 import Web3

url = "HTTP://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(url))

from_acc = "0xcc45eB0ADB61E019A993979b53C1348eBC19f769"
to_acc   = "0x396080F9F6E67BeC6A6E774b84f7E15f76B133A9"

priv_key = "0x4acd342d2ea7ec3535947f419506015b03c82bdcf6ab8d6f2e6ca355da40c447"


#Get the nonce to prevent duplicate transactions
nonce = web3.eth.get_transaction_count(from_acc)

#Build the Transaction:
tx = {
    'nonce': nonce,
    'to': to_acc,
    'value': web3.to_wei(1, 'ether'),
    'gas': 2_000_0 ,
    'gasPrice': web3.to_wei('50', 'gwei')
}

#Sign Transaction
signed_tx = web3.eth.account.sign_transaction(tx, priv_key)
tx_hash = (web3.eth.send_raw_transaction(signed_tx.rawTransaction))
print(web3.to_hex(tx_hash))



