import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
import joblib


def get_predict(data):
    def modify_data(df):
        df['FamilySize'] = np.where(df['SibSp'] + df['Parch'] == 0, 'Solo',
                                          np.where(df['SibSp'] + df['Parch'] <= 3, 'Middle', 'Big'))
        df.drop(columns=['Name', 'Ticket', 'Cabin', 'SibSp', 'Parch'], inplace=True)
        return df



    trained_model = joblib.load('titanic_XGBClassifier_model.joblib')

    train_df = pd.read_csv('train.csv', index_col='PassengerId')
    train_df.drop(columns=['Survived'], inplace=True)
    train_df = modify_data(train_df)

    test_df = pd.DataFrame(data)
    test_df.set_index('PassengerId', inplace=True)
    test_df = modify_data(test_df)

    features_num = ['Age', 'Fare']
    features_cat = ['Pclass', 'Sex', 'FamilySize', 'Embarked']

    transformer_num = make_pipeline(
        SimpleImputer(strategy="mean"),
        StandardScaler(),
    )

    transformer_cat = make_pipeline(
        SimpleImputer(strategy='most_frequent'),
        OneHotEncoder(handle_unknown='ignore'),
    )

    preprocessor = make_column_transformer(
        (transformer_num, features_num),
        (transformer_cat, features_cat)
    )

    preprocessor.fit_transform(train_df)
    test_df = preprocessor.transform(test_df)

    predict = trained_model.predict(test_df)

    return predict
