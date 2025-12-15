from fastapi import Header, HTTPException, Depends

def allow_guest_or_user(
    x_guest: str | None = Header(default=None),
):
    """
    Allows requests if:
    - x-guest: true is present
    - OR later: valid authenticated user
    """
    if x_guest == "true":
        return "guest"

    # later we can plug Supabase auth here
    raise HTTPException(
        status_code=401,
        detail="Authentication required"
    )
