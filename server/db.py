import json
import os

import firebase_admin
from firebase_admin import credentials, firestore


_credentials_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
if _credentials_json:
    try:
        _credentials_data = json.loads(_credentials_json)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(_credentials_data))
        db = firestore.client()
    except Exception as exc:
        print(f"Warning: Firebase initialization failed: {exc}")
        db = None
else:
    print("Warning: FIREBASE_CREDENTIALS_JSON is not set; Firestore is disabled.")
    db = None


def record_match_result(players: list[str], winner_id: str) -> None:
    """Record a match and update statistics for its players."""
    if db is None:
        print(f"Match result: players={players}, winner={winner_id}")
        return

    batch = db.batch()
    match_ref = db.collection("matches").document()
    batch.set(
        match_ref,
        {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "players": players,
            "winner": winner_id,
        },
    )

    for uid in players:
        data = {"games_played": firestore.Increment(1)}
        if uid == winner_id:
            data["total_wins"] = firestore.Increment(1)
        user_ref = db.collection("users").document(uid)
        batch.set(user_ref, data, merge=True)

    batch.commit()