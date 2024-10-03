from vaulthelpers import VaultHelper

vault = VaultHelper()

def get_secret(path):
    return vault.get_secret(path)
