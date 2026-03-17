
def get_filter_betfair_under25_ft(df):
    return (
        (df["Odd_Under25_FT"].between(1.7, 2.5))
        & (
            ((df['League'] == 'BELGIUM - PRO LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'BELGIUM - PRO LEAGUE') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'BELGIUM - PRO LEAGUE') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'BRAZIL - SERIE A') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'BRAZIL - SERIE B') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.50-0.55')) |
            ((df['League'] == 'BRAZIL - SERIE B') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'DENMARK - SUPERLIGA') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'ENGLAND - CHAMPIONSHIP') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.05-0.10')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE ONE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.05-0.10')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'FRANCE - LIGUE 1') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'FRANCE - LIGUE 2') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.00-0.05')) |
            ((df['League'] == 'FRANCE - LIGUE 2') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'FRANCE - LIGUE 2') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.30-0.35')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'ITALY - SERIE A') & (df['FX_Probabilidade_A'] == '0.75-0.84') & (df['FX_CV_HDA'] == '0.70-0.75')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.12-0.21') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.10-0.15')) |
            ((df['League'] == 'JAPAN - J1 LEAGUE') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'MEXICO - LIGA MX') & (df['FX_Probabilidade_A'] == '0.57-0.66') & (df['FX_CV_HDA'] == '0.35-0.40')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.21-0.30') & (df['FX_CV_HDA'] == '0.20-0.25')) |
            ((df['League'] == 'NORWAY - ELITESERIEN') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.15-0.20')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.66-0.75') & (df['FX_CV_HDA'] == '0.60-0.65')) |
            ((df['League'] == 'SAUDI ARABIA - SAUDI PROFESSION') & (df['FX_Probabilidade_A'] == '0.84-0.93') & (df['FX_CV_HDA'] == '0.55-0.60')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.39-0.48') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'SPAIN - LA LIGA') & (df['FX_Probabilidade_A'] == '0.48-0.57') & (df['FX_CV_HDA'] == '0.25-0.30')) |
            ((df['League'] == 'SPAIN - SEGUNDA DIVISIÓN') & (df['FX_Probabilidade_A'] == '0.30-0.39') & (df['FX_CV_HDA'] == '0.00-0.05'))
        )
    )
