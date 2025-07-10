import pandas as pd
import numpy as np
import logging
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# 机器学习库
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# 深度学习库
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Attention
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from config import Config
from models.database import PestDiseaseData, PredictionResult, init_database
from modules.data_preprocessing import DataPreprocessor

class PestDiseaseDataset(Dataset):
    """PyTorch数据集类"""
    
    def __init__(self, features, labels):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]

class LSTMModel(nn.Module):
    """LSTM模型用于时序预测"""
    
    def __init__(self, input_size, hidden_size, num_layers, num_classes, dropout_rate=0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           dropout=dropout_rate, batch_first=True)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out

class PestDiseasePredictor:
    """病虫害预测模型管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine, self.Session = init_database(config.DATABASE_URL)
        self.preprocessor = DataPreprocessor(config)
        self.models = {}
        self.label_encoders = {}
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
    def load_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """加载训练数据"""
        try:
            session = self.Session()
            
            # 加载病虫害数据
            pest_data = session.query(PestDiseaseData).all()
            
            # 转换为DataFrame
            df_pest = pd.DataFrame([{
                'timestamp': row.timestamp,
                'pest_type': row.pest_type,
                'disease_type': row.disease_type,
                'severity_level': row.severity_level,
                'location': row.location,
                'affected_area': row.affected_area
            } for row in pest_data])
            
            session.close()
            
            if df_pest.empty:
                logging.warning("No pest/disease data found")
                return pd.DataFrame(), pd.DataFrame()
            
            # 加载对应的环境数据
            env_data = self.preprocessor.load_data_from_db()
            
            if env_data.empty:
                logging.warning("No environment data found")
                return pd.DataFrame(), pd.DataFrame()
            
            # 合并数据
            df_pest['timestamp'] = pd.to_datetime(df_pest['timestamp'])
            env_data['timestamp'] = pd.to_datetime(env_data['timestamp'])
            
            # 按时间窗口合并（取最近的环境数据）
            merged_data = pd.merge_asof(
                df_pest.sort_values('timestamp'),
                env_data.sort_values('timestamp'),
                on='timestamp',
                direction='backward'
            )
            
            logging.info(f"Loaded {len(merged_data)} training samples")
            return merged_data, env_data
            
        except Exception as e:
            logging.error(f"Error loading training data: {e}")
            return pd.DataFrame(), pd.DataFrame()
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """准备特征和标签"""
        try:
            # 特征列
            feature_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity',
                             'wind_speed', 'rainfall', 'air_pressure']
            
            # 创建时间特征
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            feature_columns.extend(['hour', 'day_of_week', 'month'])
            
            # 选择特征
            X = df[feature_columns].fillna(0)
            
            # 创建标签（病虫害类型）
            df['pest_disease_label'] = df['pest_type'].fillna('none') + '_' + df['disease_type'].fillna('none')
            
            # 对标签进行编码
            if 'pest_disease' not in self.label_encoders:
                self.label_encoders['pest_disease'] = LabelEncoder()
            
            y = self.label_encoders['pest_disease'].fit_transform(df['pest_disease_label'])
            
            return X.values, y
            
        except Exception as e:
            logging.error(f"Error preparing features: {e}")
            return np.array([]), np.array([])
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
        """训练随机森林模型"""
        try:
            # 参数调优
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            rf = RandomForestClassifier(random_state=42)
            
            # 网格搜索
            grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1)
            grid_search.fit(X, y)
            
            best_model = grid_search.best_estimator_
            
            # 交叉验证
            cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='f1_weighted')
            
            logging.info(f"Random Forest CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
            logging.info(f"Best parameters: {grid_search.best_params_}")
            
            return best_model
            
        except Exception as e:
            logging.error(f"Error training Random Forest: {e}")
            return None
    
    def train_gradient_boosting(self, X: np.ndarray, y: np.ndarray) -> GradientBoostingClassifier:
        """训练梯度提升模型"""
        try:
            param_grid = {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 1.0]
            }
            
            gb = GradientBoostingClassifier(random_state=42)
            
            grid_search = GridSearchCV(gb, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1)
            grid_search.fit(X, y)
            
            best_model = grid_search.best_estimator_
            
            cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='f1_weighted')
            
            logging.info(f"Gradient Boosting CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
            logging.info(f"Best parameters: {grid_search.best_params_}")
            
            return best_model
            
        except Exception as e:
            logging.error(f"Error training Gradient Boosting: {e}")
            return None
    
    def create_lstm_model(self, input_shape: Tuple, num_classes: int) -> Model:
        """创建LSTM模型"""
        try:
            model = Sequential([
                LSTM(64, return_sequences=True, input_shape=input_shape),
                Dropout(0.2),
                LSTM(32, return_sequences=False),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dropout(0.2),
                Dense(num_classes, activation='softmax')
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            logging.error(f"Error creating LSTM model: {e}")
            return None
    
    def prepare_sequence_data(self, df: pd.DataFrame, sequence_length: int = 24) -> Tuple[np.ndarray, np.ndarray]:
        """准备序列数据用于LSTM训练"""
        try:
            # 按时间排序
            df = df.sort_values('timestamp')
            
            # 特征列
            feature_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity',
                             'wind_speed', 'rainfall', 'air_pressure']
            
            # 标准化特征
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(df[feature_columns].fillna(0))
            
            # 创建序列
            X, y = [], []
            for i in range(sequence_length, len(features_scaled)):
                X.append(features_scaled[i-sequence_length:i])
                # 简化标签：是否有病虫害
                has_pest = 1 if (pd.notna(df.iloc[i]['pest_type']) or pd.notna(df.iloc[i]['disease_type'])) else 0
                y.append(has_pest)
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            logging.error(f"Error preparing sequence data: {e}")
            return np.array([]), np.array([])
    
    def train_lstm_model(self, X: np.ndarray, y: np.ndarray) -> Model:
        """训练LSTM模型"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 创建模型
            model = self.create_lstm_model((X.shape[1], X.shape[2]), 2)
            
            # 训练配置
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ModelCheckpoint(
                    str(self.model_dir / 'lstm_model.h5'),
                    save_best_only=True,
                    monitor='val_accuracy'
                )
            ]
            
            # 训练模型
            history = model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_test, y_test),
                callbacks=callbacks,
                verbose=1
            )
            
            # 评估模型
            test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
            logging.info(f"LSTM Test Accuracy: {test_acc:.4f}")
            
            return model
            
        except Exception as e:
            logging.error(f"Error training LSTM model: {e}")
            return None
    
    def train_all_models(self):
        """训练所有模型"""
        try:
            # 加载数据
            pest_data, env_data = self.load_training_data()
            
            if pest_data.empty:
                logging.warning("No training data available")
                return
            
            # 准备传统机器学习特征
            X, y = self.prepare_features(pest_data)
            
            if len(X) == 0:
                logging.warning("No features prepared")
                return
            
            # 训练传统机器学习模型
            logging.info("Training Random Forest model...")
            rf_model = self.train_random_forest(X, y)
            if rf_model:
                self.models['random_forest'] = rf_model
                joblib.dump(rf_model, self.model_dir / 'random_forest_model.pkl')
            
            logging.info("Training Gradient Boosting model...")
            gb_model = self.train_gradient_boosting(X, y)
            if gb_model:
                self.models['gradient_boosting'] = gb_model
                joblib.dump(gb_model, self.model_dir / 'gradient_boosting_model.pkl')
            
            # 准备序列数据并训练LSTM
            if len(env_data) > 48:  # 确保有足够的数据创建序列
                logging.info("Preparing sequence data for LSTM...")
                X_seq, y_seq = self.prepare_sequence_data(env_data.merge(pest_data, on='timestamp', how='left'))
                
                if len(X_seq) > 0:
                    logging.info("Training LSTM model...")
                    lstm_model = self.train_lstm_model(X_seq, y_seq)
                    if lstm_model:
                        self.models['lstm'] = lstm_model
                        lstm_model.save(str(self.model_dir / 'lstm_model.h5'))
            
            # 保存标签编码器
            joblib.dump(self.label_encoders, self.model_dir / 'label_encoders.pkl')
            
            logging.info("All models trained successfully")
            
        except Exception as e:
            logging.error(f"Error training models: {e}")
    
    def load_models(self):
        """加载已训练的模型"""
        try:
            # 加载传统机器学习模型
            rf_path = self.model_dir / 'random_forest_model.pkl'
            if rf_path.exists():
                self.models['random_forest'] = joblib.load(rf_path)
                logging.info("Random Forest model loaded")
            
            gb_path = self.model_dir / 'gradient_boosting_model.pkl'
            if gb_path.exists():
                self.models['gradient_boosting'] = joblib.load(gb_path)
                logging.info("Gradient Boosting model loaded")
            
            # 加载LSTM模型
            lstm_path = self.model_dir / 'lstm_model.h5'
            if lstm_path.exists():
                self.models['lstm'] = tf.keras.models.load_model(str(lstm_path))
                logging.info("LSTM model loaded")
            
            # 加载标签编码器
            encoder_path = self.model_dir / 'label_encoders.pkl'
            if encoder_path.exists():
                self.label_encoders = joblib.load(encoder_path)
                logging.info("Label encoders loaded")
            
        except Exception as e:
            logging.error(f"Error loading models: {e}")
    
    def predict(self, features: np.ndarray, model_type: str = 'random_forest') -> Dict:
        """进行预测"""
        try:
            if model_type not in self.models:
                logging.error(f"Model {model_type} not found")
                return {}
            
            model = self.models[model_type]
            
            if model_type in ['random_forest', 'gradient_boosting']:
                # 传统机器学习模型预测
                pred_proba = model.predict_proba(features)
                pred_class = model.predict(features)
                
                # 获取类别名称
                class_names = self.label_encoders['pest_disease'].classes_
                
                results = []
                for i, (prob, cls) in enumerate(zip(pred_proba, pred_class)):
                    max_prob = np.max(prob)
                    predicted_class = class_names[cls]
                    
                    results.append({
                        'prediction': predicted_class,
                        'confidence': float(max_prob),
                        'risk_level': float(max_prob) if predicted_class != 'none_none' else 0.0
                    })
                
                return {'predictions': results}
            
            elif model_type == 'lstm':
                # LSTM模型预测
                pred_proba = model.predict(features)
                pred_class = np.argmax(pred_proba, axis=1)
                
                results = []
                for i, (prob, cls) in enumerate(zip(pred_proba, pred_class)):
                    max_prob = np.max(prob)
                    risk_level = float(max_prob) if cls == 1 else 0.0
                    
                    results.append({
                        'prediction': 'pest_risk' if cls == 1 else 'no_risk',
                        'confidence': float(max_prob),
                        'risk_level': risk_level
                    })
                
                return {'predictions': results}
            
        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return {}
    
    def predict_current_risk(self) -> Dict:
        """预测当前风险"""
        try:
            # 获取最新的环境数据
            latest_data = self.preprocessor.load_data_from_db(
                start_date=datetime.now() - timedelta(hours=24),
                end_date=datetime.now()
            )
            
            if latest_data.empty:
                logging.warning("No recent data available for prediction")
                return {}
            
            # 准备特征
            feature_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity',
                             'wind_speed', 'rainfall', 'air_pressure']
            
            latest_data['hour'] = latest_data['timestamp'].dt.hour
            latest_data['day_of_week'] = latest_data['timestamp'].dt.dayofweek
            latest_data['month'] = latest_data['timestamp'].dt.month
            
            feature_columns.extend(['hour', 'day_of_week', 'month'])
            
            # 取最新的一条记录
            latest_features = latest_data[feature_columns].iloc[-1:].fillna(0).values
            
            # 使用所有可用模型进行预测
            predictions = {}
            for model_type in self.models:
                if model_type != 'lstm':  # LSTM需要序列数据
                    pred_result = self.predict(latest_features, model_type)
                    if pred_result:
                        predictions[model_type] = pred_result['predictions'][0]
            
            # 集成预测结果
            if predictions:
                avg_risk = np.mean([pred['risk_level'] for pred in predictions.values()])
                avg_confidence = np.mean([pred['confidence'] for pred in predictions.values()])
                
                return {
                    'risk_level': float(avg_risk),
                    'confidence': float(avg_confidence),
                    'predictions': predictions,
                    'timestamp': datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            logging.error(f"Error predicting current risk: {e}")
            return {}
    
    def save_prediction_to_db(self, prediction: Dict):
        """保存预测结果到数据库"""
        try:
            session = self.Session()
            
            pred_result = PredictionResult(
                prediction_type='pest_disease',
                risk_level=prediction.get('risk_level', 0.0),
                confidence=prediction.get('confidence', 0.0),
                environmental_factors=prediction.get('predictions', {}),
                location='Default',
                model_version='1.0'
            )
            
            session.add(pred_result)
            session.commit()
            session.close()
            
            logging.info("Prediction saved to database")
            
        except Exception as e:
            logging.error(f"Error saving prediction to database: {e}")

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = Config()
    predictor = PestDiseasePredictor(config)
    
    # 训练模型
    predictor.train_all_models()
    
    # 加载模型
    predictor.load_models()
    
    # 进行预测
    current_risk = predictor.predict_current_risk()
    if current_risk:
        print(f"Current risk prediction: {current_risk}")
        predictor.save_prediction_to_db(current_risk) 