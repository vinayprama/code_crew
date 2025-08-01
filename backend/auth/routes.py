from fastapi import APIRouter, HTTPException
from .models import UserCreate, UserLogin, PasswordReset
from .utils import hash_password, verify_password, create_jwt
from database.supabase import supabase

router = APIRouter()

@router.post("/register")
def register(user: UserCreate):
    existing = supabase.table("auth_users").select("*").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pwd,
        "security_question": user.security_question,
        "security_answer": user.security_answer,
        "role": user.role,
    }
    supabase.table("auth_users").insert(user_data).execute()
    return {"message": "User registered successfully"}

# @router.post("/login")
# def login(user: UserLogin):
#     result = supabase.table("auth_users").select("*").eq("email", user.email).execute()
#     if not result.data:
#         raise HTTPException(status_code=401, detail="Invalid email")
#     user_db = result.data[0]
#     if not verify_password(user.password, user_db["password"]):
#         raise HTTPException(status_code=401, detail="Invalid password")
#     token = create_jwt({"sub": user_db["email"], "role": user_db["role"]})
#     return {"access_token": token, "token_type": "bearer"}
@router.post("/login")
def login(user: UserLogin):
    result = supabase.table("auth_users").select("*").eq("email", user.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email")
    
    user_db = result.data[0]

    if not verify_password(user.password, user_db["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_jwt({"sub": user_db["email"], "role": user_db["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user_db["role"],  # ✅ Include this
        "email": user_db["email"],  # Optional
        "name": user_db["name"]     # Optional
    }
@router.post("/reset-password")
def reset_password(data: PasswordReset):
    user = supabase.table("auth_users").select("*").eq("email", data.email).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    user = user.data[0]
    if user["security_answer"] != data.security_answer:
        raise HTTPException(status_code=403, detail="Incorrect security answer")
    new_hashed = hash_password(data.new_password)
    supabase.table("auth_users").update({"password": new_hashed}).eq("email", data.email).execute()
    return {"message": "Password reset successfully"}
