import os
import pandas as pd
import numpy as np
from clean import clean_data
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
import pickle
from prefect import task, flow
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.models.signature import infer_signature

mlflow.set_tracking_uri("http://localhost:5000") 
mlflow.set_experiment("NYC Rolling Sales")

# load the data
@task(
    name="Load the data",
    tags=["data"],
    retries=3,
    retry_delay_seconds=60
)
def load_data(file_path):
    '''
    Loads the data from the file_path and returns a pandas dataframe.
    '''
    df = clean_data(file_path, verbose=False)
    return df


# Preprocessing
@task(
    name="Preprocessing",
    tags=["preprocessing"],
    retries=3,
    retry_delay_seconds=60
)
def get_pipeline(df, columns_to_drop, estimator, param_grid):
    '''
    Returns a pipeline with the preprocessing steps.
    '''

    mlflow.log_params({"columns_to_drop": columns_to_drop,
                        "estimator": estimator.__name__,
                        "param_grid": param_grid}
    )

    # Get the quantitative and categorical variables
    quantitative_variables = ["GROSS SQUARE FEET", "LAND SQUARE FEET", "YEAR BUILT"]
    categorical_variables = ["NEIGHBORHOOD", "BUILDING CLASS CATEGORY", "TAX CLASS AT PRESENT", "BLOCK", "LOT", "BUILDING CLASS AT PRESENT", "ZIP CODE", "RESIDENTIAL UNITS", "COMMERCIAL UNITS", "TOTAL UNITS", "TAX CLASS AT TIME OF SALE", "BUILDING CLASS AT TIME OF SALE", "SALE DATE"]

    for col in columns_to_drop:
        if col in quantitative_variables:
            quantitative_variables.remove(col)
        elif col in categorical_variables:
            categorical_variables.remove(col)

    mlflow.log_params({"quantitative_variables": quantitative_variables,
                        "categorical_variables": categorical_variables}
    )

    # Preprocessing for numerical data
    quantitative_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())])

    # Preprocessing for categorical data
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))])


    # Bundle preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', quantitative_transformer, quantitative_variables),
            ('cat', categorical_transformer, categorical_variables)])

    # Define the pipeline
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), 
                                # ("grid_search", GridSearchCV(estimator=estimator(), param_grid=param_grid, n_jobs=-1, verbose=1)
                                # ])
                                ("GridSearchCV", GridSearchCV(estimator=estimator(), param_grid=param_grid, n_jobs=-1, verbose=1))
                                ])

    return pipeline


@task(
    name="Get the X and y variables",
    tags=["preprocessing"],
    retries=3,
    retry_delay_seconds=60
)
def get_X_y(df):
    '''
    Returns the X and y variables.
    '''
    X =  df.drop(columns=["SALE PRICE"])
    y = df["SALE PRICE"]
    return X, y

@task(
    name="Get the train and test sets",
    tags=["preprocessing"],
    retries=3,
    retry_delay_seconds=60
)
def get_train_test(X, y):
    '''
    Returns the train and test sets.
    '''

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    return X_train, X_test, y_train, y_test

@task(
    name="Get the model",
    tags=["model"],
    retries=3,
    retry_delay_seconds=60
)
def get_model(pipeline, X_train, y_train):
    '''
    Returns the model.
    '''

    model = pipeline.fit(X_train, y_train)
    return model

@task(
    name="Get the mean absolute error",
    tags=["model"],
    retries=3,
    retry_delay_seconds=60
)
def get_mae(model, X_test, y_test):
    '''
    Returns the mean absolute error.
    '''

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mlflow.log_metric("mae", mae)
    return mae

@task(
    name="Get the root mean squared error",
    tags=["model"],
    retries=3,
    retry_delay_seconds=60
)

def get_rmse(model, X_test, y_test):
    '''
    Returns the root mean squared error.
    '''

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mlflow.log_metric("rmse", rmse)
    return rmse

@task(
    name="Get the r2 score",
    tags=["model"],
    retries=3,
    retry_delay_seconds=60
)

def get_r2(model, X_test, y_test):
    '''
    Returns the r2 score.
    '''

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mlflow.log_metric("r2", r2)
    return r2

@task(
    name="Save the model",
    tags=["model"],
    retries=3,
    retry_delay_seconds=60
)
def save_model(model, mae, rmse, r2, signature):
    '''
    Saves the model to the file_path.
    '''
    print(f"default artifacts URI: '{mlflow.get_artifact_uri()}'")
    mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="NYC Rolling Sales", signature=signature)

    # Register model in mlfow model registry
    client = MlflowClient()
    client.create_model_version(
        name="NYC Rolling Sales",
        source="runs:/" + mlflow.active_run().info.run_id + "/model",
        run_id=mlflow.active_run().info.run_id,
        tags={"mae": mae, "rmse": rmse, "r2": r2}
    )
    

@flow(
    name="NYC Rolling Sales",
)
def main():
    # Load the data
    df = load_data("data/nyc-rolling-sales.csv")

    # Get the X and y variables
    X, y = get_X_y(df)

    # Get the train and test sets
    X_train, X_test, y_train, y_test = get_train_test(X, y)

    # Get the pipeline
    pipeline = get_pipeline(
        df,
        columns_to_drop=["ADDRESS",
                         "EASE-MENT",
                         "APARTMENT NUMBER", 
                         "BUILDING CLASS CATEGORY",
                         "TAX CLASS AT PRESENT",
                         "BLOCK",
                         "LOT",
                         "BUILDING CLASS AT PRESENT",
                         "ZIP CODE",
                         "RESIDENTIAL UNITS",
                         "COMMERCIAL UNITS",
                         "TOTAL UNITS",
                         "TAX CLASS AT TIME OF SALE",
                         "BUILDING CLASS AT TIME OF SALE",
                         "SALE DATE",
                         "NEIGHBORHOOD"
                         ],
        estimator= KNeighborsRegressor,
        param_grid={
            "n_neighbors": [3, 5, 7, 9, 11, 13, 15, 17, 19, 21],
            "weights": ["uniform", "distance"],
            "algorithm": ["auto", "ball_tree", "kd_tree", "brute"],
            "leaf_size": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "p": [1, 2]
        }
    )


    # Get the model
    model = get_model(pipeline, X_train, y_train)

    signature = infer_signature(X_train, model.predict(X_train))

    # Get the mean absolute error
    mae = get_mae(model, X_test, y_test)
    print("MAE: ", mae)

    # Get the root mean squared error
    rmse = get_rmse(model, X_test, y_test)
    print("RMSE: ", rmse)

    # Get the r2 score
    r2 = get_r2(model, X_test, y_test)
    print("R2: ", r2)

    # Save the model
    save_model(model, mae, rmse, r2, signature)

if __name__ == "__main__":
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        main()