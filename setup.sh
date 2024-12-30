#!/bin/bash

# Install required packages
pip install -r requirements.txt

# Download and install Vault locally
curl -o vault.zip https://releases.hashicorp.com/vault/1.13.3/vault_1.13.3_darwin_amd64.zip
unzip vault.zip
rm vault.zip
chmod +x vault

# Get absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create Vault config
mkdir -p "$PROJECT_DIR/vault/data"
cat > "$PROJECT_DIR/vault/config.hcl" << EOL
storage "file" {
  path = "$PROJECT_DIR/vault/data"
}

listener "tcp" {
  address     = "127.0.0.1:5011"
  tls_disable = 1
}

ui = true
EOL

# Set Vault address
VAULT_ADDR='http://127.0.0.1:5011'

# Create vault management script
cat > "$PROJECT_DIR/vault_manager.sh" << 'EOL'
#!/bin/bash

# Escape spaces in paths
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PID_FILE="${PROJECT_DIR}/vault/vault.pid"
VAULT_ADDR='http://127.0.0.1:5011'
export VAULT_ADDR

start_vault() {
    if [ -f "\$VAULT_PID_FILE" ]; then
        PID=\$(cat "\$VAULT_PID_FILE")
        if ps -p \$PID > /dev/null 2>&1; then
            echo "Vault is already running with PID \$PID"
            return
        fi
    fi
    
    "${PROJECT_DIR}/vault" server -config="${PROJECT_DIR}/vault/config.hcl" > "${PROJECT_DIR}/vault/vault.log" 2>&1 &
    echo \$! > "\$VAULT_PID_FILE"
    echo "Started Vault with PID \$(cat \$VAULT_PID_FILE)"
    sleep 5
}

stop_vault() {
    if [ -f "\$VAULT_PID_FILE" ]; then
        PID=\$(cat "\$VAULT_PID_FILE")
        if ps -p \$PID > /dev/null 2>&1; then
            kill \$PID
            rm "\$VAULT_PID_FILE"
            echo "Stopped Vault process \$PID"
        else
            echo "Vault process \$PID not found"
            rm "\$VAULT_PID_FILE"
        fi
    else
        echo "Vault PID file not found"
    fi
}

initialize_vault() {
    if ! "${PROJECT_DIR}/vault" operator init -status > /dev/null 2>&1; then
        echo "Initializing Vault..."
        "${PROJECT_DIR}/vault" operator init -key-shares=1 -key-threshold=1 > "${PROJECT_DIR}/vault/init.txt"
        UNSEAL_KEY=$(grep "Unseal Key 1" "${PROJECT_DIR}/vault/init.txt" | awk '{print $4}')
        VAULT_TOKEN=$(grep "Initial Root Token" "${PROJECT_DIR}/vault/init.txt" | awk '{print $4}')
        
        # Unseal Vault
        "${PROJECT_DIR}/vault" operator unseal "$UNSEAL_KEY"
        echo "Vault initialized and unsealed"
    else
        echo "Vault already initialized"
        if [ ! -f "${PROJECT_DIR}/vault/init.txt" ]; then
            echo "Error: vault/init.txt not found"
            return 1
        fi
        UNSEAL_KEY=$(grep "Unseal Key 1" "${PROJECT_DIR}/vault/init.txt" | awk '{print $4}')
        "${PROJECT_DIR}/vault" operator unseal "$UNSEAL_KEY"
        echo "Vault unsealed"
    fi
}

case "\$1" in
    start)
        start_vault
        initialize_vault
        ;;
    stop)
        stop_vault
        ;;
    restart)
        stop_vault
        sleep 2
        start_vault
        initialize_vault
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart}"
        exit 1
        ;;
esac
EOL

chmod +x vault_manager.sh

# Create .env file with Vault configuration
cat > .env << EOL
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_RUN_PORT=5010
VAULT_ADDR=${VAULT_ADDR}
DATABASE_URL=sqlite:///local.db
EOL

if [ ! -f "${PROJECT_DIR}/vault/init.txt" ]; then
    # Start vault temporarily to initialize it
    "${PROJECT_DIR}/vault_manager.sh" start
    sleep 2
    
    # Get the token and add it to .env
    VAULT_TOKEN=$(grep "Initial Root Token" "${PROJECT_DIR}/vault/init.txt" | awk '{print $4}')
    echo "VAULT_TOKEN=${VAULT_TOKEN}" >> "${PROJECT_DIR}/.env"
    
    # Stop vault since Flask will manage it
    "${PROJECT_DIR}/vault_manager.sh" stop
fi

# Initialize the database
flask db init
flask db migrate
flask db upgrade

echo "Setup complete!"
echo "Vault is configured in production mode:"
echo "- UI will be available at: ${VAULT_ADDR}/ui"
echo "- Storage: Persistent (vault/data)"
echo "- Credentials saved in: vault/init.txt"
echo "- Process managed by Flask"
