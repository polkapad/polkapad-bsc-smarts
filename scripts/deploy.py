from brownie import accounts, network, config, Locker, PolkapadERC20, Whitelist

OWNER = (0, "owner_pk")
MULTISIG = (1, "multisig_pk")
BURNER = (2, "burner_pk")

def deploy_whitelist(owner, multisig, default_max_allocation_size):
    contract = Whitelist.deploy(
        multisig,
        { "from": owner })

    contract.setDefaultAllocationSize(default_max_allocation_size, { "from": multisig })

    return contract

def deploy_plpd(owner, multisig):
    contract = PolkapadERC20.deploy(
        "Polkapad", 
        "PLPD", 
        multisig, 
        { "from": owner })

    return contract

def deploy_locker(owner, multisig, burner, polkapad, whitelist):
    contract = Locker.deploy(
        multisig,
        burner,
        config["addresses"]["dot"], 
        config["addresses"]["feed"],
        polkapad,
        whitelist,
        { "from": owner })

    contract.setPlpdPrice(0.3 * 1e18, { "from": multisig })

    return contract

def get_account(account):
    dev_index = account[0]
    private_key = account[1]
    
    if network.show_active() == "development":
        return accounts[dev_index]
    else:
        return accounts.add(config["addresses"][private_key])

def deploy(owner, multisig, burner):
    default_max_allocation_size = 100 * 1e18

    whitelist = deploy_whitelist(owner, multisig, default_max_allocation_size)
    plpd = deploy_plpd(owner, multisig)
    locker = deploy_locker(owner, multisig, burner, plpd, whitelist)

    plpd.setLockerContractAddress(locker, { "from": multisig })

def main():
    owner = get_account(OWNER)
    multisig = get_account(MULTISIG)
    burner = get_account(BURNER)

    deploy(owner, multisig, burner)