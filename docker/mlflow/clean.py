import great_expectations as ge
import pandas as pd


# region: Helper functions

def load_data(path: str):
    '''
    Reads the data from the path and returns a ge dataframe.
    '''
    df = ge.read_csv(path, index_col=0)
    return df

def to_string(value):
    '''
    Converts the value to string.
    '''
    try:
        return str(value)
    except ValueError:
        return ""
    
def to_number(value, type="integer"):
    '''
    Converts the value to integer or float.
    '''
    try:
        if(type == "integer"):
            return int(value)
        else:
            return float(value)
    except ValueError:
        return None

# endregion

# region: general data cleaning

def check_string_validity(df, col:str, verbose=True):
    '''
    Checks if the column contains valid string values.
    If not, it removes the rows with invalid values.
    '''

    # if col is undefined or column does not exist in the dataframe
    if(col is None or col not in df.columns):
        raise ValueError("Cannot fix column, because it does not exist")

    if(df.expect_column_values_to_not_be_null(col).success is False):
        print(f"Column {col} contains null values") if verbose else None
        df = df[df[col].notnull()]
        return df

    if(df.expect_column_values_to_be_of_type(col, "str").success is False):
        print(f"Column {col} is not of type string") if verbose else None
        df[col] = df[col].apply(lambda x: to_string(x))
        df = df[df[col].notnull()]

    return df


def check_number_validity(df, col:str, type="integer", verbose=True):
    '''
    Checks if the column contains valid number values.
    If not, it removes the rows with invalid values.
    '''

    if(col is None or col not in df.columns):
        raise ValueError("Cannot fix column, because it does not exist")
    
    if(df.expect_column_values_to_not_be_null(col).success is False):
        print(f"Column {col} contains null values") if verbose else None
        df = df[df[col].notnull()]
        return df

    if(df.expect_column_values_to_be_of_type(col, type).success is False):
        print(f"Column {col} is not of type {type}") if verbose else None
        df[col] = df[col].apply(lambda x: to_number(x))
        df = df[df[col].notnull()]

    return df

# endregion

# region: custom column cleaning

def check_borough_validity(df, verbose=True):
    '''
    Checks if the column BOROUGH contains valid values.
    If not, it removes the rows with invalid values.
    '''

    # check if the column contains valid values
    if(df.expect_column_values_to_be_in_set(
        column="BOROUGH",
        value_set=[1, 2, 3, 4, 5],
        result_format="SUMMARY",
    ).success is False):
        print("Column BOROUGH contains invalid values") if verbose else None
        df = df[df["BOROUGH"].isin([1, 2, 3, 4, 5])]
        return df
    return df


def check_salePrice_validity(df, verbose=True):
    '''
    Checks if the column SALE PRICE contains valid values.
    If not, it removes the rows with invalid values.
    '''

    # check if the column contains valid values
    if(df.expect_column_values_to_be_between(
        column="SALE PRICE",
        min_value=1000,
        max_value=100000000,
        result_format="SUMMARY",
    ).success is False):
        print("Column SALE PRICE contains invalid values") if verbose else None
        df = df[df["SALE PRICE"].between(0, 100000000)]
        return df
    return df




# endregion

def check_data_validity(df, verbose=True):
    '''
    For each column, checks if the column contains valid values and valid types.
    If not, it removes the rows.
    '''

    # BOROUGH
    df = check_number_validity(df, "BOROUGH", verbose=verbose)
    df = check_borough_validity(df, verbose=verbose)

    # NEIGHBORHOOD
    df = check_string_validity(df, "NEIGHBORHOOD", verbose=verbose)

    # BUILDING CLASS CATEGORY
    df = check_string_validity(df, "BUILDING CLASS CATEGORY", verbose=verbose)

    # TAX CLASS AT PRESENT
    df = check_string_validity(df, "TAX CLASS AT PRESENT", verbose=verbose)

    # BLOCK
    df = check_number_validity(df, "BLOCK", verbose=verbose)

    # LOT
    df = check_number_validity(df, "LOT", verbose=verbose)

    # BUILDING CLASS AT PRESENT
    df = check_string_validity(df, "BUILDING CLASS AT PRESENT", verbose=verbose)

    # ZIP CODE
    df = check_number_validity(df, "ZIP CODE", verbose=verbose)

    # RESIDENTIAL UNITS
    df = check_number_validity(df, "RESIDENTIAL UNITS", verbose=verbose)

    # COMMERCIAL UNITS
    df = check_number_validity(df, "COMMERCIAL UNITS", verbose=verbose)

    # TOTAL UNITS
    df = check_number_validity(df, "TOTAL UNITS", verbose=verbose)

    # LAND SQUARE FEET
    df = check_number_validity(df, "LAND SQUARE FEET", type="float", verbose=verbose)

    # GROSS SQUARE FEET
    df = check_number_validity(df, "GROSS SQUARE FEET", type="float", verbose=verbose)

    # YEAR BUILT
    df = check_number_validity(df, "YEAR BUILT", verbose=verbose)

    # TAX CLASS AT TIME OF SALE
    df = check_string_validity(df, "TAX CLASS AT TIME OF SALE", verbose=verbose)

    # BUILDING CLASS AT TIME OF SALE
    df = check_string_validity(df, "BUILDING CLASS AT TIME OF SALE", verbose=verbose)

    # SALE PRICE
    df = check_number_validity(df, "SALE PRICE", type="float", verbose=verbose)
    df = check_salePrice_validity(df, verbose=verbose)

    # SALE DATE
    df = check_string_validity(df, "SALE DATE", verbose=verbose)

    return df

def clean_data(path: str, verbose=True):
    '''
    Reads the data from the path, cleans it and returns a ge dataframe.
    '''
    df = load_data(path)
    df = check_data_validity(df, verbose=verbose)

    # remove duplicates
    df = df.drop_duplicates()

    # drop EASE-MENT column because it is empty
    df.drop("EASE-MENT", axis=1, inplace=True)

    # save the cleaned data
    df.to_csv("data/cleaned_data.csv")

    df = pd.read_csv("data/cleaned_data.csv", index_col=0)

    return df