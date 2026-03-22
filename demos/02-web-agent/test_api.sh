#!/bin/bash

# API 端点测试脚本
BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Demo 2 - Web Agent API 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_code=$5

    echo -n "测试: $name ... "

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}通过${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}失败${NC} (预期: $expected_code, 实际: $http_code)"
        echo "  响应: $body"
        ((FAILED++))
        return 1
    fi
}

# 1. 健康检查
echo "1. 健康检查"
test_endpoint "健康检查" "GET" "/api/health" "" "200"
echo ""

# 2. 用户注册（使用时间戳生成唯一用户名）
TIMESTAMP=$(date +%s)
USERNAME="testuser_$TIMESTAMP"
PASSWORD="testpass123"

echo "2. 用户注册"
test_endpoint "用户注册" "POST" "/api/auth/register" "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" "200"
echo ""

# 3. 用户登录
echo "3. 用户登录"
echo -n "测试: 用户登录并获取 Token ... "
login_response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

token=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$token" ]; then
    echo -e "${GREEN}通过${NC}"
    echo "  Token: ${token:0:20}..."
    ((PASSED++))
else
    echo -e "${RED}失败${NC}"
    echo "  响应: $login_response"
    ((FAILED++))
fi
echo ""

# 4. 获取当前用户（需要认证）
if [ -n "$token" ]; then
    echo "4. 认证测试"
    echo -n "测试: 获取当前用户 ... "
    me_response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/auth/me" \
        -H "Authorization: Bearer $token")
    me_code=$(echo "$me_response" | tail -n1)

    if [ "$me_code" -eq "200" ]; then
        echo -e "${GREEN}通过${NC} (HTTP $me_code)"
        ((PASSED++))
    else
        echo -e "${RED}失败${NC} (预期: 200, 实际: $me_code)"
        ((FAILED++))
    fi
    echo ""

    # 5. 获取会话列表
    echo "5. 会话管理"
    echo -n "测试: 获取会话列表 ... "
    sessions_response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/sessions" \
        -H "Authorization: Bearer $token")
    sessions_code=$(echo "$sessions_response" | tail -n1)

    if [ "$sessions_code" -eq "200" ]; then
        echo -e "${GREEN}通过${NC} (HTTP $sessions_code)"
        ((PASSED++))
    else
        echo -e "${RED}失败${NC} (预期: 200, 实际: $sessions_code)"
        ((FAILED++))
    fi
    echo ""

    # 6. 发送消息（SSE 流式）
    echo "6. 聊天功能（SSE 流式输出）"
    echo -n "测试: 发送消息并接收 SSE 流 ... "

    sse_response=$(curl -s -X POST "$BASE_URL/api/chat/stream" \
        -H "Content-Type: application/json" \
        -d "{\"message\":\"你好\"}" \
        --max-time 5)

    if echo "$sse_response" | grep -q "event: token"; then
        echo -e "${GREEN}通过${NC}"
        echo "  收到 SSE 事件流"
        ((PASSED++))
    else
        echo -e "${RED}失败${NC}"
        echo "  响应: $sse_response"
        ((FAILED++))
    fi
    echo ""
fi

# 测试总结
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo "总计: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}有 $FAILED 个测试失败${NC}"
    exit 1
fi
