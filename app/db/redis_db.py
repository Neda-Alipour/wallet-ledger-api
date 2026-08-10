from redis import Redis


from app.core.config import db_settings

_token_blacllist = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0,
)


def add_jti_to_blacklist(jti: str):
    _token_blacllist.set(jti, "blacklisted")


def is_jti_blacklisted(jti: str) -> bool:
    return _token_blacllist.exists(jti)