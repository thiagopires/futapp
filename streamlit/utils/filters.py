
metodos = [
    'Back Casa',
    'Back Visitante',
    'Back Empate',
    'Lay Casa',
    'Lay Empate',
    'Lay Visitante',
    'Lay 0x1',
    'Lay 1x1',
    'Lay 0x2',
    'Lay 0x3',
    "Lay 2x2",
    'Lay Goleada Visitante',
    'Lay 0x1 e Lay 1x0',
    'Lay 0x3 e Lay 3x0',
    'Over 0.5 HT',
    'Under 0.5 HT',
    'Over 0.5 FT',
    'Over 1.5 FT',
    'Over 2.5 FT',
    'Under 1.5 FT',
    'Under 2.5 FT',
    'BTTS Sim',
    'BTTS Não',
    'Back Casa ou Back 1x1',
]

filtros_prontos =  [
    "Sem filtro",
    "Lay Visitante Zebra",
    'Lay Visitante v2',
    "Back Casa",
    "Back Empate",
    'Over 2.5 FT',
    # 'Under 2.5 FT',
    'BTTS Sim',
    'Lay 0x1 (até 80min)',
    'Lay 0x2 (até 80min)',
    'Lay 0x3 (até 80min)',
    'Lay 1x1 (até 60min)',
    # 'BTTS Não',
]

def get_details_filtro_pronto(df, condicao, metodo, filtro_pronto_selecionado):

    if filtro_pronto_selecionado == "Lay Visitante Zebra":
        filter = get_filter_lay_visitante_zebra(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay Visitante'

    elif filtro_pronto_selecionado == "Over 2.5 FT":
        filter = get_filter_over(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Over 2.5 FT'

    elif filtro_pronto_selecionado == "Under 2.5 FT":
        filter = get_filter_under(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Under 2.5 FT'

    elif filtro_pronto_selecionado == "BTTS Sim":
        filter = get_filter_btts_yes(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'BTTS Sim'
    
    # elif filtro_pronto_selecionado == "BTTS Não":
    #     filter = get_filter_btts_no(df)
    #     df = df[filter]
    #     if condicao: condicao = 'Geral'
    #     metodo = 'BTTS Não' 
    
    elif filtro_pronto_selecionado == "Back Empate":
        filter = get_filter_back_empate(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Back Empate'
    
    elif filtro_pronto_selecionado == "Lay 0x1 (até 80min)":
        filter = get_filter_lay_0x1(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 0x1'
    
    elif filtro_pronto_selecionado == "Lay 0x2 (até 80min)":
        filter = get_filter_lay_0x2(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 0x2'

    elif filtro_pronto_selecionado == "Lay 0x3 (até 80min)":
        filter = get_filter_lay_0x3(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 0x3'

    elif filtro_pronto_selecionado == "Lay 1x1 (até 60min)":
        filter = get_filter_lay_1x1(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 1x1'

    elif filtro_pronto_selecionado == "Back Casa":
        filter = get_filter_back_casa(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Back Casa'

    elif filtro_pronto_selecionado == "Lay Visitante v2":
        filter = get_filter_lay_visitante_v2(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay Visitante'

    return df, condicao, metodo

def get_result_filtro_pronto(df, metodo):

    df["Status_Metodo"] = "RED"
    df['Profit'] = -1.0
    odd_media = ""

    if metodo == 'Back Casa':
        filter = (df["Goals_H_FT"] > df["Goals_A_FT"])
        df.loc[filter, 'Profit'] = round(df['Odd_H_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_H_FT'].mean(), 2))}"

    if metodo == 'Back Casa ou Back 1x1':
        filter = df["Primeiro_Gol"].str.contains("Home")
        # filter2 = (df["Resultado_FT"] == '1-1')
        # filter = (filter1 | filter2)
        df.loc[filter, 'Profit'] = round(df['Odd_H_FT']-1, 2)
        # df.loc[filter2, 'Profit'] = 0
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_H_FT'].mean(), 2))}"

    elif metodo == 'Back Empate':
        filter = (df["Goals_H_FT"] == df["Goals_A_FT"])
        df.loc[filter, 'Profit'] = round(df['Odd_D_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_D_FT'].mean(), 2))}"

    elif metodo == 'Back Visitante':
        filter = (df["Goals_H_FT"] < df["Goals_A_FT"])
        df.loc[filter, 'Profit'] = round(df['Odd_A_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_A_FT'].mean(), 2))}"

    elif metodo == 'Lay Visitante':
        filter = (df['Goals_H_FT'] >= df['Goals_A_FT'])  
        df.loc[filter, 'Profit'] = round(df['Odd_DC_1X']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_A_FT'].mean(), 2))}"

    elif metodo == 'Lay Empate':
        filter = (df['Goals_H_FT'] != df['Goals_A_FT'])  
        df.loc[filter, 'Profit'] = round(df['Odd_DC_12']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_D_FT'].mean(), 2))}"

    elif metodo == 'Lay Casa':
        filter = (df['Goals_H_FT'] <= df['Goals_A_FT'])   
        df.loc[filter, 'Profit'] = round(df['Odd_DC_X2']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_H_FT'].mean(), 2))}"

    elif metodo == 'Over 0.5 HT':
        filter = (df['TotalGoals_HT'] >= 0.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Over05_HT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over05_HT'].mean(), 2))}"

    elif metodo == 'Over 0.5 FT':
        filter = (df['TotalGoals_FT'] >= 0.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Over05_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over05_FT'].mean(), 2))}"

    elif metodo == 'Over 1.5 FT':
        filter = (df['TotalGoals_FT'] >= 1.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Over15_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over15_FT'].mean(), 2))}"

    elif metodo == 'Over 2.5 FT':
        filter = (df['TotalGoals_FT'] >= 2.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Over25_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over25_FT'].mean(), 2))}"

    elif metodo == 'Under 0.5 HT':
        filter = (df['TotalGoals_HT'] <= 0.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Under05_HT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Under05_HT'].mean(), 2))}"
        
    elif metodo == 'Under 1.5 FT':
        filter = (df['TotalGoals_FT'] <= 1.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Under15_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Under15_FT'].mean(), 2))}"

    elif metodo == 'Under 2.5 FT':
        filter = (df['TotalGoals_FT'] <= 2.5)   
        df.loc[filter, 'Profit'] = round(df['Odd_Under25_FT']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Under25_FT'].mean(), 2))}"

    elif metodo == 'BTTS Sim':
        filter = ((df['Goals_H_FT'] >= 1) & (df['Goals_A_FT'] >= 1))
        df.loc[filter, 'Profit'] = round(df['Odd_BTTS_Yes']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_BTTS_Yes'].mean(), 2))}"

    elif metodo == 'BTTS Não':
        filter = ((df['Goals_H_FT'] == 0) | (df['Goals_A_FT'] == 0))
        df.loc[filter, 'Profit'] = round(df['Odd_BTTS_No']-1, 2)
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_BTTS_No'].mean(), 2))}"

    elif metodo == 'Lay 0x1':
        df.loc[(df["Resultado_80"] != '0-1'), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 1x1':
        df.loc[df["Resultado_60"] != '1-1', "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 0x2':
        df.loc[df["Resultado_80"] != '0-2', "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 0x3':
        df.loc[df["Resultado_80"] != '0-3', "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 2x2':
        df.loc[df["Resultado_60"] != '2-2', "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay Goleada Visitante':
        df.loc[((df['Goals_A_FT'] < 4) | (df['Goals_A_FT'] <= df['Goals_H_FT'])), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 0x1 e Lay 1x0':
        df.loc[((df["Resultado_80"] != '0-1') & (df["Resultado_80"] != '1-0')), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 0x3 e Lay 3x0':
        df.loc[((df["Resultado_80"] != '0-3') & (df["Resultado_80"] != '3-0')), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    return df, odd_media

def get_filter_over(df):
    return (
        (df["XG_Home_Pre"] >= 1.3) &
        (df["XG_Away_Pre"] >= 1.3) &
        ((df["XG_Total_Pre"] < 2.8) | (df["XG_Total_Pre"] > 3)) &
        (df["Odd_Over25_FT"] >= 1.3) # &
        &
        (df['League'].isin([
            'PORTUGAL - LIGA NOS',
            'GERMANY - BUNDESLIGA',
            'NETHERLANDS - EREDIVISIE',
            'ENGLAND - CHAMPIONSHIP',
            'ENGLAND - EFL LEAGUE ONE',
            'TURKEY - SÜPER LIG',
            'GERMANY - 2. BUNDESLIGA',
            'SERBIA - SUPERLIGA',
            'ENGLAND - PREMIER LEAGUE',
            'SPAIN - SEGUNDA DIVISIÓN'
        ]))
    )

def get_filter_under(df):
    return (
        (df["XG_Home_Pre"] > 0) &
        (df["XG_Away_Pre"] > 0) &  
        (df["XG_Home_Pre"] < 1.3) &
        (df["XG_Away_Pre"] < 1.3) &
        (df["Odd_Under25_FT"] >= 1.5) # & 
        # (
        #     (
        #         (df["Odd_H_FT"] < df["Odd_A_FT"]) &
        #         (df['League'].isin([
        #             'Belgium Pro League',
        #             # 'Netherlands Eredivisie',
        #             'Portugal Liga NOS',
        #             # 'Germany Bundesliga',
        #             # 'France Ligue 1',
        #             'England EFL League One',
        #             'England Premier League',
        #             'Netherlands Eerste Divisie'
        #         ]))
        #         ) | (
        #         (df["Odd_H_FT"] > df["Odd_A_FT"]) &
        #         (df['League'].isin([
        #             # 'Turkey Süper Lig',
        #             'England Premier League',
        #             'England EFL League Two',
        #             # 'France Ligue 2',
        #             'Italy Serie B',
        #             'Portugal Liga NOS',
        #             'Spain Segunda División',
        #             'Belgium Pro League',
        #             'England Championship'
        #         ]))
        #     )
        # )
    )

def get_filter_btts_yes(df):
    return (
        (df["XG_Home_Pre"] >= 1.3) &
        (df["XG_Away_Pre"] >= 1.3) &
        (df["Odd_BTTS_Yes"] >= 1.4) 
        &
        (df['League'].isin([
            'SPAIN - SEGUNDA DIVISIÓN',
            'NETHERLANDS - EREDIVISIE',
            'GERMANY - BUNDESLIGA',
            'SERBIA - SUPERLIGA',
            'ENGLAND - PREMIER LEAGUE',
            'FRANCE - LIGUE 1',
            'SPAIN - LA LIGA',
        ]))
    )

def get_filter_btts_no(df):
    return (
        (df["XG_Home_Pre"] > 0) &
        (df["XG_Away_Pre"] > 0) &
        (df["XG_Home_Pre"] < 1.3) &
        (df["XG_Away_Pre"] < 1.3) &
        (df["Odd_BTTS_No"] >= 1.6) 
        # & 
        # (
        #     (
        #         (df["Odd_H_FT"] < df["Odd_A_FT"]) &
        #         (df['League'].isin([
        #             'Belgium Pro League',
        #             # 'Netherlands Eerste Divisie',
        #             'England EFL League One',
        #             'Netherlands Eredivisie',
        #             # 'England Premier League'
        #         ]))
        #         ) | (
        #         (df["Odd_H_FT"] > df["Odd_A_FT"]) &
        #         (df['League'].isin([
        #             'Belgium Pro League',
        #             'England EFL League One',
        #             'Portugal Liga NOS',
        #             'Italy Serie B',
        #             'Germany 2. Bundesliga',
        #             # 'England Championship',
        #             'England EFL League Two',
        #             'Spain Segunda División',
        #             'France Ligue 2'
        #         ]))
        #     )
        # )
    )

def get_filter_lay_0x1(df):
    return (
        (df["Odd_H_FT"] < df["Odd_A_FT"]) &
        (df["Odd_H_FT"] > 1.5) &
        ((df["Odd_H_FT"] < 2.45) | (df["Odd_H_FT"] > 2.55)) &
        (df["XG_Away_Pre"] > 1.12) &
        (df["XG_Home_Pre"] > df["XG_Away_Pre"]) &
        (df["Odd_BTTS_Yes"] > 1.5) & (df["Odd_BTTS_Yes"] < 2) &
        (df["Odd_Over25_FT"] > 1.62) & (df["Odd_Over25_FT"] < 2) 
        &
        (df['League'].isin([
            'ENGLAND - CHAMPIONSHIP',
            'ENGLAND - EFL LEAGUE ONE',
            'ENGLAND - PREMIER LEAGUE',
            'GERMANY - 2. BUNDESLIGA',
            'GERMANY - BUNDESLIGA',
            'ITALY - SERIE A',
            'NETHERLANDS - EREDIVISIE',
            'PORTUGAL - LIGA NOS',
            'ROMANIA - LIGA I',
            'SPAIN - LA LIGA',
            'TURKEY - SÜPER LIG',
            'FRANCE - LEAGUE 1'
        ]))
    )

def get_filter_lay_visitante_zebra(df):
    return (
        (df["Odd_H_FT"] < df["Odd_D_FT"]) &
        (df["Odd_D_FT"] < df["Odd_A_FT"]) &
        ((df["Odd_H_FT"] <= 1.8) | (df["Odd_H_FT"] >= 1.9)) &
        ((df["Odd_D_FT"] < 3.4) | (df["Odd_D_FT"] > 3.6)) &
        (df["Odd_H_FT"] >= 1.3) &
        (df["Odd_A_FT"] < 8) &
        # (df["Odd_BTTS_Yes"] < 2) &
        (df["Odd_BTTS_No"] >= 1.8) &
        (df["Odd_Over25_FT"] > 1.5) &
        (df["XG_Home_Pre"] > df["XG_Away_Pre"]) &
        (df["XG_Total_Pre"] >= 1.7) & # (df["XG_Total_Pre"] <= 2.6) &
        (df["XG_Away_Pre"] <= 1.25) 
        &
        (df['League'].isin([
            'POLAND - EKSTRAKLASA',
            'ENGLAND - PREMIER LEAGUE',
            'GERMANY - 2. BUNDESLIGA',
            'SPAIN - SEGUNDA DIVISIÓN',
            'FRANCE - LIGUE 1',
            'ENGLAND - EFL LEAGUE ONE',
            'TURKEY - SÜPER LIG'
        ]))
    )

def get_filter_back_empate(df):
    return (
        (df["Odd_H_FT"] > 1.5) & (df["Odd_H_FT"] <= 5) &
        (df["Odd_D_FT"] > 2.6) & (df["Odd_D_FT"] < 5.5) &
        (df["Odd_A_FT"] <= 5.5) &
        (df["XG_Home_Pre"] > 1.06) & (df["XG_Home_Pre"] < 1.7) &
        (df["XG_Away_Pre"] >= 0.85) & (df["XG_Away_Pre"] < 1.7) &
        (df["XG_Total_Pre"] >= 2.13) & (df["XG_Total_Pre"] < 3.2) &
        (df["Diff_XG_Home_Away_Pre"] > -0.5) &
        # (("PPG_Home_Pre" in df.columns) & (df["PPG_Home_Pre"] > 0.25) if "PPG_Home_Pre" in df.columns else True) &
        # (("PPG_Away_Pre" in df.columns) & (df["PPG_Away_Pre"] < 3) if "PPG_Away_Pre" in df.columns else True) &
        (df["Odd_Under25_FT"] > 1.45) & (df["Odd_Under25_FT"] < 2.57) &
        (df["Odd_BTTS_Yes"] > 1.49) & (df["Odd_BTTS_Yes"] < 2.2) &
        (df["Odd_BTTS_No"] >= 1.7) & (df["Odd_BTTS_No"] <= 2.38) &
        ((df["Odd_H_FT"] < 1.9) | (df["Odd_H_FT"] > 2.1)) &
        ((df["Odd_A_FT"] < 1.9) | (df["Odd_A_FT"] > 2.1)) 
        &
        (df['League'].isin([
            #'DENMARK - SUPERLIGA',
            'TURKEY - SÜPER LIG',
            'ROMANIA - LIGA I',
            'ITALY - SERIE A',
            'BELGIUM - PRO LEAGUE',
            'ENGLAND - PREMIER LEAGUE'
        ]))
    )

def get_filter_lay_1x1(df):
    return (
        (df["Odd_H_FT"] < df["Odd_A_FT"]) &
        (df["Odd_H_FT"].between(1.2, 1.4)) &
        (df["Odd_BTTS_Yes"] <= 2.75) &
        (~ df["Odd_Over25_FT"].between(1.44, 1.45)) &
        (df["XG_Away_Pre"] >= 0.5)
        &
        (df['League'].isin([
            'SPAIN - LA LIGA',
            'ITALY - SERIE A',
            'GERMANY - BUNDESLIGA',
            'NETHERLANDS - EREDIVISIE',
            'ENGLAND - CHAMPIONSHIP',
            'BELGIUM - PRO LEAGUE',
            # 'PORTUGAL - LIGA NOS',
            'NETHERLANDS - EERSTE DIVISIE',

        ]))
    )

def get_filter_lay_0x2(df):
    return (
        (df["XG_Away_Pre"] > 0) &
        (df["Diff_XG_Home_Away_Pre"] > 0.66) 
        &
        (df['League'].isin([
            'BELGIUM - PRO LEAGUE',
            'ENGLAND - EFL LEAGUE ONE',
            'ENGLAND - PREMIER LEAGUE',
            'FRANCE - LIGUE 1',
            'GERMANY - 2. BUNDESLIGA',
            'GERMANY - BUNDESLIGA',
            'ITALY - SERIE A',
            'ITALY - SERIE B',
            'PORTUGAL - LIGA NOS',
            'SPAIN - LA LIGA',
            'SPAIN - SEGUNDA DIVISIÓN',
            'TURKEY - SÜPER LIG'
        ]))
    )

def get_filter_lay_0x3(df):
    return (
        (df["Odd_H_FT"] < df["Odd_A_FT"]) &
        (df["XG_Home_Pre"] > 0) &
        (df["XG_Away_Pre"] > 0) &
        (df["XG_Away_Pre"] <= 2) &
        (df["Odd_H_FT"] <= 2) &
        (df["Odd_A_FT"] >= 6.5) 
        &
        (df['League'].isin([
            'ENGLAND - CHAMPIONSHIP',
            'ENGLAND - PREMIER LEAGUE',
            'FRANCE - LIGUE 1',
            'GERMANY - 2. BUNDESLIGA',
            'GERMANY - BUNDESLIGA',
            'ITALY - SERIE A',
            'NETHERLANDS - EREDIVISIE',
            'PORTUGAL - LIGA NOS',
            'ROMANIA - LIGA I',
            'SPAIN - LA LIGA',
            'SPAIN - SEGUNDA DIVISIÓN',
            'TURKEY - SÜPER LIG'
        ]))
    )

def get_filter_back_casa(df):
    return (
        (df["Odd_H_FT"].between(1.3, 2.5)) &
        (df["XG_Total_Pre"] > 2) &
        (df["XG_Home_Pre"] > 1) &
        (df["XG_Away_Pre"] > 0) & (df["XG_Away_Pre"] < 2.1) &
        (df["Odd_Over25_FT"] <= 2.55) & 
        (
            ((df['League'] == 'ENGLAND - CHAMPIONSHIP') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (df["CV_HDA_FT"].between(0.15, 0.39))) |
            
            ((df['League'] == 'ENGLAND - EFL LEAGUE ONE') 
                & (df["Probabilidade_H_FT"].between(0.52, 0.61))
                & (df["CV_HDA_FT"].between(0.3, 0.39))) |
            
            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') 
                & (df["Probabilidade_H_FT"].between(0.32, 0.41))
                & (df["CV_HDA_FT"].between(0, 0.19))) |

            ((df['League'] == 'FRANCE - LIGUE 2') 
                & (df["Probabilidade_H_FT"].between(0.32, 0.41))
                & (df["CV_HDA_FT"].between(0, 0.14))) |

            ((df['League'] == 'FRANCE - LIGUE 2') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (df["CV_HDA_FT"].between(0.1, 0.14))) |

            ((df['League'] == 'GERMANY - BUNDESLIGA') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (~df["CV_HDA_FT"].between(0.2, 0.24))) |

            ((df['League'] == 'GERMANY - BUNDESLIGA') 
                & (df["Probabilidade_H_FT"].between(0.52, 0.61))
                & (df["CV_HDA_FT"].between(0, 0.44))) |

            ((df['League'] == 'SPAIN - LA LIGA') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (df["CV_HDA_FT"].between(0.15, 0.19))) |

            ((df['League'] == 'TURKEY - SÜPER LIG') 
                & (~df["Probabilidade_H_FT"].between(0.52, 0.61))) |

            ((df['League'] == 'WALES - WELSH PREMIER LEAGUE') 
                & (df["Probabilidade_H_FT"].between(0.62, 0.81)))

            # ((df['League'] == 'ARGENTINA - PRIMERA DIVISIÓN') 
            #     & (df["Probabilidade_H_FT"].between(0.62, 0.71))) |

            # ((df['League'] == 'BRAZIL - SERIE A') 
            #     & (df["Probabilidade_H_FT"].between(0.62, 0.71))) |

            # ((df['League'] == 'BRAZIL - SERIE B') 
            #     & (df["Probabilidade_H_FT"].between(0.62, 0.71)))
    
        )
    )

def get_filter_lay_visitante_v2(df):
    return (
        (df["Odd_H_FT"] < df["Odd_A_FT"]) &
        (df["Odd_H_FT"].between(1.3, 2.5)) &
        (df["XG_Total_Pre"] > 0) &
        (df["Odd_Over25_FT"] >= 1.4) &
        (df["Odd_H_FT"] < 6) &
        (
            ((df['League'] == 'BELGIUM - PRO LEAGUE') 
                & (df["Probabilidade_H_FT"].between(0.32, 0.61))) |

            ((df['League'] == 'DENMARK - SUPERLIGA') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (~df["CV_HDA_FT"].between(0.1, 0.14))) |

            ((df['League'] == 'ENGLAND - CHAMPIONSHIP') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (df["CV_HDA_FT"].between(0.15, 0.19))) |

            ((df['League'] == 'ENGLAND - CHAMPIONSHIP') 
                & (df["Probabilidade_H_FT"].between(0.52, 0.61))
                & (df["CV_HDA_FT"].between(0.25, 0.29))) |

            ((df['League'] == 'ENGLAND - CHAMPIONSHIP') 
                & (df["Probabilidade_H_FT"].between(0.52, 0.61))
                & (df["CV_HDA_FT"].between(0.35, 0.39))) |
            
            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') 
                & (df["Probabilidade_H_FT"].between(0.32, 0.41))) | 

            ((df['League'] == 'ENGLAND - EFL LEAGUE TWO') 
                & (df["Probabilidade_H_FT"].between(0.52, 0.61))
                & (~df["CV_HDA_FT"].between(0.25, 0.29))) |

            ((df['League'] == 'PORTUGAL - LIGA NOS') 
                & (df["Probabilidade_H_FT"].between(0.32, 0.51))) |

            ((df['League'] == 'SPAIN - SEGUNDA DIVISIÓN') 
                & (df["Probabilidade_H_FT"].between(0.42, 0.51))
                & (df["CV_HDA_FT"].between(0.2, 0.24))) |

            ((df['League'] == 'PORTUGAL - LIGA NOS') ) |

            ((df['League'] == 'TURKEY - SÜPER LIG') )

        )
    )
