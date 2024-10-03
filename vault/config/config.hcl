# Configuration du backend de stockage
storage "file" {
  path = "/vault/data"
}

# Configuration des auditeurs
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1  # Désactive TLS pour le développement, activez TLS pour la production
  # tls_cert_file = "/path/to/cert.pem"
  # tls_key_file  = "/path/to/key.pem"
}

# Désactivation de mlock (utilisé pour empêcher le swapping en mémoire)
disable_mlock = true

# Activation de l'interface utilisateur de Vault
ui = true

# Configuration des logs
log_level = "info"
log_format = "json"

# Configuration des télémetries
telemetry {
  prometheus_retention_time = "24h"
  disable_hostname = true
}

# Configuration de la haute disponibilité (exemple avec Consul)
# storage "consul" {
#   address = "127.0.0.1:8500"
#   path    = "vault/"
# }

# Configuration de l'API
api_addr = "http://localhost:8200"

# Rediriger automatiquement les requêtes vers cette adresse
redirect_addr = "http://localhost:8200"

# Pour configurer le mode cluster (pour la haute disponibilité)
# cluster_addr = "https://vault-cluster:8201"

# Configuration des certificats TLS (à utiliser en production)
# tls_cert_file = "/etc/ssl/certs/vault_cert.pem"
# tls_key_file  = "/etc/ssl/private/vault_key.pem"

# Configuration des limites de ressources
resource_limits {
  max_heap_size = "2G"
}
