#!/bin/sh

# Variables
VAULT_ADDR="http://127.0.0.1:8200"
VAULT_INIT_FILE="/vault/data/vault-init.json"

# Démarrer Vault en arrière-plan
vault server -config=/vault/config/config.hcl &

# Attendre que Vault soit prêt
echo "Attente que Vault soit prêt à être initialisé..."
sleep 5

# Vérifier si Vault est déjà initialisé
vault status > /dev/null 2>&1
if [ $? -eq 2 ]; then
  echo "Vault n'est pas initialisé. Initialisation en cours..."
  
  # Initialiser Vault et sauvegarder les clés d'unseal et le root token
  vault operator init -key-shares=1 -key-threshold=1 -format=json > $VAULT_INIT_FILE
  
  # Extraire la clé d'unseal et le root token avec jq
  UNSEAL_KEY=$(cat $VAULT_INIT_FILE | jq -r ".unseal_keys_b64[0]")
  ROOT_TOKEN=$(cat $VAULT_INIT_FILE | jq -r ".root_token")
  
  # Afficher la clé d'unseal et le root token
  echo "Clé d'unseal : $UNSEAL_KEY"
  echo "Root token : $ROOT_TOKEN"

  cat $VAULT_INIT_FILE
  
  # Déverrouiller Vault (Unseal) avec la clé passée directement
  vault operator unseal $UNSEAL_KEY
  
  # Login avec le root token
  VAULT_TOKEN=$ROOT_TOKEN vault login $ROOT_TOKEN

  echo "Vault initialisé et déverrouillé."
else
  echo "Vault est déjà initialisé."
  
  # Si Vault est initialisé mais scellé, le déverrouiller
  if vault status | grep -q "sealed"; then
    echo "Déverrouillage de Vault..."
    UNSEAL_KEY=$(cat $VAULT_INIT_FILE | jq -r ".unseal_keys_b64[0]")
    
    # Afficher la clé d'unseal
    echo "Clé d'unseal : $UNSEAL_KEY"
    
    # Déverrouiller Vault sans interaction
    vault operator unseal $UNSEAL_KEY
    echo "Vault déverrouillé."
  fi
fi

# Garder le processus en cours
wait
