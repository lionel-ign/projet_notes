import logging
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

#features général
def nb_actions(df_logs:pd.DataFrame):
    """
    Calculer le nombre d'actions réalisées par chaque personne
    :param df_logs: dataset anonymisé avec les logs
    :return: DataFrame pseudo -> nb
    """
    res = df_logs.groupby('pseudo').size().reset_index(name='nb_actions')
    return res

#features concernant les jours
def moyenne_actions_par_jour(df_logs:pd.DataFrame):
    """
    Calcule le nombre d'actions par jour
    :param df_logs: DataFrame anonymisé avec les logs
    :return:
    """
    res = df_logs.groupby(['pseudo', 'jour']).size().reset_index(name='nb')
    res = res.groupby('pseudo')['nb'].mean().reset_index(name='moyenne_nb_actions')
    return res

def max_actions_par_jour(df_logs:pd.DataFrame):
    """
    Calcule le nombre d'actions par jour
    :param df_logs: DataFrame anonymisé avec les logs
    :return: DataFrame pseudo -> max
    """
    res = df_logs.groupby(['pseudo', 'jour']).size().reset_index(name='nb')
    res = res.groupby('pseudo')['nb'].max().reset_index(name='max_nb_actions')
    return res

def variabilite_activite(df_logs:pd.DataFrame):
    """
    Calcule la variabilité du nombre d'actions par jour, utilisant l'écart-type
    :param df_logs: DataFrame anonymisé avec les logs
    :return: DataFrame pseudo -> var
    """
    res = df_logs.groupby(['pseudo', 'jour']).size().reset_index(name='nb')
    res = res.groupby('pseudo')['nb'].std().reset_index(name='std_actions_par_jour')
    return res

def nb_jours_avec_action(df_logs:pd.DataFrame):
    """
    Calcule le nombre de jours uniques où chaque pseudo a effectué une action.
    :param df_logs: DataFrame contenant les logs
    :return: DataFrame avec le nombre de jours avec action par pseudo
    """
    res = df_logs.groupby('pseudo')['jour'].nunique().reset_index(name='nb_jours_avec_action')
    return res

def tempsdiff(df_logs:pd.DataFrame):
    """
    Calcule le nombre de jours entre le premier jour et le dernier jour avec une action
    :param df_logs: DataFrame contenant les logs
    :return: DataFrame pseudo -> tempsdiff
    """
    res = df_logs.groupby('pseudo')['jour'].agg(lambda x: (x.max() - x.min()).days).reset_index(name='tempsdiff_jours')
    return res

def constance_activite(df_logs:pd.DataFrame):
    """
    Calcule constance d'activite (le nombre de jour avec activité divisé par le nombre de jours entre le premier jour et le dernier jour avec activité)
    :param df_logs: DataFrame contenant les logs
    :return: dataframe pseudo -> constance
    """
    nb_jours_avec_activite = nb_jours_avec_action(df_logs)
    difftemps = tempsdiff(df_logs)
    res = nb_jours_avec_activite.merge(difftemps, on='pseudo')
    res['constance_activite'] = res['nb_jours_avec_action'] / res['tempsdiff_jours'].replace(0, 1)
    return res[['pseudo', 'constance_activite']]

def semaine_vs_weekend(df_logs:pd.DataFrame):
    """
    Calcule le pourcentage d'activité pendant le weekend
    :param df_logs: Dataframe contenant les logs
    :return: Dataframe pseudo -> pourcentage d'activite pendant le weekend
    """
    df_logs['jour_semaine'] = pd.to_datetime(df_logs['jour']).dt.weekday  # lundi=0, dimanche=6
    df_logs['is_weekend'] = df_logs['jour_semaine'] >= 5
    res = df_logs.groupby('pseudo')['is_weekend'].mean().reset_index(name='pct_weekend')
    return res

#features avec heures
def periode_moyen_activite(df_logs:pd.DataFrame):
    """
    Calcule la période moyenne d'activite par jour en minutes
    :param df_logs: dataframe contenant les logs
    :return: dataframe pseudo -> période moyenne d'activté par jour en minutes
    """
    periode = df_logs.groupby(['pseudo', 'jour'])['heure'].agg(lambda x: (x.max() - x.min()).total_seconds() / 60)
    res = periode.groupby('pseudo').mean().reset_index(name='activite_moyenne_par_jour_min')
    return res

def pourcentage_nuit(df_logs:pd.DataFrame):
    """
    Calcule la pourcentage d'activité pendant la nuit (entre 22h le soir et 7h du matin)
    :param df_logs: dataframe contenant les logs
    :return: DataFrame pseudo -> pourcentage d'activité la nuit
    """
    df_logs['heure_seule'] = pd.to_datetime(df_logs['heures'], format="%H:%M:%S").dt.hour
    df_logs['pourcentage_nuit'] = (df_logs['heure_seule'] < 7) | (df_logs['heure_seule'] >= 22)
    res = df_logs.groupby('pseudo')['pourcentage_nuit'].mean().reset_index(name='pourcentage_activite_nuit')
    return res

def pourcentage_matin(df_logs:pd.DataFrame):
    """
    Calcule la pourcentage d'activité le matin (entre 7h et 13h)
    :param df_logs: dataframe contenant les logs
    :return: DataFrame pseudo -> pourcentage d'activité le matin
    """
    df_logs['heure_seule'] = pd.to_datetime(df_logs['heures'], format="%H:%M:%S").dt.hour
    df_logs['pourcentage_matin'] = (df_logs['heure_seule'] >= 7) & (df_logs['heure_seule'] < 13)
    res = df_logs.groupby('pseudo')['pourcentage_matin'].mean().reset_index(name='pourcentage_activite_matin')
    return res

def pourcentage_aprem(df_logs:pd.DataFrame):
    """
    Calcule la pourcentage d'activité l'après-midi (entre 13h et 18h)
    :param df_logs: dataframe contenant les logs
    :return: DataFrame pseudo -> pourcentage d'activité l'après-midi
    """
    df_logs['heure_seule'] = pd.to_datetime(df_logs['heures'], format="%H:%M:%S").dt.hour
    df_logs['pourcentage_aprem'] = (df_logs['heure_seule'] >= 13) & (df_logs['heure_seule'] < 18)
    res = df_logs.groupby('pseudo')['pourcentage_aprem'].mean().reset_index(name='pourcentage_activite_aprem')
    return res

def pourcentage_soir(df_logs:pd.DataFrame):
    """
    Calcule la pourcentage d'activité le soir (entre 18h et 22h)
    :param df_logs: dataframe contenant les logs
    :return: DataFrame pseudo -> pourcentage d'activité le soir
    """
    df_logs['heure_seule'] = pd.to_datetime(df_logs['heures'], format="%H:%M:%S").dt.hour
    df_logs['pourcentage_soir'] = (df_logs['heure_seule'] >= 18) & (df_logs['heure_seule'] < 22)
    res = df_logs.groupby('pseudo')['pourcentage_soir'].mean().reset_index(name='pourcentage_activite_soir')
    return res

#features utilisant le composant
def nb_composant(df_logs:pd.DataFrame):
    """
    Calcule le nombre de composants différentes
    :param df_logs: DataFrame contenant les logs
    :return: DataFrame pseudo -> nombre de composants
    """
    res = df_logs.groupby('pseudo')['composant'].nunique().reset_index(name='nb_composant')
    return res

def nb_chaque_composant(df_logs:pd.DataFrame):
    """
    Calcule le nombre d'activités de chaque composant
    :param df_logs: dataframe contenant les logs
    :return: dataframe avec pseudo et le nombre d'activités pour chaque composant
    """
    res = pd.crosstab(df_logs['pseudo'], df_logs['composant']).reset_index()
    res.columns = ['pseudo'] + [f"composant_{col}" for col in res.columns if col != 'pseudo']
    return res

def top_composant(df_logs:pd.DataFrame):
    """
    Calcule le composant le plus utilisé par pseudo
    :param df_logs: dateframe contenant les logs
    :return: dataframe pseudo -> le composant le plus utilisé
    """
    top_composant = df_logs.groupby(['pseudo', 'composant']).size().reset_index(name='count')
    res = top_composant.loc[top_composant.groupby('pseudo')['count'].idxmax(), ['pseudo', 'composant']]
    res = res.rename(columns={'composant': 'top_composant'})
    return res

#features utilisant le contexte générale
def nb_contexte_gen(df_logs:pd.DataFrame):
    """
    Calcule le nombre de contexte générale différentes
    :param df_logs: DataFrame contenant les logs
    :return: DataFrame pseudo -> nombre de contextes
    """
    res = df_logs.groupby('pseudo')['contexte_general'].nunique().reset_index(name='nb_contexte')
    return res

def nb_chaque_contexte(df_logs:pd.DataFrame):
    """
    Calcule le nombre d'activités de chaque pseudo pour chaque contexte général.
    :param df_logs: DataFrame contenant les logs
    :return: DataFrame avec pseudo et le nombre d'activités pour chaque contexte
    """
    res = pd.crosstab(df_logs['pseudo'], df_logs['contexte_general']).reset_index()
    res.columns = ['pseudo'] + [f"contexte_{col}" for col in res.columns if col != 'pseudo']
    return res

def top_contexte(df_logs:pd.DataFrame):
    """
    Calcule le contexte le plus utilisé par pseudo
    :param df_logs: dateframe contenant les logs
    :return: dataframe pseudo -> le contextes le plus utilisé
    """
    top_contexte = df_logs.groupby(['pseudo', 'contexte_general']).size().reset_index(name='count')
    res = top_contexte.loc[top_contexte.groupby('pseudo')['count'].idxmax(), ['pseudo', 'contexte_general']]
    res = res.rename(columns={'contexte_general': 'top_contexte'})
    return res

#features utilisant l'evenement
def nb_chaque_evenement(df_logs:pd.DataFrame):
    """
    Calcule le nombre d'activités de chaque pseudo pour chaque evenement.
    :param df_logs: DataFrame contenant les logs
    :return: DataFrame avec pseudo et le nombre d'activités pour chaque evenement
    """
    res = pd.crosstab(df_logs['pseudo'], df_logs['evenement']).reset_index()
    res.columns = ['pseudo'] + [f"evenement_{col}" for col in res.columns if col != 'pseudo']
    return res

def top_evenement(df_logs:pd.DataFrame):
    """
    Calcule l'evenement le plus utilisé par pseudo
    :param df_logs: dateframe contenant les logs
    :return: dataframe pseudo -> l'evenement le plus utilisé
    """
    top_evenement = df_logs.groupby(['pseudo', 'evenement']).size().reset_index(name='count')
    res = top_evenement.loc[top_evenement.groupby('pseudo')['count'].idxmax(), ['pseudo', 'evenement']]
    res = res.rename(columns={'evenement': 'top_evenement'})
    return res

#Créer le DataFrame pour analyses
def creer_df(df_logs:pd.DataFrame):
    """
    Fonction qui permet de créer le DataFrame qui va servir pour le reste de l'analyse
    :param df_logs: dataframe contenant les logs
    :return: DataFrame avec toutes les features qu'on a créées
    """
    df = nb_actions(df_logs)
    df = df.merge(moyenne_actions_par_jour(df_logs), on="pseudo", how="left")
    df = df.merge(nb_jours_avec_action(df_logs), on="pseudo", how="left")
    df = df.merge(variabilite_activite(df_logs), on="pseudo", how="left")
    df = df.merge(tempsdiff(df_logs), on="pseudo", how="left")
    df = df.merge(constance_activite(df_logs), on="pseudo", how="left")
    df = df.merge(periode_moyen_activite(df_logs), on="pseudo", how="left")
    df = df.merge(pourcentage_nuit(df_logs), on="pseudo", how="left")
    df = df.merge(pourcentage_matin(df_logs), on="pseudo", how="left")
    df = df.merge(pourcentage_aprem(df_logs), on="pseudo", how="left")
    df = df.merge(pourcentage_soir(df_logs), on="pseudo", how="left")
    df = df.merge(semaine_vs_weekend(df_logs), on="pseudo", how="left")
    df = df.merge(nb_contexte_gen(df_logs), on="pseudo", how="left")
    df = df.merge(nb_composant(df_logs), on="pseudo", how="left")
    df = df.merge(nb_chaque_contexte(df_logs), on="pseudo", how="left")
    df = df.merge(top_contexte(df_logs), on="pseudo", how="left")
    df = df.merge(nb_chaque_composant(df_logs), on="pseudo", how="left")
    df = df.merge(top_composant(df_logs), on="pseudo", how="left")
    df = df.merge(nb_chaque_evenement(df_logs), on="pseudo", how="left")
    df = df.merge(top_evenement(df_logs), on="pseudo", how="left")
    return df

def save_dataframe(df:pd.DataFrame, filename:str):
    """
    Ecrire le df créé dans un fichier csv
    :param df: DataFrame à écrire
    :param filename: nombre du fichier (sans extension)
    """
    df.to_csv(f"{filename}.csv", index=False)
    print(f"DataFrame opgeslagen als {filename}.csv")

# Train-set split
def separation_train_test(df:pd.DataFrame, df_notes:pd.DataFrame):
    """
    Préparation basique des dataframes pour la suite de l'analyse
    :param df: dataframe contenant les features
    :param df_notes: dataframe contenant les notes
    :return: un dataframe X_train avec les features et 80% des observations, un dataframe X_test avec les features et 20% des observations,
    un vecteur y_train avec les notes de 80% des observations et un vecteur y_test avec les notes de 20% des observations
    """
    df_all = df.merge(df_notes, on="pseudo") #S'assurer que les deux df sont au même ordre
    y = df_all["note"]
    X = df_all.drop(["note", "pseudo"], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    return X_train, X_test, y_train, y_test

# Transformation du DataFrame logs
def enlever_correlations_complets(df:DataFrame):
    """
    Enlève les features qui on une corrélation de 1 (deuxième encontré est enlèvé)
    :param df: Dataframe avec les features
    :return: Dataframe avec moins de features
    """
    corr_matrix = df.select_dtypes(include=['float64', 'int64']).corr()
    columns_to_drop = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) == 1:  # If correlation is exactly 1
                colname = corr_matrix.columns[i]  # Get the column name
                columns_to_drop.append(colname)
    df_cleaned = df.drop(columns=columns_to_drop)
    #print(f"Columns dropped: {columns_to_drop}")
    #print(df.shape)
    return df_cleaned

def encodage(df:pd.DataFrame):
    """
    Fonction qui permet d'encoder les variables catégorielles
    :param df: Dataframes avec les features
    :return: Dateframe avec seulement des variables numériques
    """
    encoder = OneHotEncoder(sparse_output=False)
    categorical_cols = df.select_dtypes(include='object').columns
    encoded_array = encoder.fit_transform(df[categorical_cols])

    encoded_cols = encoder.get_feature_names_out(categorical_cols)
    df_encoded = pd.DataFrame(encoded_array, columns=encoded_cols)
    df_encode = df.drop(columns=categorical_cols).join(df_encoded)

    return df_encode

def scaling(df:pd.DataFrame):
    """
    Permet de standardiser un dataframe antérieurement encodé. MinMax est utilisé pour garder les colonnes binaires
    :param df: Dataframe avec seulement valeurs numériques
    :return: Dataframe avec colonnes scaled
    """
    df_scaled = df.copy()
    cols_to_scale = df_scaled.columns.difference(['pseudo'])
    scaler = MinMaxScaler()
    df_scaled[cols_to_scale] = scaler.fit_transform(df_scaled[cols_to_scale])
    return df_scaled

def reduction_dimensions(df:pd.DataFrame):
    """

    :param df:
    :return:
    """
    pass

def df_transformer(df:pd.DataFrame):
    """
    Permet de transformer le dataframe et le mettre en bon format pour utiliser dans les modèles de machine learning
    :param df: Dataframe avec les features
    :return: Dataframe transformé sans variables corrélées à 100%, toutes les variables numériques (encodées) et scalées
    """
    df = enlever_correlations_complets(df)
    df = encodage(df)
    df = scaling(df)
    return df

if __name__ == '__main__':
    import modele

    logs = modele.get_logs()
    notes = modele.get_notes()
    logs = modele.filter_logs(logs, notes)
    logs = modele.split_columns(logs)
    notes = modele.filter_notes(notes, logs)
    print(logs.head(10))
    print(logs.shape)
    print(notes.shape)

    df = creer_df(logs)
    print(df.head(10))
    print(df.shape)

    X_train, X_test, y_train, y_test = separation_train_test(df, notes)
    print(X_train.shape, y_train.shape)
    print(X_test.shape, y_test.shape)
    print(X_train.head())

    X_train_encode = encodage(X_train)
    print(X_train_encode.shape)
    print(X_train_encode.head())

    #save_dataframe(df, "df_complet")

    #df_cleaned = df_transformer(X_train)
    #print(df_cleaned.head(10))
    #print(df_cleaned.shape)