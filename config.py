import os
from datetime import datetime


class Config:
    STEAM_API_KEY = os.getenv("STEAM_API_KEY", "apisteamhere")
    
    #crawler settings
    MAX_CONCURRENT_PLAYER_REQUESTS = 50
    MAX_CONCURRENT_STORE_REQUESTS = 3
    STORE_API_DELAY = 1.5  
    REQUEST_TIMEOUT = 10   
    RETRY_DELAY = 10    
    
    #file paths
    DATA_RAW_DIR = "data/raw"
    DATA_PROCESSED_DIR = "data/processed"
    
    #file naming
    @staticmethod
    def get_crawl_filename():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"steam_data_{timestamp}.xlsx"
    
    #processing settings
    MIN_GAME_OCCURRENCES = 20
    MIN_PLAYERS_THRESHOLD = 0
    
    # Output filename
    ANALYSIS_OUTPUT = "steam_analysis.xlsx"
    
    #logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'