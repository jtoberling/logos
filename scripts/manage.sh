#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       Logos Service Management Script                       ║
# ║        Management and monitoring tool for Logos MCP components           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGOS_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$LOGOS_ROOT/deploy/docker/docker-compose.yml"
DOCKER_COMPOSE_PORTEINER_FILE="$LOGOS_ROOT/deploy/docker/docker-compose.portainer.yml"

# Color codes for output (compatible with most terminals)
if [[ -t 1 ]] && [[ -n "$TERM" ]] && [[ "$TERM" != "dumb" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    # Disable colors if not in a terminal or dumb terminal
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    MAGENTA=''
    CYAN=''
    BOLD=''
    RESET=''
fi

# Service information mapping
declare -A SERVICE_INFO=(
    ["qdrant"]="Vector Database|6333,6334|http://localhost:6333"
    ["logos-mcp"]="MCP Server|6335|http://localhost:6335"
    ["ollama"]="LLM Service|11434|http://localhost:11434"
    ["lmstudio"]="LLM Service|1234|http://localhost:1234"
)

# Function to print colored messages
print_message() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${RESET}"
}

# Function to print header
print_header() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}║${RESET}${BOLD}                          LOGOS SERVICE MANAGER${RESET}${CYAN}                          ║${RESET}"
    echo -e "${CYAN}║${RESET}${BOLD}                Digital Personality & Memory Engine${RESET}${CYAN}                     ║${RESET}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════════╝${RESET}"
    echo
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_message "${RED}" "❌ Docker is not running or not accessible"
        print_message "${YELLOW}" "   Please start Docker and try again"
        return 1
    fi
    return 0
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        print_message "${RED}" "❌ docker-compose is not available"
        print_message "${YELLOW}" "   Please install docker-compose and try again"
        return 1
    fi
    return 0
}

# Function to get service status
get_service_status() {
    local service="$1"
    local container_name

    # Map service names to container names
    case "$service" in
        "qdrant")
            container_name="logos-memory"
            ;;
        "logos-mcp")
            container_name="logos-mcp-server"
            ;;
        "ollama")
            container_name="logos-ollama"
            ;;
        "lmstudio")
            container_name="logos-lmstudio"
            ;;
        *)
            echo "unknown"
            return
            ;;
    esac

    # Check if container exists and is running
    if docker ps --filter "name=$container_name" --format "{{.Names}}" | grep -q "^$container_name$"; then
        echo "running"
    elif docker ps -a --filter "name=$container_name" --format "{{.Names}}" | grep -q "^$container_name$"; then
        echo "stopped"
    else
        echo "not_created"
    fi
}

# Function to get service uptime
get_service_uptime() {
    local service="$1"
    local container_name

    case "$service" in
        "qdrant")
            container_name="logos-memory"
            ;;
        "logos-mcp")
            container_name="logos-mcp-server"
            ;;
        "ollama")
            container_name="logos-ollama"
            ;;
        "lmstudio")
            container_name="logos-lmstudio"
            ;;
        *)
            echo "N/A"
            return
            ;;
    esac

    local uptime
    uptime=$(docker ps --filter "name=$container_name" --format "{{.RunningFor}}" 2>/dev/null)
    echo "${uptime:-N/A}"
}

# Function to show running services status
show_service_status() {
    print_message "${YELLOW}" "🔍 LOGOS SERVICES STATUS"
    echo

    if ! check_docker; then
        return 1
    fi

    # Print table header
    echo "+----------------+---------------------+--------+-------------+-------------------------+"
    printf "| %-14s | %-19s | %-6s | %-11s | %-23s |\n" "SERVICE" "DESCRIPTION" "PORTS" "STATUS" "URL"
    echo "+----------------+---------------------+--------+-------------+-------------------------+"

    for service in "${!SERVICE_INFO[@]}"; do
        IFS='|' read -r display_name ports url <<< "${SERVICE_INFO[$service]}"

        local status
        status=$(get_service_status "$service")

        # Color code status
        case "$status" in
            "running")
                status_colored="${GREEN}running${RESET}"
                ;;
            "stopped")
                status_colored="${RED}stopped${RESET}"
                ;;
            "not_created")
                status_colored="${YELLOW}not created${RESET}"
                ;;
            *)
                status_colored="${YELLOW}$status${RESET}"
                ;;
        esac

        printf "| %-14s | %-19s | %-6s | %-11s | %-23s |\n" \
               "$service" "$display_name" "$ports" "$status_colored" "$url"
    done

    echo "+----------------+---------------------+--------+-------------+-------------------------+"
    echo
}

# Function to start all services
start_services() {
    print_message "${YELLOW}" "🚀 Starting Logos services..."

    if ! check_docker || ! check_docker_compose; then
        return 1
    fi

    cd "$SCRIPT_DIR/docker"

    if docker-compose ps | grep -q "logos"; then
        print_message "${BLUE}" "Services are already running"
        return 0
    fi

    print_message "${BLUE}" "Starting core services (Qdrant + Logos MCP)..."
    docker-compose up -d qdrant logos-mcp

    if [ $? -eq 0 ]; then
        print_message "${GREEN}" "✅ Core services started successfully"
        print_message "${CYAN}" "   📊 Qdrant: http://localhost:6333"
        print_message "${CYAN}" "   🧠 Logos MCP: http://localhost:6335"
    else
        print_message "${RED}" "❌ Failed to start services"
        return 1
    fi
}

# Function to start LLM services
start_llm_services() {
    print_message "${YELLOW}" "🤖 Starting LLM services..."

    if ! check_docker || ! check_docker_compose; then
        return 1
    fi

    cd "$SCRIPT_DIR/docker"

    print_message "${BLUE}" "Starting LLM services (Ollama + LMStudio)..."
    docker-compose --profile llm up -d

    if [ $? -eq 0 ]; then
        print_message "${GREEN}" "✅ LLM services started successfully"
        print_message "${CYAN}" "   🦙 Ollama: http://localhost:11434"
        print_message "${CYAN}" "   🎭 LMStudio: http://localhost:1234"
    else
        print_message "${RED}" "❌ Failed to start LLM services"
        return 1
    fi
}

# Function to stop services
stop_services() {
    print_message "${YELLOW}" "🛑 Stopping Logos services..."

    if ! check_docker || ! check_docker_compose; then
        return 1
    fi

    cd "$SCRIPT_DIR/docker"

    docker-compose down

    if [ $? -eq 0 ]; then
        print_message "${GREEN}" "✅ Services stopped successfully"
    else
        print_message "${RED}" "❌ Failed to stop services"
        return 1
    fi
}

# Function to show service logs
show_logs() {
    if ! check_docker; then
        return 1
    fi

    echo
    print_message "${YELLOW}" "Select service to view logs:"
    echo -e "  ${MAGENTA}1${RESET} - Qdrant Database"
    echo -e "  ${MAGENTA}2${RESET} - Logos MCP Server"
    echo -e "  ${MAGENTA}3${RESET} - Ollama (if running)"
    echo -e "  ${MAGENTA}4${RESET} - LMStudio (if running)"
    echo -e "  ${MAGENTA}b${RESET} - Back to main menu"
    echo
    print_message "${CYAN}" "Enter your choice: "
    read -r choice

    local service_name=""
    case $choice in
        1) service_name="logos-memory" ;;
        2) service_name="logos-mcp-server" ;;
        3) service_name="logos-ollama" ;;
        4) service_name="logos-lmstudio" ;;
        b|B) return ;;
        *) print_message "${RED}" "Invalid choice"; return ;;
    esac

    if docker ps -a --filter "name=$service_name" --format "{{.Names}}" | grep -q "^$service_name$"; then
        print_message "${BLUE}" "Showing logs for $service_name (Ctrl+C to exit)..."
        docker logs -f "$service_name"
    else
        print_message "${RED}" "Service $service_name is not available"
    fi
}

# Function to check service health
check_health() {
    print_message "${YELLOW}" "🏥 Checking service health..."

    if ! check_docker; then
        return 1
    fi

    # Check Qdrant health
    if curl -f http://localhost:6333/healthz >/dev/null 2>&1; then
        print_message "${GREEN}" "✅ Qdrant: Healthy"
    else
        print_message "${RED}" "❌ Qdrant: Unhealthy or not running"
    fi

    # Check Logos MCP health
    if timeout 5 bash -c "echo > /dev/tcp/localhost/6335" 2>/dev/null; then
        print_message "${GREEN}" "✅ Logos MCP: Healthy"

        # Try to get version info
        if command -v curl >/dev/null 2>&1; then
            local version
            version=$(curl -s http://localhost:6335/version 2>/dev/null | head -n 1)
            if [ -n "$version" ]; then
                print_message "${CYAN}" "   📋 Version: $version"
            fi
        fi
    else
        print_message "${RED}" "❌ Logos MCP: Unhealthy or not running"
    fi

    # Check optional LLM services
    if timeout 5 bash -c "echo > /dev/tcp/localhost/11434" 2>/dev/null; then
        print_message "${GREEN}" "✅ Ollama: Running"
    else
        print_message "${YELLOW}" "⚠️  Ollama: Not running (optional)"
    fi

    if timeout 5 bash -c "echo > /dev/tcp/localhost/1234" 2>/dev/null; then
        print_message "${GREEN}" "✅ LMStudio: Running"
    else
        print_message "${YELLOW}" "⚠️  LMStudio: Not running (optional)"
    fi
}

# Function to clean up containers and volumes
cleanup() {
    print_message "${YELLOW}" "🧹 Cleaning up Logos containers and volumes..."

    if ! check_docker || ! check_docker_compose; then
        return 1
    fi

    cd "$SCRIPT_DIR/docker"

    print_message "${RED}" "⚠️  This will remove all Logos containers and volumes!"
    print_message "${YELLOW}" "   Data will be permanently lost."
    echo
    print_message "${CYAN}" "Are you sure? (type 'yes' to confirm): "
    read -r confirm

    if [[ "$confirm" != "yes" ]]; then
        print_message "${BLUE}" "Cleanup cancelled"
        return 0
    fi

    print_message "${BLUE}" "Removing containers and volumes..."
    docker-compose down -v --remove-orphans

    if [ $? -eq 0 ]; then
        print_message "${GREEN}" "✅ Cleanup completed"
    else
        print_message "${RED}" "❌ Cleanup failed"
        return 1
    fi
}

# Function to check if semgrep is available
check_semgrep() {
    if ! command -v semgrep >/dev/null 2>&1; then
        print_message "${RED}" "❌ Semgrep is not installed"
        print_message "${YELLOW}" "   Install with: pip install semgrep"
        print_message "${CYAN}" "   Or: pip3 install semgrep"
        return 1
    fi
    return 0
}

# Function to run security scan with semgrep
run_security_scan() {
    print_message "${YELLOW}" "🔒 Running Security Scan with Semgrep..."

    if ! check_semgrep; then
        return 1
    fi

    # Create reports directory
    local reports_dir="reports"
    mkdir -p "$reports_dir"

    # Generate timestamp for report file
    local timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    local report_file="$reports_dir/logos_security_scan_$timestamp.json"

    # Define semgrep rule sets for Python/Docker projects
    local semgrep_configs=("p/owasp-top-ten" "p/secrets" "p/r2c-security-audit")

    print_message "${CYAN}" "🔍 Scanning Logos codebase..."
    print_message "${BLUE}" "   Rule sets: ${semgrep_configs[*]}"
    print_message "${BLUE}" "   Report: $report_file"
    echo

    # Build semgrep command
    local semgrep_cmd="semgrep --json --output=$report_file"
    for config in "${semgrep_configs[@]}"; do
        semgrep_cmd="$semgrep_cmd --config=$config"
    done

    # Add exclusions and optimizations
    semgrep_cmd="$semgrep_cmd --timeout=60 --max-target-bytes=1000000 --metrics=off --max-memory=1000 --jobs=2"
    semgrep_cmd="$semgrep_cmd --exclude='**/node_modules/**' --exclude='**/__pycache__/**' --exclude='**/.*'"
    semgrep_cmd="$semgrep_cmd --exclude='**/coverage/**' --exclude='**/htmlcov/**' --exclude='**/venv/**'"
    semgrep_cmd="$semgrep_cmd --exclude='**/build/**' --exclude='**/dist/**' --exclude='**/reports/**'"

    # Scan the src directory and root level files
    # Only scan files that actually exist
    local scan_targets=("src/" "cli/" "deploy/")
    [[ -f "manage.sh" ]] && scan_targets+=("manage.sh")
    [[ -f "manage-README.md" ]] && scan_targets+=("manage-README.md")
    [[ -f "Dockerfile" ]] && scan_targets+=("Dockerfile")
    [[ -f "docker-compose.yml" ]] && scan_targets+=("docker-compose.yml")
    [[ -f "docker-compose.portainer.yml" ]] && scan_targets+=("docker-compose.portainer.yml")

    semgrep_cmd="$semgrep_cmd ${scan_targets[*]}"

    # Run semgrep
    print_message "${CYAN}" "⏳ Running security analysis..."
    eval "$semgrep_cmd"
    local exit_code=$?

    # Analyze results
    if [[ -f "$report_file" ]]; then
        local findings_count
        findings_count=$(jq '.results | length' "$report_file" 2>/dev/null || echo "0")

        local blocking_count
        blocking_count=$(jq '[.results[] | select(.extra.severity == "ERROR" or .extra.severity == "WARNING")] | length' "$report_file" 2>/dev/null || echo "0")

        print_message "${GREEN}" "✅ Security scan completed"
        print_message "${BLUE}" "   📊 Findings: $findings_count"
        print_message "${BLUE}" "   🚨 Blocking issues: $blocking_count"
        print_message "${BLUE}" "   📄 Report: $report_file"

        if [[ $blocking_count -gt 0 ]]; then
            print_message "${RED}" "⚠️  Review blocking security issues in the report"
        fi

        if [[ $findings_count -eq 0 ]]; then
            print_message "${GREEN}" "🎉 No security issues found!"
        fi
    else
        print_message "${RED}" "❌ Failed to generate security report"
        return 1
    fi

    return $exit_code
}

# Function to show usage information
show_usage() {
    print_header
    print_message "${YELLOW}" "USAGE:"
    echo "  $0 [command]"
    echo
    print_message "${YELLOW}" "COMMANDS:"
    echo "  status     - Show service status"
    echo "  start      - Start core services (Qdrant + MCP)"
    echo "  start-llm  - Start LLM services (Ollama + LMStudio)"
    echo "  stop       - Stop all services"
    echo "  logs       - View service logs"
    echo "  health     - Check service health"
    echo "  security   - Run security scan with Semgrep"
    echo "  cleanup    - Remove containers and volumes"
    echo "  help       - Show this help"
    echo
    print_message "${YELLOW}" "EXAMPLES:"
    echo "  $0 status           # Show current status"
    echo "  $0 start            # Start Logos services"
    echo "  $0 security         # Run security scan"
    echo "  $0 logs             # View logs interactively"
    echo
}

# Function to show interactive menu
show_menu() {
    while true; do
        print_header
        show_service_status

        print_message "${YELLOW}" "Select an option:"
        echo -e "  ${MAGENTA}1${RESET} - ${YELLOW}Start Core Services${RESET}    ${MAGENTA}2${RESET} - ${YELLOW}Start LLM Services${RESET}"
        echo -e "  ${MAGENTA}3${RESET} - ${YELLOW}Stop All Services${RESET}      ${MAGENTA}4${RESET} - ${YELLOW}Service Status${RESET}"
        echo -e "  ${MAGENTA}5${RESET} - ${YELLOW}View Logs${RESET}               ${MAGENTA}6${RESET} - ${YELLOW}Health Check${RESET}"
        echo -e "  ${MAGENTA}7${RESET} - ${YELLOW}Security Scan${RESET}            ${MAGENTA}8${RESET} - ${YELLOW}Cleanup${RESET}                ${MAGENTA}q${RESET} - ${YELLOW}Quit${RESET}"
        echo
        print_message "${CYAN}" "Enter your choice: "
        read -r choice

        case $choice in
            1) start_services ;;
            2) start_llm_services ;;
            3) stop_services ;;
            4) show_service_status ;;
            5) show_logs ;;
            6) check_health ;;
            7) run_security_scan ;;
            8) cleanup ;;
            q|Q) break ;;
            *) print_message "${RED}" "Invalid choice. Please try again." ;;
        esac

        if [[ $choice != "q" && $choice != "Q" ]]; then
            echo
            print_message "${CYAN}" "Press Enter to continue..."
            read -r
        fi
    done
}

# Main script logic
main() {
    # Parse command line arguments
    case "${1:-}" in
        "status")
            print_header
            show_service_status
            ;;
        "start")
            start_services
            ;;
        "start-llm")
            start_llm_services
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "health")
            check_health
            ;;
        "security")
            run_security_scan
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        "")
            # No arguments, show interactive menu
            show_menu
            ;;
        *)
            print_message "${RED}" "Unknown command: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"