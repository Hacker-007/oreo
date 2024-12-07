import pandas as pd
from pmdarima import auto_arima
from tqdm import tqdm

UNEMPLOYED_DATA = "./data/Connecticut Unemployed.csv"
REAL_ESTATE_DATA = "./data/Real Estate.csv"


def main():
    unemployed_df = pd.read_csv(UNEMPLOYED_DATA).set_index('Date')
    predicted_df = None
    for town in tqdm(unemployed_df['Town'].unique()):
        model = auto_arima(
            unemployed_df[unemployed_df["Town"] == town]['Unemployed'],
            seasonal=True,
            m=12,
        )

        predicted = model.predict(n_periods=12)
        predicted.name = 'Unemployed'
        predicted = predicted.to_frame()
        predicted['Town'] = town
        if predicted_df is None:
            predicted_df = predicted
        else:
            predicted_df = pd.concat([predicted_df, predicted])

    predicted_df.to_csv('test.csv')

if __name__ == "__main__":
    main()
