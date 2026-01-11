#!/bin/bash
# ============================================================================
# VPS Final Test Script - Pre-Deployment Verification
# Tests all deployment scripts and system components before production
# ============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 VPS Final Test Suite - Pre-Deployment Verification${NC}"
echo "=================================================="

# Test Results Array
TESTS=()
PASSED=0
FAILED=0

add_test() {
    local name="$1"
    local result="$2"
    local message="$3"
    
    TESTS+=("$name|$result|$message")
    if [ "$result" = "PASS" ]; then
        ((PASSED++))
        echo -e "✅ ${GREEN}$name${NC}: $message"
    else
        ((FAILED++))
        echo -e "❌ ${RED}$name${NC}: $message"
    fi
}

# Test 1: Environment Validation
echo -e "\n${YELLOW}🔍 Testing Environment Validation...${NC}"
cd /home/akn/vps/projects/webimar
if ./env.validation.sh .env.example > /dev/null 2>&1; then
    add_test "Environment Validation" "PASS" "Script works correctly"
else
    add_test "Environment Validation" "FAIL" "Validation script has issues"
fi

# Test 2: Docker Build Test (optimized images)
echo -e "\n${YELLOW}🐳 Testing Optimized Docker Builds...${NC}"
if docker build -f docker/Dockerfile.api -t webimar-api-test . > /dev/null 2>&1; then
    IMAGE_SIZE=$(docker images webimar-api-test --format "table {{.Size}}" | tail -n1)
    add_test "Docker API Build" "PASS" "Image built successfully ($IMAGE_SIZE)"
    docker rmi webimar-api-test > /dev/null 2>&1
else
    add_test "Docker API Build" "FAIL" "Build failed"
fi

# Test 3: Dev-Local Script Test
echo -e "\n${YELLOW}🔧 Testing Dev-Local Script...${NC}"
if timeout 30s ./dev-local.sh --test-mode > /dev/null 2>&1; then
    add_test "Dev-Local Script" "PASS" "Starts without errors"
else
    add_test "Dev-Local Script" "FAIL" "Has startup issues"
fi

# Test 4: Dev-Docker Script Test  
echo -e "\n${YELLOW}🐳 Testing Dev-Docker Script...${NC}"
if ./dev-docker.sh --dry-run > /dev/null 2>&1; then
    add_test "Dev-Docker Script" "PASS" "Configuration valid"
else
    add_test "Dev-Docker Script" "FAIL" "Configuration issues"
fi

# Test 5: Backup Script Test
echo -e "\n${YELLOW}💾 Testing Backup Scripts...${NC}"
if /home/akn/vps/scripts/backup-vps-optimized.sh --test-mode > /dev/null 2>&1; then
    add_test "Backup Script" "PASS" "FTP backup configuration valid"
else
    add_test "Backup Script" "FAIL" "Backup configuration issues"
fi

# Test 6: Monitoring Stack Test
echo -e "\n${YELLOW}📊 Testing Monitoring Configuration...${NC}"
cd /home/akn/vps/infrastructure
if docker-compose -f monitoring-complete.yml config > /dev/null 2>&1; then
    add_test "Monitoring Config" "PASS" "Compose configuration valid"
else
    add_test "Monitoring Config" "FAIL" "Compose configuration errors"
fi

# Test 7: Nginx Configuration Test
echo -e "\n${YELLOW}🌐 Testing Nginx Configuration...${NC}"
if docker run --rm -v /home/akn/vps/infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t > /dev/null 2>&1; then
    add_test "Nginx Config" "PASS" "Configuration syntax valid"
else
    add_test "Nginx Config" "FAIL" "Syntax errors found"
fi

# Test 8: SSL Configuration Test
echo -e "\n${YELLOW}🔒 Testing SSL Configuration...${NC}"
if [ -d "/home/akn/vps/infrastructure/ssl" ] && [ -f "/home/akn/vps/infrastructure/nginx/conf.d/webimar.conf" ]; then
    add_test "SSL Setup" "PASS" "SSL directories and config exist"
else
    add_test "SSL Setup" "FAIL" "SSL configuration incomplete"
fi

# Test 9: Scripts Permissions Test
echo -e "\n${YELLOW}🔧 Testing Script Permissions...${NC}"
SCRIPT_ERRORS=0
for script in /home/akn/vps/scripts/*.sh; do
    if [ ! -x "$script" ]; then
        ((SCRIPT_ERRORS++))
    fi
done

if [ $SCRIPT_ERRORS -eq 0 ]; then
    add_test "Script Permissions" "PASS" "All scripts executable"
else
    add_test "Script Permissions" "FAIL" "$SCRIPT_ERRORS scripts not executable"
fi

# Test 10: Port Security Test
echo -e "\n${YELLOW}🔐 Testing Port Security...${NC}"
cd /home/akn/vps/projects/webimar
EXPOSED_DB_PORTS=$(grep -E "^\s*-\s*[\"']?543[2-9]:|^\s*-\s*[\"']?637[0-9]:" docker-compose.yml || true)
if [ -z "$EXPOSED_DB_PORTS" ]; then
    add_test "Port Security" "PASS" "No database ports exposed"
else
    add_test "Port Security" "FAIL" "Database ports still exposed"
fi

# Final Report
echo -e "\n${BLUE}📋 TEST RESULTS SUMMARY${NC}"
echo "=============================="
printf "%-25s %-6s %s\n" "Test Name" "Result" "Message"
echo "------------------------------------------------------"

for test in "${TESTS[@]}"; do
    IFS='|' read -r name result message <<< "$test"
    if [ "$result" = "PASS" ]; then
        printf "%-25s ${GREEN}%-6s${NC} %s\n" "$name" "$result" "$message"
    else
        printf "%-25s ${RED}%-6s${NC} %s\n" "$name" "$result" "$message"
    fi
done

echo "=============================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

# Overall Result
if [ $FAILED -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}ALL TESTS PASSED!${NC}"
    echo -e "✅ System ready for production deployment"
    exit 0
else
    echo -e "\n⚠️  ${YELLOW}$FAILED TESTS FAILED${NC}"
    echo -e "🔧 Please fix issues before production deployment"
    exit 1
fi