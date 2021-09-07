from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            if not self.check_token(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")

            decoded_token = auth.verify_id_token(credentials.credentials)
            return decoded_token['uid']
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def check_token(self, token: str) -> bool:
        try:
            return auth.verify_id_token(token) is not None
        except:
            return False
