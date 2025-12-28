import os
import pickle
import logging
import numpy as np
from typing import Optional
from datetime import datetime
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

logger = logging.getLogger(__name__)

# Model storage path
MODEL_DIR = "trained_models"
MODEL_PATH = os.path.join(MODEL_DIR, "naive_bayes_model.pkl")


class NaiveBayesService:
    """
    Service for Gaussian Naive Bayes classification.
    
    Handles model training, prediction, and persistence.
    """
    
    # Class labels
    CLASSES = ["ringan", "sedang", "berat"]
    
    # Feature names for reference
    FEATURE_NAMES = [
        "damage_area",
        "damage_depth", 
        "damage_point_count",
        "component_age",
        "usage_frequency",
        "corrosion_level",
        "deformation"
    ]
    
    def __init__(self):
        self.model: Optional[GaussianNB] = None
        self.is_trained: bool = False
        self.last_trained_at: Optional[datetime] = None
        self.training_samples: int = 0
        self._load_model()
    
    def _load_model(self) -> None:
        """Load model from disk if exists."""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.is_trained = True
                    self.last_trained_at = data.get("trained_at")
                    self.training_samples = data.get("training_samples", 0)
                logger.info(f"Model loaded from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None
                self.is_trained = False
    
    def _save_model(self) -> None:
        """Save model to disk."""
        os.makedirs(MODEL_DIR, exist_ok=True)
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump({
                    "model": self.model,
                    "trained_at": self.last_trained_at,
                    "training_samples": self.training_samples
                }, f)
            logger.info(f"Model saved to {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def train(
        self,
        features: list[list[float]],
        labels: list[str],
        test_size: float = 0.2
    ) -> dict:
        """
        Train the Naive Bayes model.
        
        Args:
            features: List of feature vectors (7 features each)
            labels: List of damage level labels (Ringan/Sedang/Berat)
            test_size: Proportion of data for testing (0-1)
        
        Returns:
            Dictionary containing training metrics
        """
        logger.info(f"Starting model training with {len(features)} samples")
        
        if len(features) < 10:
            raise ValueError("Minimum 10 samples required for training")
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Initialize and train model
        self.model = GaussianNB()
        self.model.fit(X_train, y_train)
        
        # Predict on test set
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        
        # Get detailed classification report
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        
        # Get confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=self.CLASSES)
        
        # Update state
        self.is_trained = True
        self.last_trained_at = datetime.utcnow()
        self.training_samples = len(X_train)
        
        # Save model
        self._save_model()
        
        logger.info(f"Model training completed. Accuracy: {accuracy:.4f}")
        
        return {
            "success": True,
            "message": "Model trained successfully",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "classification_report": self._clean_report(report),
            "confusion_matrix": cm.tolist()
        }
    
    def predict(self, features: list[float]) -> dict:
        """
        Predict damage level for given features.
        
        Args:
            features: List of 7 features
        
        Returns:
            Dictionary containing prediction and probabilities
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model is not trained yet")
        
        if len(features) != 7:
            raise ValueError(f"Expected 7 features, got {len(features)}")
        
        # Reshape for single prediction
        X = np.array(features).reshape(1, -1)
        
        # Get prediction and probabilities
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Map probabilities to class names
        prob_dict = {}
        for i, class_name in enumerate(self.model.classes_):
            prob_dict[class_name] = float(probabilities[i])
        
        # Get confidence (probability of predicted class)
        confidence = float(max(probabilities))
        
        logger.debug(f"Prediction: {prediction} (confidence: {confidence:.4f})")
        
        return {
            "predicted_level": prediction,
            "confidence": confidence,
            "probabilities": {
                "ringan": prob_dict.get("ringan", 0.0),
                "sedang": prob_dict.get("sedang", 0.0),
                "berat": prob_dict.get("berat", 0.0)
            }
        }
    
    def get_status(self) -> dict:
        """Get current model status."""
        return {
            "is_trained": self.is_trained,
            "training_samples": self.training_samples if self.is_trained else None,
            "last_trained_at": self.last_trained_at.isoformat() if self.last_trained_at else None,
            "accuracy": None  # Will be filled from database
        }
    
    def _clean_report(self, report: dict) -> dict:
        """Clean classification report for storage."""
        cleaned = {}
        for key in self.CLASSES:
            if key in report:
                cleaned[key] = {
                    "precision": float(report[key]["precision"]),
                    "recall": float(report[key]["recall"]),
                    "f1-score": float(report[key]["f1-score"]),
                    "support": int(report[key]["support"])
                }
        return cleaned
    
    def get_model_info(self) -> dict:
        """Get model parameters and info."""
        if not self.is_trained or self.model is None:
            return {"error": "Model not trained"}
        
        return {
            "class_count": len(self.model.classes_),
            "classes": self.model.classes_.tolist(),
            "feature_count": len(self.FEATURE_NAMES),
            "feature_names": self.FEATURE_NAMES,
            "class_prior": self.model.class_prior_.tolist(),
            "theta": self.model.theta_.tolist(),  # Mean of each feature per class
            "var": self.model.var_.tolist()  # Variance of each feature per class
        }


# Singleton instance
naive_bayes_service = NaiveBayesService()