"""데이터 처리 모듈"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class DataProcessor:
    """데이터 전처리를 위한 클래스"""
    
    def __init__(self):
        self.scaler = None
    
    def load_data(self, filepath):
        """데이터 파일 로드
        
        Args:
            filepath: 데이터 파일 경로
            
        Returns:
            pd.DataFrame: 로드된 데이터
        """
        return pd.read_csv(filepath)
    
    def clean_data(self, df):
        """데이터 정제
        
        Args:
            df: 원본 데이터프레임
            
        Returns:
            pd.DataFrame: 정제된 데이터프레임
        """
        # 결측치 처리
        df = df.dropna()
        
        # 중복 제거
        df = df.drop_duplicates()
        
        return df
    
    def normalize_features(self, X, method='standard'):
        """특징 정규화
        
        Args:
            X: 특징 데이터
            method: 정규화 방법 ('standard' 또는 'minmax')
            
        Returns:
            np.ndarray: 정규화된 데이터
        """
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return self.scaler.fit_transform(X)
