import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Read dataset
@st.cache_data
def load_data():
    df = pd.read_excel("btbs_zip_poisson_model.xlsx")  # Replace with the path to your Excel file
    return df

def format_percentage(value):
    return f"{int(value * 100)}%"

def predict_outcome(home_prob, draw_prob, away_prob):
    if home_prob > draw_prob and home_prob > away_prob:
        return 'Home Win'
    elif draw_prob > home_prob and draw_prob > away_prob:
        return 'Draw'
    else:
        return 'Away Win'

def predict_goals(over_prob, under_prob, threshold):
    if over_prob > under_prob:
        return f'Over {threshold}'
    else:
        return f'Under {threshold}'

def filter_dates(df):
    dates = pd.to_datetime(df['match_date']).dt.date.unique()
    return [datetime.strptime(str(date), '%Y-%m-%d').date() for date in dates]

def get_matches_for_date(df, selected_date):
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    return df[df['match_date'].str.startswith(selected_date_str)]

def display_matches_by_league(matches):
    for league, league_matches in matches.groupby('division'):
        st.subheader(f"Matches for {league}")
        output_df = pd.DataFrame(columns=['Match', 'Home Win', 'Draw', 'Away Win', 'O/U 1.5', 'O/U 2.5', 'Outcome Prediction'])
        for index, row in league_matches.iterrows():
            match_data = {
                'Match': row['match_teams'],
                'Home Win': row['home_win_prob'],
                'Draw': row['draw_prob'],
                'Away Win': row['away_win_prob'],
                'O/U 1.5': predict_goals(row['over_15_prob'], row['under_15_prob'], 1.5),
                'O/U 2.5': predict_goals(row['over_25_prob'], row['under_25_prob'], 2.5),
                'Outcome Prediction': predict_outcome(row['home_win_prob'], row['draw_prob'], row['away_win_prob'])
            }
            output_df = pd.concat([output_df, pd.DataFrame([match_data])], ignore_index=True)
        
        # Format percentages to two decimal places
        output_df[['Home Win', 'Draw', 'Away Win']] = output_df[['Home Win', 'Draw', 'Away Win']].applymap(lambda x: "{:.2f}%".format(x * 100))
        
        output_df = output_df[['Match', 'Home Win', 'Draw', 'Away Win', 'O/U 1.5', 'O/U 2.5', 'Outcome Prediction']]
        st.dataframe(output_df, width=1500)  # Adjust width as per your preference


def main():
    # Load data
    df = load_data()

    # Date selector
    st.title('Soccer Prediction App ⚽🥅')
    selected_date = st.date_input('Select a date:', min_value=min(filter_dates(df)), max_value=max(filter_dates(df)))

    # Filter matches for selected date
    matches_for_date = get_matches_for_date(df, selected_date)

    # Display matches by league
    display_matches_by_league(matches_for_date)

if __name__ == "__main__":
    main()
