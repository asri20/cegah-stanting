import os
import boto3
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Konfigurasi Database RDS [cite: 31]
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model Database (Fitur 1: Simpan Data Anak)
class Anak(Base):
    __tablename__ = "data_anak"
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String)
    berat = Column(String)

Base.metadata.create_all(bind=engine)

# Konfigurasi S3 [cite: 32]
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='ap-southeast-1'
)

@app.get("/", response_class=HTMLResponse)
async def home():
    # Fitur 2: Menampilkan Halaman Utama
    return "<h1>Tumbuh Cerah: Sistem Pemantauan Kesehatan</h1><p>Gunakan form untuk upload data.</p>"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Fitur 3: Upload ke S3 [cite: 38]
    bucket_name = os.getenv('S3_BUCKET')
    s3_client.upload_fileobj(file.file, bucket_name, file.filename)
    return {"message": f"File {file.filename} berhasil diupload ke S3!"}

@app.post("/submit")
async def handle_submit(
    nama: str = Form(...), 
    berat: str = Form(...), 
    file: UploadFile = File(...)
):
    # 1. Simpan ke RDS (Database)
    db = SessionLocal()
    baru = Anak(nama=nama, berat=berat)
    db.add(baru)
    db.commit()
    db.close()

    # 2. Simpan ke S3 (Storage)
    bucket_name = os.getenv('S3_BUCKET')
    s3_client.upload_fileobj(file.file, bucket_name, file.filename)

    return {"status": "Sukses!", "nama": nama, "s3_file": file.filename}