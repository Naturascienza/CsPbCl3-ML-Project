"""모델 학습 모듈"""
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib


class ModelTrainer:
    """머신러닝 모델 학습을 위한 클래스"""
    
    def __init__(self, model_type='random_forest'):
        """
        Args:
            model_type: 모델 유형 ('random_forest', 'gradient_boosting')
        """
        self.model_type = model_type
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """모델 초기화"""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X_train, y_train):
        """모델 학습
        
        Args:
            X_train: 학습 데이터 특징
            y_train: 학습 데이터 레이블
        """
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        """예측 수행
        
        Args:
            X: 예측할 데이터
            
        Returns:
            np.ndarray: 예측 결과
        """
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        """모델 평가
        
        Args:
            X_test: 테스트 데이터 특징
            y_test: 테스트 데이터 레이블
            
        Returns:
            dict: 평가 지표
        """
        y_pred = self.predict(X_test)
        
        return {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
    
    def cross_validate(self, X, y, cv=5):
        """교차 검증
        
        Args:
            X: 전체 데이터 특징
            y: 전체 데이터 레이블
            cv: 폴드 수
            
        Returns:
            dict: 교차 검증 결과
        """
        scores = cross_val_score(
            self.model, X, y,
            cv=cv,
            scoring='r2',
            n_jobs=-1
        )
        
        return {
            'scores': scores,
            'mean': scores.mean(),
            'std': scores.std()
        }
    
    def save_model(self, filepath):
        """모델 저장
        
        Args:
            filepath: 저장할 파일 경로
        """
        joblib.dump(self.model, filepath)
    
    def load_model(self, filepath):
        """모델 로드
        
        Args:
            filepath: 로드할 파일 경로
        """
        self.model = joblib.load(filepath)
