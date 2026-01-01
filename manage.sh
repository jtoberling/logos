#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       Logos Service Management Script                     ║
# ║        Management and monitoring tool for Logos MCP components            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGOS_ROOT="$SCRIPT_DIR"
DOCKER_COMPOSE_FILE="$LOGOS_ROOT/deploy/docker/docker-compose.yml"
DOCKER_COMPOSE_PORTEINER_FILE="$LOGOS_ROOT/deploy/docker/docker-compose.portainer.yml"

# Color codes for output (compatible with most terminals)
# Respect NO_COLOR and FORCE_COLOR environment variables
if [[ "${NO_COLOR:-0}" == "1" ]] || [[ "${FORCE_COLOR:-1}" == "0" ]]; then
    # Colors explicitly disabled
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    MAGENTA=''
    CYAN=''
    BOLD=''
    RESET=''
elif [[ -n "$TERM" ]] && [[ "$TERM" != "dumb" ]] && [[ "$TERM" != "unknown" ]]; then
    # Enable colors for proper terminals
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    # Disable colors for dumb/unknown terminals
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
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo -e "${BOLD}║                          LOGOS SERVICE MANAGER                            ║${RESET}"
    echo -e "${BOLD}║                Digital Personality & Memory Engine                        ║${RESET}"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
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

    # Print table header (SERVICE=14, DESCRIPTION=19, PORTS=11, STATUS=15, URL=23)
    echo "+----------------+---------------------+------------+---------------+-------------------------+"
    printf "| %-14s | %-19s | %-11s | %-15s | %-23s |\n" "SERVICE" "DESCRIPTION" "PORTS" "STATUS" "URL"
    echo "+----------------+---------------------+------------+---------------+-------------------------+"

    for service in "${!SERVICE_INFO[@]}"; do
        IFS='|' read -r display_name ports url <<< "${SERVICE_INFO[$service]}"

        local status
        status=$(get_service_status "$service")

        # Determine status color and symbol
        local status_color=""
        local status_text="$status"
        case "$status" in
            "running")
                status_color="$GREEN"
                status_text="running"
                ;;
            "stopped")
                status_color="$RED"
                status_text="stopped"
                ;;
            "not_created")
                status_color="$YELLOW"
                status_text="not created"
                ;;
            *)
                status_color="$YELLOW"
                ;;
        esac

        printf "| %-14s | %-19s | %-11s | ${status_color}%-15s${RESET} | %-23s |\n" \
               "$service" "$display_name" "$ports" "$status_text" "$url"
    done

    echo "+----------------+---------------------+------------+---------------+-------------------------+"
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

# Function to start CLI
start_cli() {
    print_message "${YELLOW}" "🚀 Starting Logos CLI..."

    # Check if Python is available
    if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
        print_message "${RED}" "❌ Python is not available"
        print_message "${YELLOW}" "   Please install Python 3.8+ and try again"
        return 1
    fi

    # Check if CLI directory exists
    if [[ ! -d "cli" ]]; then
        print_message "${RED}" "❌ CLI directory not found"
        return 1
    fi

    # Change to CLI directory and run
    cd cli || {
        print_message "${RED}" "❌ Failed to change to CLI directory"
        return 1
    }

    # Check if requirements are installed
    if [[ ! -f "requirements.txt" ]]; then
        print_message "${RED}" "❌ CLI requirements.txt not found"
        return 1
    fi

    print_message "${BLUE}" "   Installing CLI dependencies..."
    if pip install -r requirements.txt >/dev/null 2>&1; then
        print_message "${GREEN}" "   ✅ CLI dependencies installed"
    else
        print_message "${RED}" "   ❌ Failed to install CLI dependencies"
        cd ..
        return 1
    fi

    print_message "${GREEN}" "🎉 CLI is ready!"
    print_message "${CYAN}" "   📖 Run: python cli/cli.py --help"
    cd ..
}

# Function to build Docker image
build_docker() {
    print_message "${YELLOW}" "🏗️ Building Logos Docker image..."

    if ! check_docker; then
        return 1
    fi

    # Check if Dockerfile exists
    if [[ ! -f "Dockerfile" ]]; then
        print_message "${RED}" "❌ Dockerfile not found in current directory"
        return 1
    fi

    local image_tag="logos:latest"
    print_message "${BLUE}" "   Building Docker image: $image_tag"

    if docker build -t "$image_tag" .; then
        print_message "${GREEN}" "   ✅ Docker image built successfully"
        print_message "${CYAN}" "   🏷️ Image tag: $image_tag"
        print_message "${CYAN}" "   🚀 Run: docker run -p 6335:6335 $image_tag"
    else
        print_message "${RED}" "   ❌ Failed to build Docker image"
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

# Function to show last security scan report
show_last_security_scan() {
    print_message "${YELLOW}" "📊 Last Security Scan Report"

    local reports_dir="reports"
    if [[ ! -d "$reports_dir" ]]; then
        print_message "${RED}" "❌ No reports directory found"
        return 1
    fi

    # Find the most recent security scan report
    local last_report
    last_report=$(find "$reports_dir" -name "logos_security_scan_*.json" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

    if [[ -z "$last_report" ]]; then
        print_message "${RED}" "❌ No security scan reports found"
        print_message "${YELLOW}" "   Run: ./manage.sh security"
        return 1
    fi

    # Extract information from the report
    local scan_time
    scan_time=$(basename "$last_report" | sed 's/logos_security_scan_\([0-9]\{8\}\)_\([0-9]\{6\}\)\.json/\1 \2/' | sed 's/\(....\)\(..\)\(..\) \(..\)\(..\)\(..\)/\1-\2-\3 \4:\5:\6/')

    local findings_count
    findings_count=$(jq '.results | length' "$last_report" 2>/dev/null || echo "0")

    local blocking_count
    blocking_count=$(jq '[.results[] | select(.extra.severity == "ERROR" or .extra.severity == "WARNING")] | length' "$last_report" 2>/dev/null || echo "0")

    local rules_count
    rules_count=$(jq '.results | map(.check_id) | unique | length' "$last_report" 2>/dev/null || echo "0")

    print_message "${BLUE}" "   📅 Last scan: $scan_time"
    print_message "${BLUE}" "   📊 Total findings: $findings_count"
    print_message "${BLUE}" "   🚨 Blocking issues: $blocking_count"
    print_message "${BLUE}" "   📋 Rules checked: $rules_count"
    print_message "${BLUE}" "   📄 Report: $last_report"

    if [[ $blocking_count -gt 0 ]]; then
        print_message "${RED}" "⚠️  Review blocking security issues"
        echo
        print_message "${YELLOW}" "Top blocking issues:"
        jq -r '.results[] | select(.extra.severity == "ERROR" or .extra.severity == "WARNING") | "\(.extra.severity): \(.check_id) - \(.path):\(.start.line)"' "$last_report" 2>/dev/null | head -5
    else
        print_message "${GREEN}" "✅ No blocking security issues"
    fi

    echo
    print_message "${CYAN}" "To run a new scan: ./manage.sh security"
}

# Function to show usage information
show_usage() {
    print_header
    print_message "${YELLOW}" "USAGE:"
    echo "  $0 [command]    # Direct command execution"
    echo "  $0              # Interactive menu mode"
    echo
    print_message "${YELLOW}" "COMMANDS:"
    echo "  status            - Show service status"
    echo "  start             - Start core services (Qdrant + MCP)"
    echo "  start-llm         - Start LLM services (Ollama + LMStudio)"
    echo "  start-cli         - Setup and prepare CLI client"
    echo "  build             - Build Docker image"
    echo "  stop              - Stop all services"
    echo "  logs              - View service logs interactively"
    echo "  health            - Check service health"
    echo "  security          - Run security scan with Semgrep"
    echo "  security-report   - Show last security scan results"
    echo "  cleanup           - Remove containers and volumes"
    echo "  help              - Show this help"
    echo
    print_message "${YELLOW}" "INTERACTIVE MENU HOTKEYS:"
    print_message "${CYAN}"   "  Service Control: s=start, l=llm, c=cli, b=build, q=stop, t=status"
    print_message "${CYAN}"   "  Monitoring:      v=logs, h=health, r=security, p=report, u=cleanup"
    print_message "${RED}"    "  System:          ?=help, x=exit"
    echo
    print_message "${YELLOW}" "EXAMPLES:"
    echo "  $0                # Launch interactive menu"
    echo "  $0 status         # Show current status"
    echo "  $0 start          # Start Logos services"
    echo "  $0 start-cli      # Setup CLI client"
    echo "  $0 build          # Build Docker image"
    echo "  $0 security       # Run security scan"
    echo "  $0 logs           # View logs interactively"
    echo
}

# Function to show interactive menu
show_menu() {
    while true; do
        print_header
        show_service_status

        echo
        print_message "${BOLD}${YELLOW}" "╔══════════════════════ SERVICE CONTROL ══════════════════════╗"
        echo -e "${BOLD}${YELLOW}║${RESET}  ${MAGENTA}s${RESET} - Start Core Services     ${MAGENTA}l${RESET} - Start LLM Services     ${MAGENTA}c${RESET} - Setup CLI           ${RESET}${BOLD}${YELLOW}║${RESET}"
        echo -e "${BOLD}${YELLOW}║${RESET}  ${MAGENTA}b${RESET} - Build Docker Image     ${MAGENTA}q${RESET} - Stop All Services     ${MAGENTA}t${RESET} - Service Status      ${RESET}${BOLD}${YELLOW}║${RESET}"
        echo -e "${BOLD}${YELLOW}╚═══════════════════════════════════════════════════════════════╝${RESET}"

        echo
        print_message "${BOLD}${YELLOW}" "╔══════════════════════ MONITORING ═══════════════════════════╗"
        echo -e "${BOLD}${YELLOW}║${RESET}  ${MAGENTA}v${RESET} - View Logs               ${MAGENTA}h${RESET} - Health Check          ${MAGENTA}r${RESET} - Security Scan       ${RESET}${BOLD}${YELLOW}║${RESET}"
        echo -e "${BOLD}${YELLOW}║${RESET}  ${MAGENTA}p${RESET} - Last Security Report   ${MAGENTA}u${RESET} - Cleanup               ${MAGENTA}?${RESET} - Help                ${RESET}${BOLD}${YELLOW}║${RESET}"
        echo -e "${BOLD}${YELLOW}╚═══════════════════════════════════════════════════════════════╝${RESET}"

        echo
        print_message "${BOLD}${RED}" "  [x] Exit / Quit"
        echo
        print_message "${CYAN}" "Choose an option: "
        read -r choice

        case $choice in
            s|S) start_services ;;
            l|L) start_llm_services ;;
            c|C) start_cli ;;
            b|B) build_docker ;;
            q|Q) stop_services ;;
            t|T) show_service_status ;;
            v|V) show_logs ;;
            h|H) check_health ;;
            r|R) run_security_scan ;;
            p|P) show_last_security_scan ;;
            u|U) cleanup ;;
            \?|help|-h|--help) show_usage ;;
            x|X) break ;;
            *) print_message "${RED}" "❌ Invalid choice. Press '?' for help or 'x' to exit." ;;
        esac

        if [[ $choice != "x" && $choice != "X" ]]; then
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
        "start-cli")
            start_cli
            ;;
        "build")
            build_docker
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
        "security-report")
            show_last_security_scan
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