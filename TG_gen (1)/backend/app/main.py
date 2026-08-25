import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import engine, Base
from app.db.seed import seed_database
from app.api.v1.endpoints import (
    auth, users, projects, analysis, recommendations,
    dyeing, impact, chat, concepts, generated_images, reports, admin, fabric_detection,
    visual_search, outfit, outfit_studio_products
)

Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Full-stack AI Sustainable Fabric Analyzer and Fashion Design Assistant API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(fabric_detection.router, prefix="/api/fabric", tags=["Fabric AI Detection"])
app.include_router(fabric_detection.router, prefix="/api/fabric-detection", tags=["Fabric Detection"])
app.include_router(fabric_detection.router, prefix=f"{settings.API_V1_STR}/fabric-detection", tags=["Fabric Detection"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["Projects"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Fabric Analysis"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Fabric Recommendations"])
app.include_router(dyeing.router, prefix=f"{settings.API_V1_STR}/dyeing", tags=["Dyeing Recommendations"])
app.include_router(impact.router, prefix=f"{settings.API_V1_STR}/impact", tags=["Environmental Impact"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["AI Design Assistant Chat"])
app.include_router(concepts.router, prefix=f"{settings.API_V1_STR}/concepts", tags=["Design Concepts"])
app.include_router(generated_images.router, prefix=f"{settings.API_V1_STR}/generated-images", tags=["Generated Concept Images"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Sustainability Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Model & Catalog Management"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Catalog Management"])
app.include_router(visual_search.router, prefix="/api/visual-search", tags=["Visual Search"])
app.include_router(outfit.router, prefix="/api/outfit", tags=["AI Outfit Studio"])
app.include_router(outfit_studio_products.router, prefix="/api/outfit-studio", tags=["AI Outfit Studio - Compare & Buy"])
app.include_router(outfit_studio_products.router, prefix=f"{settings.API_V1_STR}/outfit-studio", tags=["AI Outfit Studio - Compare & Buy"])


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "version": "1.0.0"
    }
