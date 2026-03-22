"""
认证端点
"""
from fastapi import APIRouter, HTTPException, status, Depends

from app.models import RegisterRequest, LoginRequest, AuthResponse, User
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.db.repositories import UserRepository
from app.auth.dependencies import get_current_user
from app.auth.jwt import TokenPayload

router = APIRouter(prefix="/api/auth", tags=["auth"])

user_repo = UserRepository()


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest) -> AuthResponse:
    """
    用户注册

    - **username**: 用户名（3-50字符）
    - **password**: 密码（至少6位）
    """
    # 检查用户名是否已存在
    existing_user = await user_repo.find_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 哈希密码
    password_hash = hash_password(request.password)

    # 创建用户
    user = await user_repo.create(request.username, password_hash)

    # 生成 token
    token = create_access_token(user.id, user.username)

    return AuthResponse(
        user=User(
            id=user.id,
            username=user.username,
            created_at=user.created_at
        ),
        token=token
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码
    """
    # 查找用户
    user = await user_repo.find_by_username(request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成 token
    token = create_access_token(user.id, user.username)

    return AuthResponse(
        user=User(
            id=user.id,
            username=user.username,
            created_at=user.created_at
        ),
        token=token
    )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user)
) -> User:
    """
    获取当前用户信息

    需要认证
    """
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return User(
        id=user.id,
        username=user.username,
        created_at=user.created_at
    )
