
def get_filter_betfair_lay_visitante(df):
    return ( 
        (df['Odd_A_FT'].between(2.4, 5.5))
        & (df['Odd_H_FT'] < 2.6)
        & (df['Odd_H_FT'] < df['Odd_A_FT'])
        & (
            ((df['League'] == 'ARGENTINA - PRIMERA DIVISIÓN') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'BELGIUM - PRO LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'BELGIUM - PRO LEAGUE') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'BRAZIL - SERIE A') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'BRAZIL - SERIE A') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'BRAZIL - SERIE B') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'BRAZIL - SERIE B') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'DENMARK - SUPERLIGA') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE ONE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE ONE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'ENGLAND - PREMIER LEAGUE') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'GERMANY - BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'GERMANY - BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'GERMANY - BUNDESLIGA') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'ITALY - SERIE B') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'MEXICO - LIGA MX') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'MEXICO - LIGA MX') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'MEXICO - LIGA MX') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'MEXICO - LIGA MX') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'MEXICO - LIGA MX') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'NETHERLANDS - EERSTE DIVISIE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'NETHERLANDS - EREDIVISIE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'PORTUGAL - LIGA NOS') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.40-0.45'))
        )
    )
