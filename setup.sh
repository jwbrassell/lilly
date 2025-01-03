#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install required packages
pip install -r requirements.txt

# Clean up any existing vault files
rm -rf "${SCRIPT_DIR}/vault"
rm -f "${SCRIPT_DIR}/vault.zip"

# Create vault directory structure
mkdir -p "${SCRIPT_DIR}/vault/data"

# Download and install Vault locally
cd "${SCRIPT_DIR}/vault"
curl -o vault.zip https://releases.hashicorp.com/vault/1.13.3/vault_1.13.3_darwin_amd64.zip
unzip vault.zip
rm vault.zip
chmod +x vault

# Create Vault config
cat > config.hcl << EOL
storage "file" {
  path = "${SCRIPT_DIR}/vault/data"
}

listener "tcp" {
  address     = "127.0.0.1:5011"
  tls_disable = 1
}

ui = true
EOL

# Set Vault address
VAULT_ADDR='http://127.0.0.1:5011'
export VAULT_ADDR

# Create vault management script
cat > "${SCRIPT_DIR}/vault_manager.sh" << 'EOL'
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="${SCRIPT_DIR}/vault"
VAULT_BIN="${VAULT_DIR}/vault"
VAULT_PID_FILE="${VAULT_DIR}/vault.pid"
VAULT_LOG="${VAULT_DIR}/vault.log"
VAULT_INIT="${VAULT_DIR}/init.txt"
VAULT_ADDR='http://127.0.0.1:5011'
export VAULT_ADDR

start_vault() {
    if [ -f "$VAULT_PID_FILE" ]; then
        PID=$(cat "$VAULT_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Vault is already running with PID $PID"
            return
        fi
    fi
    
    # Ensure log file exists
    mkdir -p "$VAULT_DIR"
    touch "$VAULT_LOG"
    
    "$VAULT_BIN" server -config="${VAULT_DIR}/config.hcl" > "$VAULT_LOG" 2>&1 &
    echo $! > "$VAULT_PID_FILE"
    echo "Started Vault with PID $(cat "$VAULT_PID_FILE")"
    sleep 2
}

stop_vault() {
    if [ -f "$VAULT_PID_FILE" ]; then
        PID=$(cat "$VAULT_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            rm "$VAULT_PID_FILE"
            echo "Stopped Vault process $PID"
        else
            echo "Vault process $PID not found"
            rm "$VAULT_PID_FILE"
        fi
    else
        echo "Vault PID file not found"
    fi
}

initialize_vault() {
    # Wait for vault to be ready
    sleep 2
    
    # Check if vault is initialized
    if ! "$VAULT_BIN" operator init -status > /dev/null 2>&1; then
        echo "Initializing Vault..."
        # Initialize vault and save output
        "$VAULT_BIN" operator init -key-shares=1 -key-threshold=1 > "$VAULT_INIT"
        
        # Extract keys from the output
        UNSEAL_KEY=$(grep "Unseal Key 1:" "$VAULT_INIT" | awk '{print $NF}')
        ROOT_TOKEN=$(grep "Initial Root Token:" "$VAULT_INIT" | awk '{print $NF}')
        
        # Unseal vault
        "$VAULT_BIN" operator unseal "$UNSEAL_KEY"
        
        # Export token for use
        export VAULT_TOKEN="$ROOT_TOKEN"
        echo "Vault initialized and unsealed"
    else
        echo "Vault already initialized"
        if [ ! -f "$VAULT_INIT" ]; then
            echo "Error: $VAULT_INIT not found"
            return 1
        fi
        # Extract key from the output
        UNSEAL_KEY=$(grep "Unseal Key 1:" "$VAULT_INIT" | awk '{print $NF}')
        
        # Unseal vault
        "$VAULT_BIN" operator unseal "$UNSEAL_KEY"
        echo "Vault unsealed"
    fi
}

case "$1" in
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
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
EOL

chmod +x "${SCRIPT_DIR}/vault_manager.sh"

# Create .env file with Vault configuration
cat > "${SCRIPT_DIR}/.env" << EOL
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_RUN_PORT=5010
VAULT_ADDR=${VAULT_ADDR}
DATABASE_URL=sqlite:///local.db
EOL

# Start vault temporarily to initialize it
"${SCRIPT_DIR}/vault_manager.sh" start
sleep 2

# Get the token and add it to .env if init.txt exists
if [ -f "${SCRIPT_DIR}/vault/init.txt" ]; then
    VAULT_TOKEN=$(grep "Initial Root Token:" "${SCRIPT_DIR}/vault/init.txt" | awk '{print $NF}')
    echo "VAULT_TOKEN=${VAULT_TOKEN}" >> "${SCRIPT_DIR}/.env"
fi

# Stop vault since Flask will manage it
"${SCRIPT_DIR}/vault_manager.sh" stop

# Initialize the database
cd "${SCRIPT_DIR}"
flask db init
flask db migrate
flask db upgrade

echo "Setup complete!"
echo "Vault is configured in production mode:"
echo "- UI will be available at: ${VAULT_ADDR}/ui"
echo "- Storage: Persistent (vault/data)"
echo "- Credentials saved in: vault/init.txt"
echo "- Process managed by Flask"
