"""
predict_note.py — ML inference for note recognition.
Loaded once at startup; called on every audio submission.
"""
import io
import json
import os
import pickle
import logging

import numpy as np

logger = logging.getLogger(__name__)

# ── Lazy-loaded singletons ───────────────────────────────────
_model   = None
_encoder = None
_config  = None


def _load():
    global _model, _encoder, _config
    # Already loaded (or already attempted)
    if _config is not None:
        return

    from django.conf import settings

    model_path   = settings.NOTE_CLASSIFIER_PATH
    encoder_path = settings.LABEL_ENCODER_PATH
    config_path  = settings.FEATURE_CONFIG_PATH

    # ── Load feature_config.json if it exists ────────────────
    if os.path.exists(config_path):
        with open(config_path) as f:
            _config = json.load(f)
    else:
        # No config file yet — build a minimal default so demo mode works
        _config = {
            'labels': [
                f"{n}{o}"
                for o in range(4, 7)
                for n in ['DO','DO#','RE','RE#','MI','FA','FA#','SOL','SOL#','LA','LA#','SI']
            ][:25],  # DO4 → DO6
            'sr': 22050, 'duration': 1.8,
            'n_mfcc': 40, 'hop_length': 512,
            'n_fft': 2048, 'n_frames': 72,
        }

    # ── Check if model files exist ────────────────────────────
    if not os.path.exists(model_path):
        logger.warning(
            "[NoteClassifier] Model not found — running in DEMO mode."
        )
        _model   = None
        _encoder = None
        return

    # ── Load real model ───────────────────────────────────────
    try:
        import tensorflow as tf
        logger.info("[NoteClassifier] Loading model...")
        _model = tf.keras.models.load_model(str(model_path))

        with open(encoder_path, 'rb') as f:
            _encoder = pickle.load(f)

        logger.info("[NoteClassifier] Model loaded ✓")
    except Exception as exc:
        logger.error(f"[NoteClassifier] Failed to load model: {exc}")
        _model   = None
        _encoder = None


def _extract_features(signal, sr):
    """Extract MFCC + delta + chroma + spectral contrast."""
    import librosa

    cfg = _config
    target_len = int(sr * cfg['duration'])

    if len(signal) > target_len:
        signal = signal[:target_len]
    else:
        signal = np.pad(signal, (0, max(0, target_len - len(signal))))

    hop  = cfg['hop_length']
    nfft = cfg['n_fft']
    nmfcc= cfg['n_mfcc']

    mfcc    = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=nmfcc,
                                    n_fft=nfft, hop_length=hop)
    mfcc_d  = librosa.feature.delta(mfcc)
    mfcc_d2 = librosa.feature.delta(mfcc, order=2)
    chroma  = librosa.feature.chroma_stft(y=signal, sr=sr,
                                           n_fft=nfft, hop_length=hop)
    contrast= librosa.feature.spectral_contrast(y=signal, sr=sr,
                                                  n_fft=nfft, hop_length=hop)

    combined = np.vstack([mfcc, mfcc_d, mfcc_d2, chroma, contrast])
    combined = ((combined - combined.mean(axis=1, keepdims=True)) /
                (combined.std(axis=1, keepdims=True) + 1e-8))

    # Pad / crop frames to match training shape
    target_frames = cfg['n_frames']
    if combined.shape[1] > target_frames:
        combined = combined[:, :target_frames]
    elif combined.shape[1] < target_frames:
        combined = np.pad(combined,
                          ((0, 0), (0, target_frames - combined.shape[1])))

    return combined


def predict_from_bytes(audio_bytes, top_k=3):
    _load()

    # ── Demo / fallback mode ─────────────────────────────────
    if _model is None:
        import random
        labels = _config.get('labels', [
            f"{n}{o}" for o in range(4, 7)
            for n in ['DO','DO#','RE','RE#','MI','FA','FA#','SOL','SOL#','LA','LA#','SI']
        ])
        note = random.choice(labels)
        return {
            'note': note,
            'confidence': round(random.uniform(0.5, 0.99), 3),
            'top_k': [{'note': note, 'confidence': 1.0}],
            'demo_mode': True,
        }

    # ── Real inference ───────────────────────────────────────
    import librosa
    import soundfile as sf

    # Decode audio
    signal, file_sr = sf.read(io.BytesIO(audio_bytes))
    logger.info(f"[predict] Audio decoded: shape={signal.shape}, sr={file_sr}")

    if signal.ndim > 1:
        signal = signal.mean(axis=1)

    target_sr = _config['sr']
    if file_sr != target_sr:
        logger.info(f"[predict] Resampling {file_sr} -> {target_sr}")
        signal = librosa.resample(signal.astype(np.float32),
                                  orig_sr=file_sr, target_sr=target_sr)

    signal = signal.astype(np.float32)
    logger.info(f"[predict] Signal length: {len(signal)} samples, max_amp={signal.max():.3f}")

    feat = _extract_features(signal, target_sr)
    logger.info(f"[predict] Features shape: {feat.shape}")
    feat_input = feat[np.newaxis, ..., np.newaxis]

    proba = _model.predict(feat_input, verbose=0)[0]
    top_k_idx = np.argsort(proba)[::-1][:top_k]

    top_k_preds = [
        {
            'note':       str(_encoder.inverse_transform([i])[0]),
            'confidence': float(proba[i]),
        }
        for i in top_k_idx
    ]

    logger.info(f"[predict] Top-3: {top_k_preds}")

    return {
        'note':       top_k_preds[0]['note'],
        'confidence': top_k_preds[0]['confidence'],
        'top_k':      top_k_preds,
        'demo_mode':  False,
    }
