# Pycloud
 
**Description**: 

Just a random collection of tools arround ssh to make interacting easier.

**Minicloud Basics**: 

	minicloud.py init ~/your-new-dir
	minicloud.py register 127.0.0.1 -n example_name -e environment -t tag1 tag2 
	minicloud.py shell -n example_name

	minicloud.py init ~/your-new-dir
	minicloud.py register 127.0.0.1 -n example_name -e environment -t tag1 tag2 
	minicloud.py shell -n example_name

**Vault Basics**: 

	vault.py -d ~/vault_file.json --private_key ~/.ssh/id_rsa create
	vault.py -d ~/vault_file.json --private_key ~/.ssh/id_rsa view
		{'Example': 'value'}
	vault.py -d ~/vault_file.json --private_key ~/.ssh/id_rsa get Example
		::Example::
		'value'
	vault.py -d ~/vault_file.json --private_key ~/.ssh/id_rsa edit
		### Opens your favorite editor and lets you change the vault data ###
	vault.py -d ~/vault_file.json --private_key ~/.ssh/id_rsa add_user username ~/other-users-key.pub
