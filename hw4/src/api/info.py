from fastapi import APIRouter

router = APIRouter(tags=["Info"])

@router.get('/info')
def text():
    return {
        "message": "Привіт. Це додаток, який отримує дані з NIST про CVE та виводить їх користувачеві.",
        "author": "Єлизавета Черемних"
    }