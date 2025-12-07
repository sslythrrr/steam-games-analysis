import pandas as pd
import glob
import os
import numpy as np
from config import Config


def load_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        
        if not all(col in df.columns for col in ['id', 'name', 'players']):
            return None
        
        df['id'] = df['id'].astype(str)
        df['players'] = pd.to_numeric(df['players'], errors='coerce').fillna(0)
        df = df[df['players'] > 0].copy()
        
        return df
    except:
        return None


def process_data():
    print("="*50)
    print("Processing Steam Data")
    print("="*50)
    
    excel_files = glob.glob(os.path.join(Config.DATA_RAW_DIR, "*.xlsx"))
    
    if not excel_files:
        print("No data files found!")
        return
    
    print(f"Loading {len(excel_files)} files...")
    
    data_frames = [load_data(f) for f in excel_files]
    valid_dfs = [df for df in data_frames if df is not None]
    
    if not valid_dfs:
        print("No valid data!")
        return
    
    #count occurrences
    game_counts = {}
    for df in valid_dfs:
        for game in df['name'].unique():
            game_counts[game] = game_counts.get(game, 0) + 1
    
    common_games = [g for g, c in game_counts.items() if c >= Config.MIN_GAME_OCCURRENCES]
    print(f"Analyzing {len(common_games)} games...")
    
    #filter
    filtered_dfs = []
    for df in valid_dfs:
        filtered_dfs.append(df[df['name'].isin(common_games)].copy() if df is not None else None)
    
    #merge
    merged = pd.concat([df for df in filtered_dfs if df is not None], ignore_index=True)
    
    #aggregate
    final = merged.groupby(['id', 'name'])['players'].sum().reset_index()
    final.sort_values(by='players', ascending=False, inplace=True)
    final.rename(columns={'players': 'total_player'}, inplace=True)
    
    #calculate trends
    trends = []
    for game in common_games:
        values = []
        for df in filtered_dfs:
            if df is not None and game in df['name'].values:
                values.append(df.loc[df['name'] == game, 'players'].iloc[0])
        
        if len(values) > 1:
            diff = pd.Series(values).diff()
            trends.append({
                'name': game,
                'max_increase': diff.max(),
                'max_decrease': diff.min(),
                'average_change': diff.mean()
            })
        else:
            trends.append({
                'name': game,
                'max_increase': 0,
                'max_decrease': 0,
                'average_change': 0
            })
    
    trends_df = pd.DataFrame(trends)
    final = pd.merge(final, trends_df, on='name')
    
    #build time series
    game_data = {}
    for file_idx, df in enumerate(filtered_dfs):
        if df is None:
            continue
        for _, row in df.iterrows():
            game = row['name']
            if game in common_games:
                if game not in game_data:
                    game_data[game] = [0] * len(excel_files)
                game_data[game][file_idx] = row['players']
    
    file_cols = [os.path.splitext(os.path.basename(f))[0] for f in excel_files]
    matrix = pd.DataFrame.from_dict(game_data, orient='index', columns=file_cols)
    matrix = matrix.replace(0, np.nan)
    matrix['average_player'] = matrix.mean(axis=1)
    
    for col in file_cols:
        matrix[col].fillna(matrix['average_player'], inplace=True)
    
    final = pd.merge(final, matrix, left_on='name', right_index=True)
    
    #reorder columns
    avg_col = final.pop('average_player')
    final.insert(final.columns.get_loc('total_player') + 1, 'average_player', avg_col)
    
    #save
    os.makedirs(Config.DATA_PROCESSED_DIR, exist_ok=True)
    output = os.path.join(Config.DATA_PROCESSED_DIR, Config.ANALYSIS_OUTPUT)
    final.to_excel(output, index=False, engine='openpyxl')
    
    print(f"Saved to: {output}")
    print(f"Total games: {len(final)}")
    print("Done!")


if __name__ == "__main__":
    process_data()