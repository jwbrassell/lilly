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
