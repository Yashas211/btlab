import sys
import cmd
from web3 import Web3


class WalletShell(cmd.Cmd):
    intro = 'Welcome to the ClassCrypto Shell. Type help or ? to list commands.\n'
    prompt = '(crypto) > '

    def __init__(self):
        super().__init__()

        # 1. Initialize the Ghost Blockchain
        # EthereumTesterProvider creates a temporary chain in your RAM.
        # It handles mining, signatures, and gas automatically.
        self.w3 = Web3(Web3.EthereumTesterProvider())

        # 2. Setup "Users"
        # We map friendly names (Alice) to the complex Hex addresses
        # provided by the test environment.
        self.accounts = self.w3.eth.accounts

        self.users = {
            "bank": self.accounts[0],
            "alice": self.accounts[1],
            "bob": self.accounts[2],
            "charlie": self.accounts[3]
        }

        print(
            f"Blockchain initialized with {len(self.users)} users: "
            "Bank, Alice, Bob, Charlie"
        )

    def do_balance(self, arg):
        """
        Check balance of a user.
        Usage: balance <user_name>
        Example: balance alice
        """
        name = arg.lower().strip()

        if name not in self.users:
            print(
                f"Error: User '{name}' not found. "
                f"Available: {list(self.users.keys())}"
            )
            return

        address = self.users[name]

        # Balances are returned in 'Wei' (tiny units),
        # we convert them to 'Ether' for readability.
        wei_balance = self.w3.eth.get_balance(address)
        eth_balance = self.w3.from_wei(wei_balance, 'ether')

        print(f"User: {name.capitalize()}")
        print(f"Address: {address}")
        print(f"Balance: {eth_balance} ETH")

    def do_send(self, arg):
        """
        Send crypto between users.
        Usage: send <from> <to> <amount>
        Example: send bank alice 10
        """
        args = arg.split()

        if len(args) != 3:
            print("Error: Usage is 'send <from> <to> <amount>'")
            return

        sender = args[0].lower()
        receiver = args[1].lower()
        amount = args[2]

        if sender not in self.users or receiver not in self.users:
            print(
                "Error: Unknown user. "
                "Please use: bank, alice, bob, charlie"
            )
            return

        try:
            amount_eth = float(amount)

            sender_addr = self.users[sender]
            receiver_addr = self.users[receiver]

            print(
                f"Processing transaction: "
                f"{sender.capitalize()} -> "
                f"{receiver.capitalize()} ({amount_eth} ETH)..."
            )

            # 1. Submit the Transaction
            # In a real app, you would need the Private Key to sign this.
            # The TesterProvider handles the signing automatically for us.
            tx_hash = self.w3.eth.send_transaction({
                'from': sender_addr,
                'to': receiver_addr,
                'value': self.w3.to_wei(amount_eth, 'ether')
            })

            # 2. Wait for Mining (Validation)
            # The network needs time to include the transaction in a block.
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            print(f"Success! Block #{receipt.blockNumber} mined.")
            print(f"Gas Used: {receipt.gasUsed} (Cost to process)")
            print(f"Tx Hash: {tx_hash.hex()}")

        except ValueError as e:
            print(f"Transaction Failed: {e}")

        except Exception as e:
            print(f"System Error: {e}")

    def do_chain(self, arg):
        """
        Inspect the latest block in the chain.
        """
        latest = self.w3.eth.get_block('latest')

        print("\n--- LATEST BLOCK ---")
        print(f"Block Number: {latest.number}")
        print(f"Block Hash: {latest.hash.hex()}")
        print(f"Transactions: {len(latest.transactions)}")
        print("--------------------")

    def do_exit(self, arg):
        """Exit the shell."""
        print("Closing connection...")
        return True


if __name__ == '__main__':
    try:
        WalletShell().cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
