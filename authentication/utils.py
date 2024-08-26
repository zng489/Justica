def is_magistrado(decoded_token, profiles):
    if decoded_token is None:
        return False
    user_profiles = decoded_token.get("corporativo", []) or []
    for profile in user_profiles:
        profile_name = str(profile.get("dsc_perfil") or "").lower().strip()
        if profile_name in profiles:
            return True

    return False


def get_codigo_tribunal(decoded_token, silent=False):
    field_name = "seq_tribunal_pai"
    cod_tribunal = None
    if not decoded_token and not silent:
        raise ValueError("Empty user's decoded token")
    decoded_token = decoded_token or dict()
    user_profiles = decoded_token.get("corporativo", []) or []
    for profile in user_profiles:
        cod_tribunal = str(profile.get(field_name) or "").lower().strip()
        if cod_tribunal:
            return cod_tribunal

    if cod_tribunal is None and not silent:
        raise ValueError(f"'{field_name}' not found")

    return None
