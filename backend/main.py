
from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from auth import get_current_user

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from database import get_db

from database import engine, Base, get_db
from models import User

from schemas import (
    RegisterUser,
    LoginUser,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UpdateUser
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    generate_token,
     admin_required
)

from email_service import (
    send_verification_email,
    send_reset_email
)

# Create tables
Base.metadata.create_all(bind=engine)
def create_admin(db: Session):

    admin = (
        db.query(User)
        .filter(User.email == "admin@gmail.com")
        .first()
    )

    if not admin:
        admin_user = User(
            first_name="System",
            middle_name="",
            last_name="Admin",
            full_name="System Admin",
            email="admin@gmail.com",
            mobile="9999999999",
            password_hash=hash_password("Admin@123"),
            role="admin",
            is_verified=True,
            is_active=True
        )

        db.add(admin_user)
        db.commit()

db = next(get_db())
try:
    create_admin(db)
finally:
    db.close()
app = FastAPI()



#  CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"         
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ROOT 
@app.get("/")
def root():
    return {
        "message": "Auth API running with PostgreSQL"
    }

# ADMIN - GET ALL USERS

@app.get("/admin/users")
def get_all_users( 
    db: Session = Depends(get_db),
     current_user:User=Depends(admin_required)
):

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role,
            "status": user.status
        }
        for user in users
    ]


#  update user
@app.put("/admin/users/{user_id}")
def update_user(
    user_id: int,
    data: UpdateUser,
    db: Session = Depends(get_db),
     current_user:User=Depends(admin_required)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if data.full_name is not None:
        user.full_name = data.full_name

    if data.email is not None:
        user.email = data.email

    if data.mobile is not None:
        user.mobile = data.mobile

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "User updated successfully",
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "mobile": user.mobile,
           
        }
    }
    
#deactive user
@app.patch("/admin/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "deactive"
    user.is_active=False

    # print("Status Before Commit:", user.status)
    db.commit()
    db.refresh(user)

    # print("Status After Commit:", user.status)

    return {
        "success": True,
        "message": "User deactivated successfully",
        "status":user.status
    }

#activate users
@app.patch("/admin/users/{user_id}/activate")
def activate_user(
    user_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(admin_required)
):
    user =db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="USer not found")

    user.status="active"
    user.is_active=True

    db.commit()
    db.refresh(user)

    return {
        "success":True,
        "message":"User Activated Successfully",
        "status":user.status
    }

#  REGISTER 
@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()

        if existing_user:
            return {"success": False, "message": "Email already exists"}

        full_name = (
            f"{user.first_name} "
            f"{user.middle_name + ' ' if user.middle_name else ''}"
            f"{user.last_name}"
        ).strip()

        verification_token = generate_token()

        new_user = User(
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            full_name=full_name,
            email=user.email,
            mobile=user.mobile,
            password_hash=hash_password(user.password),
            role="user",
            is_verified=False,
            is_active=False,
            verification_token=verification_token
        )
        # print("GENERATED TOKEN:", verification_token)
        # print("USER OBJECT TOKEN:", new_user.verification_token)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        send_verification_email(new_user.email, verification_token)

        return {
            "success": True,
            "message": "Registration successful. Please verify your email."
        }
        

    except Exception as e:
        print("REGISTER ERROR:", e)
        db.rollback()
        return {
            "success": False,
            "message": str(e)
        }

#  VERIFY EMAIL 

@app.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.verification_token == token)
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "Invalid or expired token"
        }

    user.is_verified = True
    user.is_active = True
    user.verification_token = None

    db.commit()

    return {
        "success": True,
        "message": "Email verified successfully"
    }


#  LOGIN 

@app.post("/login")
def login(
    user: LoginUser,
    db: Session = Depends(get_db)
):
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        return {
            "success": False,
            "message": "User not found"
        }

    if not db_user.is_verified:
        return {
            "success": False,
            "message": "Please verify your email first"
        }

    if not db_user.is_active:
        return {
            "success": False,
            "message": "Account is inactive"
        }

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        return {
            "success": False,
            "message": "Wrong password"
        }

    db_user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(
        data={
            "email": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "success": True,
        "token": access_token,
        "user": {
            "id": db_user.id,
            "name": db_user.full_name,
            "email": db_user.email,
            "role": db_user.role
        }
    }


#  FORGOT PASSWORD 

@app.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "Email not found"
        }

    reset_token = generate_token()

    user.reset_token = reset_token
    db.commit()

    send_reset_email(
        request.email,
        reset_token
    )

    return {
        "success": True,
        "message": "Reset link sent successfully"
    }


#  RESET PASSWORD 

@app.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.reset_token == request.token)
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "Invalid or expired token"
        }

    user.password_hash = hash_password(
        request.new_password
    )

    user.reset_token = None

    db.commit()

    return {
        "success": True,
        "message": "Password reset successful"
        
    }

