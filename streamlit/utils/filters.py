import numpy as np

from utils.filters_func import *

def profit_no_comission(odd, side='Back'):
    comission = 0.028
    if side == 'Back':
        profit = (odd - 1) * (1 - comission)
    elif side == 'Lay':
        profit = (1 / (odd - 1)) * (1 - comission)
    return round(profit, 2)

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
    'Lay 1x3',
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

metodos_tabs = [
    'Back Casa',
    'Back Visitante',
    'Lay Casa',
    'Lay Visitante',
    'Lay 0x1',
    'Lay 0x2',
    'Lay 0x3',
    'Lay 1x3',
    'Lay 0x1 75min',
    'Lay 0x2 75min',
    'Lay 0x3 75min',
    'Lay 1x3 75min',
    'Lay Goleada Visitante',
    'Over 0.5 HT',
    'Under 0.5 HT',
    'Over 2.5 FT',
    'Under 2.5 FT',
    'BTTS Sim'
]

filtros_prontos =  {
    'FootyStats' : [
        "Sem filtro",
        "Lay Visitante Zebra",
        'Lay Visitante v2',
        "Back Casa",
        "Back Empate",
        'Over 2.5 FT',
        'BTTS Sim',
        'Lay 0x1 (até 80min)',
        'Lay 0x2 (até 80min)',
        'Lay 0x3 (até 80min)',
        'Lay 1x1 (até 60min)'
    ],
    'Betfair': [
        "Sem filtro",
        'BF - Lay Visitante',
        # 'BF - Over 2.5 FT',
        # 'BF - Under 2.5 FT',
        # 'BF - BTTS Sim',
        'BF - Over 0.5 HT',
        # 'BF - Under 0.5 HT',
        'BF - Lay 0x1 (até 75min)',
        'BF - Lay 0x2 (até 75min)',
        'BF - Lay 0x3 (até 75min)',
        'BF - Lay 1x3 (até 75min)',
    ]
}

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

    elif filtro_pronto_selecionado == "BTTS Sim":
        filter = get_filter_btts_yes(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'BTTS Sim'
    
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

    elif filtro_pronto_selecionado == "BF - Lay Visitante":
        filter = get_filter_betfair_lay_visitante(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay Visitante'

    elif filtro_pronto_selecionado == "BF - Lay 0x1 (até 75min)":
        filter = get_filter_betfair_lay_0x1(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 0x1 75min'

    elif filtro_pronto_selecionado == "BF - Lay 0x2 (até 75min)":
        filter = get_filter_betfair_lay_0x2(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 0x2 75min'

    elif filtro_pronto_selecionado == "BF - Lay 0x3 (até 75min)":
        filter = get_filter_betfair_lay_0x3(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 0x3 75min'

    elif filtro_pronto_selecionado == "BF - Lay 1x3 (até 75min)":
        filter = get_filter_betfair_lay_1x3(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Lay 1x3 75min'

    elif filtro_pronto_selecionado == "BF - Over 2.5 FT":
        filter = get_filter_betfair_over25_ft(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Over 2.5 FT'

    elif filtro_pronto_selecionado == "BF - Under 2.5 FT":
        filter = get_filter_betfair_under25_ft(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Under 2.5 FT'

    elif filtro_pronto_selecionado == "BF - BTTS Sim":
        filter = get_filter_betfair_btts_yes(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'BTTS Sim'

    elif filtro_pronto_selecionado == "BF - Over 0.5 HT":
        filter = get_filter_betfair_over05_ht(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Over 0.5 HT'

    elif filtro_pronto_selecionado == "BF - Under 0.5 HT":
        filter = get_filter_betfair_under05_ht(df)
        df = df[filter]
        if condicao: condicao = 'Geral'
        if metodo: metodo = 'Under 0.5 HT'

    return df, condicao, metodo

def get_result_filtro_pronto(df, metodo):

    df["Status_Metodo"] = "RED"
    df['Profit'] = -1.0
    odd_media = ""

    if metodo == 'Back Casa':
        filter = (df["Goals_H_FT"] > df["Goals_A_FT"])
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_H_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_H_FT'].mean(), 2))}"

    if metodo == 'Back Casa ou Back 1x1':
        filter = df["Primeiro_Gol"].str.contains("Home")
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_H_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_H_FT'].mean(), 2))}"

    elif metodo == 'Back Empate':
        filter = (df["Goals_H_FT"] == df["Goals_A_FT"])
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_D_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_D_FT'].mean(), 2))}"

    elif metodo == 'Back Visitante':
        filter = (df["Goals_H_FT"] < df["Goals_A_FT"])
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_A_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_A_FT'].mean(), 2))}"

    elif metodo == 'Lay Visitante':
        filter = (df['Goals_H_FT'] >= df['Goals_A_FT'])  
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_DC_1X'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_A_FT'].mean(), 2))}"

    elif metodo == 'Lay Empate':
        filter = (df['Goals_H_FT'] != df['Goals_A_FT'])  
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_DC_12'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_D_FT'].mean(), 2))}"

    elif metodo == 'Lay Casa':
        filter = (df['Goals_H_FT'] <= df['Goals_A_FT'])   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_DC_X2'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_H_FT'].mean(), 2))}"

    elif metodo == 'Over 0.5 HT':
        filter = (df['TotalGoals_HT'] >= 0.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Over05_HT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over05_HT'].mean(), 2))}"

    elif metodo == 'Over 0.5 FT':
        filter = (df['TotalGoals_FT'] >= 0.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Over05_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over05_FT'].mean(), 2))}"

    elif metodo == 'Over 1.5 FT':
        filter = (df['TotalGoals_FT'] >= 1.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Over15_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over15_FT'].mean(), 2))}"

    elif metodo == 'Over 2.5 FT':
        filter = (df['TotalGoals_FT'] >= 2.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Over25_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Over25_FT'].mean(), 2))}"

    elif metodo == 'Under 0.5 HT':
        filter = (df['TotalGoals_HT'] <= 0.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Under05_HT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Under05_HT'].mean(), 2))}"
        
    elif metodo == 'Under 1.5 FT':
        filter = (df['TotalGoals_FT'] <= 1.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Under15_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Under15_FT'].mean(), 2))}"

    elif metodo == 'Under 2.5 FT':
        filter = (df['TotalGoals_FT'] <= 2.5)   
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_Under25_FT'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_Under25_FT'].mean(), 2))}"

    elif metodo == 'BTTS Sim':
        filter = ((df['Goals_H_FT'] >= 1) & (df['Goals_A_FT'] >= 1))
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_BTTS_Yes'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_BTTS_Yes'].mean(), 2))}"

    elif metodo == 'BTTS Não':
        filter = ((df['Goals_H_FT'] == 0) | (df['Goals_A_FT'] == 0))
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_BTTS_No'])
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_BTTS_No'].mean(), 2))}"

    elif metodo == 'Lay 0x1 75min':
        df = df[df['Odd_CS_0x1_Lay'] > 0] 
        df['Profit'] =  np.where(df['Resultado_75'] == '0-1', -0.25,
                        np.where(df['Resultado_75'] == '0-0', -0.08, profit_no_comission(df['Odd_CS_0x1_Lay'],'Lay')))
        df['Status_Metodo']  = np.where(df['Profit'] >= 0, 'GREEN', 'RED')
        odd_media = f"{str(round(df['Odd_CS_0x1_Lay'].mean(), 2))}"

    elif metodo == 'Lay 0x1':
        df = df[df['Odd_CS_0x1_Lay'] > 0]
        filter = (df["Resultado_FT"] != '0-1')
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_CS_0x1_Lay'],'Lay')
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_CS_0x1_Lay'].mean(), 2))}"

    elif metodo == 'Lay 1x1':
        df.loc[(df["Resultado_80"] != '1-1'), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 0x2 75min':
        df = df[df['Odd_CS_0x2_Lay'] > 0]
        df['Profit'] =  np.where(df['Resultado_75'] == '0-2', -0.25,
                        np.where(df['Resultado_75'] == '0-1', -0.08,
                        np.where(df['Resultado_75'] == '0-0', profit_no_comission(df['Odd_CS_0x2_Lay'],'Lay') * 0.5, profit_no_comission(df['Odd_CS_0x2_Lay'],'Lay'))))
        
        df['Status_Metodo'] =   np.where(df['Resultado_75'].isin(['0-1','0-2']), 'RED',
                                np.where(df['Resultado_75'] == '0-0', 'VOID', 'GREEN'))
        
        odd_media = f"{str(round(df['Odd_CS_0x2_Lay'].mean(), 2))}"

    elif metodo == 'Lay 0x2':
        df = df[df['Odd_CS_0x2_Lay'] > 0]
        filter = (df["Resultado_FT"] != '0-2')
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_CS_0x2_Lay'],'Lay')
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_CS_0x2_Lay'].mean(), 2))}"

    elif metodo == 'Lay 0x3 75min':
        df = df[df['Odd_CS_0x3_Lay'] > 0]
        df['Profit'] =  np.where(df['Resultado_75'] == '0-3', -0.25,
                        np.where(df['Resultado_75'] == '0-2', -0.08, profit_no_comission(df['Odd_CS_0x3_Lay'],'Lay') ))
        
        df['Status_Metodo'] =   np.where(df['Resultado_75'].isin(['0-2','0-3']), 'RED',
                                np.where(df['Resultado_75'].isin(['0-0','0-1']), 'VOID', 'GREEN'))
        
        odd_media = f"{str(round(df['Odd_CS_0x3_Lay'].mean(), 2))}"
        
    elif metodo == 'Lay 0x3':
        df = df[df['Odd_CS_0x3_Lay'] > 0]
        filter = (df["Resultado_FT"] != '0-3')
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_CS_0x3_Lay'],'Lay')
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_CS_0x3_Lay'].mean(), 2))}"

    elif metodo == 'Lay 1x3 75min':
        df = df[df['Odd_CS_1x3_Lay'] > 0] 
        df['Profit'] =  np.where(df['Resultado_75'] == '1-3', -0.25,
                        np.where(df['Resultado_75'] == '0-3', -0.08,
                        np.where(df['Resultado_75'] == '1-2', -0.08, profit_no_comission(df['Odd_CS_1x3_Lay'],'Lay'))))
        df['Status_Metodo']  = np.where(df['Profit'] >= 0, 'GREEN', 'RED')
        odd_media = f"{str(round(df['Odd_CS_1x3_Lay'].mean(), 2))}"

    elif metodo == 'Lay 1x3':
        df = df[df['Odd_CS_1x3_Lay'] > 0]
        filter = (df["Resultado_FT"] != '1-3')
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_CS_1x3_Lay'],'Lay')
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_CS_1x3_Lay'].mean(), 2))}"


    elif metodo == 'Lay 2x2':
        df.loc[df["Resultado_60"] != '2-2', "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay Goleada Visitante':
        filter = ((df['Goals_A_FT'] < 4) | (df['Goals_A_FT'] <= df['Goals_H_FT']))
        df.loc[filter, 'Profit'] = profit_no_comission(df['Odd_CS_Goleada_A'],'Lay')
        df.loc[filter, "Status_Metodo"] = "GREEN"
        odd_media = f"{str(round(df['Odd_CS_Goleada_A'].mean(), 2))}"

    elif metodo == 'Lay 0x1 e Lay 1x0':
        df.loc[((df["Resultado_80"] != '0-1') & (df["Resultado_80"] != '1-0')), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    elif metodo == 'Lay 0x3 e Lay 3x0':
        df.loc[((df["Resultado_80"] != '0-3') & (df["Resultado_80"] != '3-0')), "Status_Metodo"] = "GREEN"
        df['Profit'] = 0

    return df, odd_media