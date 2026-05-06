
def get_filter_betfair_over25_ft(df):
    return (
        (df["Odd_Over25_FT"].between(1.7, 2.5))
        & (
            ((df['League'] == 'BELGIUM - PRO LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'BRAZIL - SERIE A') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.00-0.05')) |
            ((df['League'] == 'BRAZIL - SERIE A') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'DENMARK - SUPERLIGA') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'EUROPA CHAMPIONS LEAGUE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'EUROPA CHAMPIONS LEAGUE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'GERMANY - 2. BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'GERMANY - BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'GERMANY - BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'GERMANY - BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'NETHERLANDS - EERSTE DIVISIE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'NETHERLANDS - EERSTE DIVISIE') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'NETHERLANDS - EERSTE DIVISIE') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'NETHERLANDS - EREDIVISIE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.50-0.55')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.50-0.55')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.45-0.50')) |
            ((df['League'] == 'SPAIN - SEGUNDA DIVISIÓN') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'TURKEY - SÜPER LIG') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'TURKEY - SÜPER LIG') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.50-0.55'))
        )
    )
