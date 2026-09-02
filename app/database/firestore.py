"""
Firebase Admin SDK Initialization and Firestore Client Management.

Supports credentials via:
1. FIREBASE_SERVICE_ACCOUNT_JSON (Raw JSON string from environment variable)
2. FIREBASE_CREDENTIALS_PATH (Path to JSON service account key file)
3. Application Default Credentials (ADC) as fallback
4. Mock/Fallback mode for local testing without cloud credentials
"""

import os
import json
import logging
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger("app.database.firestore")

_firestore_client: Optional[Any] = None
_is_mock_mode: bool = False


def init_firestore():
    """Initializes Firebase Admin SDK and returns the Firestore client."""
    global _firestore_client, _is_mock_mode
    if _firestore_client is not None:
        return _firestore_client

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        logger.warning(
            "firebase-admin package is not installed. Operating in mock/fallback database mode."
        )
        _is_mock_mode = True
        return None

    cred_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    cred_file_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")

    cred = None
    if cred_json_str and cred_json_str.strip():
        try:
            cred_dict = json.loads(cred_json_str)
            cred = credentials.Certificate(cred_dict)
            logger.info("Firebase initialized using FIREBASE_SERVICE_ACCOUNT_JSON environment variable.")
        except Exception as e:
            logger.warning(f"Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")

    if cred is None and cred_file_path and Path(cred_file_path).exists():
        try:
            cred = credentials.Certificate(cred_file_path)
            logger.info(f"Firebase initialized using service account file at '{cred_file_path}'.")
        except Exception as e:
            logger.warning(f"Failed to load credentials from '{cred_file_path}': {e}")

    if cred is None:
        # Check if running in mock/offline mode or Application Default Credentials
        try:
            firebase_admin.initialize_app()
            _firestore_client = firestore.client()
            logger.info("Firebase initialized using Application Default Credentials (ADC).")
            return _firestore_client
        except Exception as e:
            logger.warning(
                f"Firebase credentials not found or initialization failed ({e}). "
                "Operating in mock/in-memory fallback database mode for testing."
            )
            _is_mock_mode = True
            return None

    try:
        firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
        return _firestore_client
    except Exception as e:
        logger.error(f"Error initializing Firebase app: {e}")
        _is_mock_mode = True
        return None


def get_firestore_db():
    """Returns initialized Firestore client or None if mock mode."""
    global _firestore_client
    if _firestore_client is None and not _is_mock_mode:
        init_firestore()
    return _firestore_client


def is_firestore_mock() -> bool:
    """Returns whether database is running in mock/offline mode."""
    global _is_mock_mode
    return _is_mock_mode
