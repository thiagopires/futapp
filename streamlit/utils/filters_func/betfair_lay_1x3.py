
def get_filter_betfair_lay_1x3(df):
    return (
        (df["Odd_H_FT"] > df["Odd_A_FT"])
        & (df["Odd_A_FT"] <= 2.1)
        & (df["Odd_CS_1x3_Lay"] <= 40)
        & (
            ((df['League'] == 'AUSTRALIA - A-LEAGUE') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'BRAZIL - SERIE A') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'DENMARK - SUPERLIGA') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.50-0.55')) |
            ((df['League'] == 'EUROPA CHAMPIONS LEAGUE') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'EUROPA LEAGUE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'EUROPA LEAGUE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'EUROPA LEAGUE') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'ITALY - SERIE B') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'NETHERLANDS - EERSTE DIVISIE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'NETHERLANDS - EERSTE DIVISIE') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'NETHERLANDS - EREDIVISIE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.50-0.55')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.45-0.50')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'ROMANIA - LIGA I') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.60-0.65')) |
            ((df['League'] == 'SCOTLAND - PREMIERSHIP') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.45-0.50')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'TURKEY - SÜPER LIG') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.55-0.60'))
        )
    )
