from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Updated imports to reflect new model structure
from ..models.auth_model import User, UserCreate, Token
from ..models.response import ResponseModel
from ..services.auth_service import AuthService, get_current_active_user
from ..core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_auth_service(service: AuthService = Depends(AuthService)):
    return service

@router.post("/register", response_model=ResponseModel[User], status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    service: AuthService = Depends(get_auth_service)
):
    """
    Endpoint to register a new user.
    """
    user_dict = service.register_user(user_data)
    
    # Convert DB data to the Pydantic model for the response
    if "_id" in user_dict:
        user_dict["_id"] = str(user_dict["_id"])
    user_response_data = User.model_validate(user_dict)
    
    return ResponseModel(
        status="success",
        message="User registered successfully.",
        status_code=status.HTTP_201_CREATED,
        data=user_response_data
    )

@router.post("/login", response_model=ResponseModel[Token])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """
    Endpoint to authenticate and get a JWT access token.
    """
    user_dict = service.authenticate_user(form_data.username, form_data.password)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_dict["username"]}, expires_delta=access_token_expires
    )
    
    token_data = Token(access_token=access_token, token_type="bearer")
    
    return ResponseModel(
        status="success",
        message="Login successful.",
        status_code=status.HTTP_200_OK,
        data=token_data
    )

@router.post("/logout", response_model=ResponseModel)
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint for user logout. In a stateless JWT setup, this is mainly
    for the client to know it should discard the token.
    """
    return ResponseModel(
        status="success",
        message="Logout successful. Please discard your token on the client side.",
        status_code=status.HTTP_200_OK
    )

@router.get("/users/me", response_model=ResponseModel[User])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Protected endpoint to get the current authenticated user's details.
    """
    return ResponseModel(
        status="success",
        status_code=status.HTTP_200_OK,
        data=current_user
    )

