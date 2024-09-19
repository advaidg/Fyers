def fetch_data(option_type):
    global options, matrix_lines
    sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRnTeq02XqSkqPgIFTXBG_kUkfND08mbJIXk0m_1ADr5W9BtSX_gdqwSm3LtWyTRDDbB3wCFzuc6Vm9/pub?output=csv'
    df = pd.read_csv(sheet_url)
    if option_type == "CE":
        options = [df.columns[0]]  # Use the name of the first column as options
        matrix_lines = df.iloc[:, 0].dropna().tolist()  # Values in the first column
    elif option_type == "PE":
        options = [df.columns[1]]  # Use the name of the first column as options
        matrix_lines = df.iloc[:, 1].dropna().tolist()  # Values in the second column
    else:
        raise ValueError("Invalid option_type specified. Use 'CE' or 'PE'.")

    print("Options:", options)
    print("Matrix Lines:", matrix_lines)
