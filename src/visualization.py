"""시각화 모듈"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


class Visualizer:
    """데이터 및 결과 시각화를 위한 클래스"""
    
    def __init__(self, style='seaborn-v0_8'):
        """
        Args:
            style: matplotlib 스타일
        """
        plt.style.use('default')
        sns.set_theme()
        self.fig_size = (10, 6)
    
    def plot_correlation_matrix(self, df, save_path=None):
        """상관관계 매트릭스 플롯
        
        Args:
            df: 데이터프레임
            save_path: 저장 경로 (선택사항)
        """
        plt.figure(figsize=self.fig_size)
        correlation = df.corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        plt.show()
    
    def plot_feature_importance(self, model, feature_names, save_path=None):
        """특징 중요도 플롯
        
        Args:
            model: 학습된 모델
            feature_names: 특징 이름 리스트
            save_path: 저장 경로 (선택사항)
        """
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=self.fig_size)
        plt.title('Feature Importances')
        plt.bar(range(len(importances)), importances[indices])
        plt.xticks(range(len(importances)), 
                   [feature_names[i] for i in indices], 
                   rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        plt.show()
    
    def plot_predictions(self, y_true, y_pred, save_path=None):
        """예측 결과 산점도
        
        Args:
            y_true: 실제 값
            y_pred: 예측 값
            save_path: 저장 경로 (선택사항)
        """
        plt.figure(figsize=self.fig_size)
        plt.scatter(y_true, y_pred, alpha=0.5)
        
        # 완벽한 예측 라인
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Prediction vs Actual')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        plt.show()
    
    def plot_residuals(self, y_true, y_pred, save_path=None):
        """잔차 플롯
        
        Args:
            y_true: 실제 값
            y_pred: 예측 값
            save_path: 저장 경로 (선택사항)
        """
        residuals = y_true - y_pred
        
        plt.figure(figsize=self.fig_size)
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.axhline(y=0, color='r', linestyle='--', lw=2)
        plt.xlabel('Predicted Values')
        plt.ylabel('Residuals')
        plt.title('Residual Plot')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        plt.show()
