"""
Este módulo realiza cálculos matemáticos y contiene funciones de utilidad.
Autor: [Tu Nombre]
Fecha: [Fecha Actual]
"""
import pandas as pd
import os
import phonenumbers

FILE_CSV = "layout_tnu.csv"

ORIGIN_FILE = "Leads CRM.xlsx"


columns = ["Area Code", "Phone", "Name", "Value",
           "Email", "Tags", "Company", "Assignee"]

df = pd.DataFrame(columns=columns)

df.to_csv(FILE_CSV, index=False, sep=";")

print(f"Archivo creado con exito {FILE_CSV}")


def format_phone_number(phone_str):
    """
    SIRVE PARA DAR FORMATO A LOS NUMEROS
    """

    if pd.isna(phone_str) or not isinstance(phone_str, str):
        return "", ""

    sanitized_phone = phone_str.lower().replace("p:", "").replace(
        " ", "").replace("(", "").replace(")", "").replace("-", "").strip()
    sanitized_phone = ''.join(
        filter(lambda x: x.isdigit() or x == '+', sanitized_phone))

    try:
        if not sanitized_phone.startswith("+"):
            if len(sanitized_phone) > 10:
                sanitized_phone = "+" + sanitized_phone
            else:
                sanitized_phone = "+52" + sanitized_phone

        parsed_number = phonenumbers.parse(sanitized_phone, None)

        if phonenumbers.is_valid_number(parsed_number):
            area_code = str(parsed_number.country_code)
            national_number = str(parsed_number.national_number)
            if area_code == "52":
                area_code = area_code + "1"

            return area_code, national_number
    except phonenumbers.NumberParseException:
        pass

    return "", ""


# Leer Archivo
try:
    df_origin = pd.read_excel(ORIGIN_FILE, engine='openpyxl')
    print("\n Contenido del archivo")
    print(df_origin.head())

    # Aplicar la sanitizcion de numeros:
    phone_data = df_origin["Numero con lada"].astype(
        str).apply(format_phone_number)
    df_origin["Area Code"], df_origin["Phone"] = zip(*phone_data)

    df_mapeado = pd.DataFrame({
        "Area Code": df_origin["Area Code"],
        "Phone": df_origin["Phone"].fillna(""),  # Reemplazar NaN por vacío
        "Name": df_origin["Nombre"],
        "Value": "",  # Asignar valor predeterminado 0
        "Email": df_origin["Correo"],
        "Tags":  df_origin.apply(lambda row: ", ".join(filter(None, [str(row["Sigla"]) if pd.notna(row["Sigla"]) else "", str(row["Campaña"]) if pd.notna(row["Campaña"]) else ""])), axis=1),
        "Company": df_origin.iloc[:, 6],  # Valor fijo para la compañía
        "Assignee": df_origin.iloc[:, 5]
    })

    df_mapeado = df_mapeado.applymap(lambda x: x if isinstance(x, str) else x)

    df_mapeado.to_csv(FILE_CSV, index=False, encoding='utf-8-sig', sep=';')
    print(f"✅ Datos extraídos y guardados en {FILE_CSV}")

except FileNotFoundError:
    print("⚠️ El archivo de origen no existe. Asegúrate de colocarlo en la misma carpeta.")
except KeyError as e:
    print(f"⚠️ Error: La columna {e} no se encontró en el archivo de origen.")
