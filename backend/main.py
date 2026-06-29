import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException, Request
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import SQLAlchemyError

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
from utils.logger import logger

# Create tables
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize database tables: {str(e)}", exc_info=True)
    raise e

def create_admin(db: Session):
    logger.info("Entering create_admin()")
    try:
        logger.info("Querying database for existing admin user")
        admin = (
            db.query(User)
            .filter(User.email == "admin@gmail.com")
            .first()
        )

        if not admin:
            logger.info("No admin user found. Creating default admin user...")
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
            logger.info("Committing default admin creation to database")
            db.commit()
            logger.info("Default admin user created successfully.")
        else:
            logger.debug("Default admin user already exists.")
        logger.info("Exiting create_admin()")
    except Exception as e:
        logger.exception("Exception in create_admin()")
        logger.info("Rolling back database changes in create_admin()")
        db.rollback()
        raise e

db = next(get_db())
try:
    create_admin(db)
finally:
    db.close()

# Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Entering lifespan()")
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")
    logger.info("Exiting lifespan()")

app = FastAPI(lifespan=lifespan)



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


# Custom Middleware for Request Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Entering log_requests()")
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        log_message = f"Request completed: {request.method} {request.url} | Status: {response.status_code} | Duration: {process_time:.4f}s"
        if response.status_code >= 500:
            logger.error(log_message)
        elif response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        logger.info("Exiting log_requests()")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url} | Error: {str(e)} | Duration: {process_time:.4f}s", exc_info=True)
        logger.exception("Exception in log_requests()")
        raise e

# Custom Exception Handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.info("Entering sqlalchemy_exception_handler()")
    logger.error(f"Database error during {request.method} {request.url}: {str(exc)}", exc_info=True)
    response = JSONResponse(
        status_code=500,
        content={"success": False, "message": "A database error occurred."}
    )
    logger.info("Exiting sqlalchemy_exception_handler()")
    return response

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.info("Entering generic_exception_handler()")
    logger.error(f"Unhandled exception during {request.method} {request.url}: {str(exc)}", exc_info=True)
    response = JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected server error occurred."}
    )
    logger.info("Exiting generic_exception_handler()")
    return response


# ROOT 
@app.get("/")
def root():
    logger.info("Entering root()")
    logger.debug("Root endpoint accessed")
    response_data = {
        "message": "Auth API running with PostgreSQL"
    }
    logger.info("Exiting root()")
    return response_data

# ADMIN - GET ALL USERS

@app.get("/admin/users")
def get_all_users( 
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    logger.info("Entering get_all_users()")
    logger.info(f"Admin {current_user.email} requested list of all users.")
    try:
        logger.info("Querying all users from database")
        users = db.query(User).all()
        logger.debug(f"Retrieved {len(users)} users.")
        res = [
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
        logger.info("Exiting get_all_users()")
        return res
    except Exception as e:
        logger.exception("Exception in get_all_users()")
        raise e


#  update user
@app.put("/admin/users/{user_id}")
def update_user(
    user_id: int,
    data: UpdateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    logger.info("Entering update_user()")
    logger.info(f"Admin {current_user.email} requested update for user ID: {user_id}")
    try:
        logger.info(f"Querying user ID {user_id} from database")
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            logger.warning(f"Admin update failed: User with ID {user_id} not found.")
            logger.info("Exiting update_user()")
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        logger.info(f"Updating fields for user ID {user_id}")
        if data.full_name is not None:
            user.full_name = data.full_name

        if data.email is not None:
            user.email = data.email

        if data.mobile is not None:
            user.mobile = data.mobile

        logger.info(f"Committing updates for user ID {user_id} to database")
        db.commit()
        logger.info(f"Refreshing user ID {user_id}")
        db.refresh(user)
        logger.info(f"User with ID {user_id} successfully updated by Admin {current_user.email}")

        res = {
            "success": True,
            "message": "User updated successfully",
            "data": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "mobile": user.mobile,
            }
        }
        logger.info("Exiting update_user()")
        return res
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Exception in update_user()")
        logger.info("Rolling back database changes in update_user()")
        db.rollback()
        raise e
    
#deactive user
@app.patch("/admin/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    logger.info("Entering deactivate_user()")
    logger.info(f"Admin {current_user.email} requested deactivation for user ID: {user_id}")
    try:
        logger.info(f"Querying user ID {user_id} from database")
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"Admin deactivation failed: User with ID {user_id} not found.")
            logger.info("Exiting deactivate_user()")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Setting status of user ID {user_id} to deactive")
        user.status = "deactive"
        user.is_active = False

        logger.info(f"Committing deactivation of user ID {user_id}")
        db.commit()
        logger.info(f"Refreshing user ID {user_id}")
        db.refresh(user)
        logger.info(f"User with ID {user_id} successfully deactivated by Admin {current_user.email}")

        res = {
            "success": True,
            "message": "User deactivated successfully",
            "status": user.status
        }
        logger.info("Exiting deactivate_user()")
        return res
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Exception in deactivate_user()")
        logger.info("Rolling back database changes in deactivate_user()")
        db.rollback()
        raise e

#activate users
@app.patch("/admin/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    logger.info("Entering activate_user()")
    logger.info(f"Admin {current_user.email} requested activation for user ID: {user_id}")
    try:
        logger.info(f"Querying user ID {user_id} from database")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Admin activation failed: User with ID {user_id} not found.")
            logger.info("Exiting activate_user()")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Setting status of user ID {user_id} to active")
        user.status = "active"
        user.is_active = True

        logger.info(f"Committing activation of user ID {user_id}")
        db.commit()
        logger.info(f"Refreshing user ID {user_id}")
        db.refresh(user)
        logger.info(f"User with ID {user_id} successfully activated by Admin {current_user.email}")

        res = {
            "success": True,
            "message": "User Activated Successfully",
            "status": user.status
        }
        logger.info("Exiting activate_user()")
        return res
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Exception in activate_user()")
        logger.info("Rolling back database changes in activate_user()")
        db.rollback()
        raise e

#  REGISTER 
@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    logger.info("Entering register()")
    logger.info(f"Registration attempt started for email: {user.email}")
    try:
        logger.info("Querying for existing email in database")
        existing_user = db.query(User).filter(User.email == user.email).first()

        if existing_user:
            logger.warning(f"Registration failed: Email already exists: {user.email}")
            logger.info("Exiting register()")
            return {"success": False, "message": "Email already exists"}

        logger.info("Formatting user full name")
        full_name = (
            f"{user.first_name} "
            f"{user.middle_name + ' ' if user.middle_name else ''}"
            f"{user.last_name}"
        ).strip()

        logger.info("Generating verification token")
        verification_token = generate_token()

        logger.info("Hashing password for registration")
        pw_hash = hash_password(user.password)

        new_user = User(
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            full_name=full_name,
            email=user.email,
            mobile=user.mobile,
            password_hash=pw_hash,
            role="user",
            is_verified=False,
            is_active=False,
            verification_token=verification_token
        )

        logger.info("Adding new user to session")
        db.add(new_user)
        logger.info("Committing user registration to database")
        db.commit()
        logger.info("Refreshing registered user details")
        db.refresh(new_user)
        logger.info(f"User registered successfully in database: {user.email}")

        logger.info("Triggering verification email send")
        send_verification_email(new_user.email, verification_token)
        logger.info(f"Verification email request triggered for: {user.email}")

        res = {
            "success": True,
            "message": "Registration successful. Please verify your email."
        }
        logger.info("Exiting register()")
        return res

    except Exception as e:
        logger.exception("Exception in register()")
        logger.info("Rolling back database changes in register()")
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
    logger.info("Entering verify_email()")
    logger.info("Email verification request received.")
    try:
        logger.info("Querying user by verification token")
        user = (
            db.query(User)
            .filter(User.verification_token == token)
            .first()
        )

        if not user:
            logger.warning("Email verification failed: Invalid or expired token.")
            logger.info("Exiting verify_email()")
            return {
                "success": False,
                "message": "Invalid or expired token"
            }

        logger.info(f"Verifying and activating user email: {user.email}")
        user.is_verified = True
        user.is_active = True
        user.verification_token = None

        logger.info("Committing email verification state to database")
        db.commit()
        logger.info(f"Email verified successfully for user ID: {user.id}, email: {user.email}")

        res = {
            "success": True,
            "message": "Email verified successfully"
        }
        logger.info("Exiting verify_email()")
        return res
    except Exception as e:
        logger.exception("Exception in verify_email()")
        logger.info("Rolling back database changes in verify_email()")
        db.rollback()
        raise e


#  LOGIN 

@app.post("/login")
def login(
    user: LoginUser,
    db: Session = Depends(get_db)
):
    logger.info("Entering login()")
    logger.info(f"Login attempt initiated for email: {user.email}")
    try:
        logger.info("Querying user email from database")
        db_user = (
            db.query(User)
            .filter(User.email == user.email)
            .first()
        )

        if not db_user:
            logger.warning(f"Login failed: User not found for email: {user.email}")
            logger.info("Exiting login()")
            return {
                "success": False,
                "message": "User not found"
            }

        logger.info("Checking user email verification status")
        if not db_user.is_verified:
            logger.warning(f"Login failed: Email not verified for user: {user.email}")
            logger.info("Exiting login()")
            return {
                "success": False,
                "message": "Please verify your email first"
            }

        logger.info("Checking user active status")
        if not db_user.is_active:
            logger.warning(f"Login failed: Account inactive for user: {user.email}")
            logger.info("Exiting login()")
            return {
                "success": False,
                "message": "Account is inactive"
            }

        logger.info("Verifying input password hash")
        pw_ok = verify_password(user.password, db_user.password_hash)
        if not pw_ok:
            logger.warning(f"Login failed: Wrong password for user: {user.email}")
            logger.info("Exiting login()")
            return {
                "success": False,
                "message": "Wrong password"
            }

        logger.info("Updating user last login timestamp")
        db_user.last_login_at = datetime.now(timezone.utc)
        logger.info("Committing last login time change to database")
        db.commit()
        logger.info(f"Login successful for user: {db_user.email}")

        logger.info("Generating JWT access token")
        access_token = create_access_token(
            data={
                "email": db_user.email,
                "role": db_user.role
            }
        )

        res = {
            "success": True,
            "token": access_token,
            "user": {
                "id": db_user.id,
                "name": db_user.full_name,
                "email": db_user.email,
                "role": db_user.role
            }
        }
        logger.info("Exiting login()")
        return res
    except Exception as e:
        logger.exception("Exception in login()")
        logger.info("Rolling back database changes in login()")
        db.rollback()
        raise e


#  FORGOT PASSWORD 

@app.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    logger.info("Entering forgot_password()")
    logger.info(f"Password reset requested for email: {request.email}")
    try:
        logger.info("Querying user by email for password reset")
        user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if not user:
            logger.warning(f"Password reset request failed: Email not found: {request.email}")
            logger.info("Exiting forgot_password()")
            return {
                "success": False,
                "message": "Email not found"
            }

        logger.info("Generating reset token")
        reset_token = generate_token()

        logger.info("Saving reset token to database user record")
        user.reset_token = reset_token
        logger.info("Committing reset token update to database")
        db.commit()
        logger.info(f"Password reset token saved for user: {request.email}")

        logger.info("Triggering send of password reset email")
        send_reset_email(
            request.email,
            reset_token
        )
        logger.info(f"Password reset link email triggered for: {request.email}")

        res = {
            "success": True,
            "message": "Reset link sent successfully"
        }
        logger.info("Exiting forgot_password()")
        return res
    except Exception as e:
        logger.exception("Exception in forgot_password()")
        logger.info("Rolling back database changes in forgot_password()")
        db.rollback()
        raise e


#  RESET PASSWORD 

@app.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    logger.info("Entering reset_password()")
    logger.info("Password reset submission received.")
    try:
        logger.info("Querying user by reset token")
        user = (
            db.query(User)
            .filter(User.reset_token == request.token)
            .first()
        )

        if not user:
            logger.warning("Password reset failed: Invalid or expired token.")
            logger.info("Exiting reset_password()")
            return {
                "success": False,
                "message": "Invalid or expired token"
            }

        logger.info("Hashing new password for update")
        pw_hash = hash_password(request.new_password)
        user.password_hash = pw_hash

        logger.info("Clearing reset token from database")
        user.reset_token = None

        logger.info("Committing password reset to database")
        db.commit()
        logger.info(f"Password reset successful for user: {user.email}")

        res = {
            "success": True,
            "message": "Password reset successful"
        }
        logger.info("Exiting reset_password()")
        return res
    except Exception as e:
        logger.exception("Exception in reset_password()")
        logger.info("Rolling back database changes in reset_password()")
        db.rollback()
        raise e

