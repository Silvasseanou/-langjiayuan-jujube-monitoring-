import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer, KNNImputer

from config import Config
from models.database import EnvironmentData, init_database

class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine, self.Session = init_database(config.DATABASE_URL)
        
    def load_data_from_db(self, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """从数据库加载数据"""
        try:
            session = self.Session()
            
            query = session.query(EnvironmentData)
            
            if start_date:
                query = query.filter(EnvironmentData.timestamp >= start_date)
            if end_date:
                query = query.filter(EnvironmentData.timestamp <= end_date)
                
            data = query.all()
            session.close()
            
            # 转换为DataFrame
            df = pd.DataFrame([{
                'timestamp': row.timestamp,
                'temperature': row.temperature,
                'humidity': row.humidity,
                'soil_moisture': row.soil_moisture,
                'light_intensity': row.light_intensity,
                'wind_speed': row.wind_speed,
                'rainfall': row.rainfall,
                'air_pressure': row.air_pressure,
                'location': row.location,
                'sensor_id': row.sensor_id
            } for row in data])
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
            logging.info(f"Loaded {len(df)} records from database")
            return df
            
        except Exception as e:
            logging.error(f"Error loading data from database: {e}")
            return pd.DataFrame()
    
    def detect_outliers(self, df: pd.DataFrame, column: str, method: str = 'zscore', 
                       threshold: float = 3.0) -> pd.Series:
        """检测异常值"""
        try:
            if method == 'zscore':
                z_scores = np.abs(stats.zscore(df[column].dropna()))
                outliers = z_scores > threshold
                
            elif method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
                
            elif method == 'isolation_forest':
                from sklearn.ensemble import IsolationForest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(df[[column]].fillna(df[column].mean())) == -1
                
            else:
                raise ValueError(f"Unknown outlier detection method: {method}")
                
            return pd.Series(outliers, index=df.index)
            
        except Exception as e:
            logging.error(f"Error detecting outliers in {column}: {e}")
            return pd.Series(False, index=df.index)
    
    def remove_outliers(self, df: pd.DataFrame, columns: List[str] = None, 
                       method: str = 'zscore') -> pd.DataFrame:
        """移除异常值"""
        try:
            if columns is None:
                columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity', 
                          'wind_speed', 'rainfall', 'air_pressure']
            
            df_cleaned = df.copy()
            total_outliers = 0
            
            for column in columns:
                if column in df_cleaned.columns:
                    outliers = self.detect_outliers(df_cleaned, column, method)
                    outlier_count = outliers.sum()
                    total_outliers += outlier_count
                    
                    if outlier_count > 0:
                        logging.info(f"Detected {outlier_count} outliers in {column}")
                        # 将异常值设为NaN，后续进行插值
                        df_cleaned.loc[outliers, column] = np.nan
            
            logging.info(f"Total outliers detected and removed: {total_outliers}")
            return df_cleaned
            
        except Exception as e:
            logging.error(f"Error removing outliers: {e}")
            return df
    
    def interpolate_missing_values(self, df: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
        """插值填补缺失值"""
        try:
            df_filled = df.copy()
            numeric_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity', 
                             'wind_speed', 'rainfall', 'air_pressure']
            
            for column in numeric_columns:
                if column in df_filled.columns:
                    missing_count = df_filled[column].isnull().sum()
                    
                    if missing_count > 0:
                        logging.info(f"Interpolating {missing_count} missing values in {column}")
                        
                        if method == 'linear':
                            df_filled[column] = df_filled[column].interpolate(method='linear')
                        elif method == 'polynomial':
                            df_filled[column] = df_filled[column].interpolate(method='polynomial', order=2)
                        elif method == 'spline':
                            df_filled[column] = df_filled[column].interpolate(method='spline', order=3)
                        elif method == 'knn':
                            # 使用KNN进行插值
                            imputer = KNNImputer(n_neighbors=5)
                            df_filled[column] = imputer.fit_transform(df_filled[[column]]).flatten()
                        elif method == 'forward_fill':
                            df_filled[column] = df_filled[column].fillna(method='ffill')
                        elif method == 'backward_fill':
                            df_filled[column] = df_filled[column].fillna(method='bfill')
                        
                        # 如果仍有缺失值，使用均值填充
                        if df_filled[column].isnull().any():
                            df_filled[column] = df_filled[column].fillna(df_filled[column].mean())
            
            return df_filled
            
        except Exception as e:
            logging.error(f"Error interpolating missing values: {e}")
            return df
    
    def smooth_data(self, df: pd.DataFrame, window: int = 5, method: str = 'rolling_mean') -> pd.DataFrame:
        """数据平滑"""
        try:
            df_smoothed = df.copy()
            numeric_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity', 
                             'wind_speed', 'rainfall', 'air_pressure']
            
            for column in numeric_columns:
                if column in df_smoothed.columns:
                    if method == 'rolling_mean':
                        df_smoothed[f'{column}_smoothed'] = df_smoothed[column].rolling(window=window, center=True).mean()
                    elif method == 'rolling_median':
                        df_smoothed[f'{column}_smoothed'] = df_smoothed[column].rolling(window=window, center=True).median()
                    elif method == 'exponential':
                        df_smoothed[f'{column}_smoothed'] = df_smoothed[column].ewm(span=window).mean()
                    elif method == 'savgol':
                        from scipy.signal import savgol_filter
                        df_smoothed[f'{column}_smoothed'] = savgol_filter(
                            df_smoothed[column].fillna(method='ffill'), 
                            window_length=window, 
                            polyorder=2
                        )
            
            return df_smoothed
            
        except Exception as e:
            logging.error(f"Error smoothing data: {e}")
            return df
    
    def normalize_data(self, df: pd.DataFrame, method: str = 'minmax') -> Tuple[pd.DataFrame, object]:
        """数据标准化/归一化"""
        try:
            df_normalized = df.copy()
            numeric_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity', 
                             'wind_speed', 'rainfall', 'air_pressure']
            
            columns_to_normalize = [col for col in numeric_columns if col in df_normalized.columns]
            
            if method == 'minmax':
                scaler = MinMaxScaler()
            elif method == 'standard':
                scaler = StandardScaler()
            else:
                raise ValueError(f"Unknown normalization method: {method}")
            
            df_normalized[columns_to_normalize] = scaler.fit_transform(df_normalized[columns_to_normalize])
            
            logging.info(f"Normalized data using {method} method")
            return df_normalized, scaler
            
        except Exception as e:
            logging.error(f"Error normalizing data: {e}")
            return df, None
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建特征工程"""
        try:
            df_features = df.copy()
            
            # 时间特征
            df_features['hour'] = df_features['timestamp'].dt.hour
            df_features['day_of_week'] = df_features['timestamp'].dt.dayofweek
            df_features['month'] = df_features['timestamp'].dt.month
            df_features['season'] = df_features['month'].apply(self._get_season)
            
            # 移动平均特征
            for column in ['temperature', 'humidity', 'soil_moisture']:
                if column in df_features.columns:
                    df_features[f'{column}_ma_24h'] = df_features[column].rolling(window=24).mean()
                    df_features[f'{column}_ma_7d'] = df_features[column].rolling(window=168).mean()
            
            # 差分特征
            for column in ['temperature', 'humidity', 'soil_moisture']:
                if column in df_features.columns:
                    df_features[f'{column}_diff'] = df_features[column].diff()
                    df_features[f'{column}_diff_24h'] = df_features[column].diff(periods=24)
            
            # 组合特征
            if 'temperature' in df_features.columns and 'humidity' in df_features.columns:
                df_features['heat_index'] = self._calculate_heat_index(
                    df_features['temperature'], df_features['humidity']
                )
            
            # 统计特征
            for column in ['temperature', 'humidity', 'soil_moisture']:
                if column in df_features.columns:
                    df_features[f'{column}_std_24h'] = df_features[column].rolling(window=24).std()
                    df_features[f'{column}_min_24h'] = df_features[column].rolling(window=24).min()
                    df_features[f'{column}_max_24h'] = df_features[column].rolling(window=24).max()
            
            logging.info("Created engineered features")
            return df_features
            
        except Exception as e:
            logging.error(f"Error creating features: {e}")
            return df
    
    def _get_season(self, month: int) -> str:
        """获取季节"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _calculate_heat_index(self, temperature: pd.Series, humidity: pd.Series) -> pd.Series:
        """计算热指数"""
        try:
            # 简化的热指数计算
            hi = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + (humidity * 0.094))
            return hi
        except Exception as e:
            logging.error(f"Error calculating heat index: {e}")
            return pd.Series(0, index=temperature.index)
    
    def process_data(self, start_date: datetime = None, end_date: datetime = None,
                    remove_outliers: bool = True, interpolate: bool = True,
                    smooth: bool = False, normalize: bool = False,
                    create_features: bool = True) -> pd.DataFrame:
        """完整的数据预处理流程"""
        try:
            # 加载数据
            df = self.load_data_from_db(start_date, end_date)
            
            if df.empty:
                logging.warning("No data to process")
                return df
            
            logging.info(f"Starting data preprocessing with {len(df)} records")
            
            # 移除异常值
            if remove_outliers:
                df = self.remove_outliers(df)
            
            # 插值填补缺失值
            if interpolate:
                df = self.interpolate_missing_values(df)
            
            # 数据平滑
            if smooth:
                df = self.smooth_data(df)
            
            # 数据标准化
            if normalize:
                df, scaler = self.normalize_data(df)
            
            # 特征工程
            if create_features:
                df = self.create_features(df)
            
            # 去除包含NaN的行
            df = df.dropna()
            
            logging.info(f"Data preprocessing completed. Final dataset size: {len(df)} records")
            return df
            
        except Exception as e:
            logging.error(f"Error in data preprocessing: {e}")
            return pd.DataFrame()
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """生成数据质量报告"""
        try:
            report = {
                'total_records': len(df),
                'date_range': {
                    'start': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
                    'end': df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
                },
                'missing_values': {},
                'outliers': {},
                'statistics': {}
            }
            
            numeric_columns = ['temperature', 'humidity', 'soil_moisture', 'light_intensity', 
                             'wind_speed', 'rainfall', 'air_pressure']
            
            for column in numeric_columns:
                if column in df.columns:
                    # 缺失值统计
                    missing_count = df[column].isnull().sum()
                    missing_percent = (missing_count / len(df)) * 100
                    report['missing_values'][column] = {
                        'count': missing_count,
                        'percentage': round(missing_percent, 2)
                    }
                    
                    # 异常值统计
                    outliers = self.detect_outliers(df, column)
                    outlier_count = outliers.sum()
                    outlier_percent = (outlier_count / len(df)) * 100
                    report['outliers'][column] = {
                        'count': outlier_count,
                        'percentage': round(outlier_percent, 2)
                    }
                    
                    # 基本统计
                    report['statistics'][column] = {
                        'mean': round(df[column].mean(), 2),
                        'std': round(df[column].std(), 2),
                        'min': round(df[column].min(), 2),
                        'max': round(df[column].max(), 2),
                        'q25': round(df[column].quantile(0.25), 2),
                        'q75': round(df[column].quantile(0.75), 2)
                    }
            
            return report
            
        except Exception as e:
            logging.error(f"Error generating data quality report: {e}")
            return {}

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = Config()
    preprocessor = DataPreprocessor(config)
    
    # 处理最近7天的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # 完整的数据预处理
    processed_df = preprocessor.process_data(
        start_date=start_date,
        end_date=end_date,
        remove_outliers=True,
        interpolate=True,
        smooth=False,
        normalize=False,
        create_features=True
    )
    
    # 生成数据质量报告
    if not processed_df.empty:
        quality_report = preprocessor.get_data_quality_report(processed_df)
        print("数据质量报告:")
        print(quality_report) 