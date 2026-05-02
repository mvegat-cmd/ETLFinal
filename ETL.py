import pandas as pd
#Lectura de archivos
catalog = pd.read_csv("data/Catalog_Orders.txt", sep=",")
products = pd.read_csv("data/products.txt", sep=",")
web = pd.read_csv("data/Web_orders.txt", sep=";")
with open("data/Web_orders.txt", "r", encoding="utf-8") as f:
    header = f.readline().replace('"','').strip().split(",")
web = pd.read_csv(
    "data/Web_orders.txt",
    sep=";",
    skiprows=1,
    names=header,
    engine="python"
)
# Renombrar
web.columns = ["ID", "INV", "PCODE", "DATE", "CATALOG", "QTY", "custnum"]
print(web.head())
print(web.columns)
#Mostrar primeras filas
print("CATALOG ORDERS")
print(catalog.head())
print("\nWEB ORDERS")
print(web.head())
print("\nPRODUCTS")
print(products.head())


#Limpieza en Fechas
web["DATE"] = pd.to_datetime(web["DATE"], dayfirst=True, errors="coerce")
def limpiar_date_catalog(date):
    try:
        partes = str(date).split("/")
        if len(partes) == 3:
            mes = partes[0]
            anio = partes[1]
            dia = partes[2]

            if len(anio) == 2:
                anio = "19" + anio

            return f"{anio}-{mes}-{dia}"
        else:
            return None
    except:
        return None
catalog["DATE"] = catalog["DATE"].apply(limpiar_date_catalog)
catalog["DATE"] = pd.to_datetime(catalog["DATE"], errors="coerce")

#Limpieza en cantidad
catalog["QTY"] = pd.to_numeric(catalog["QTY"], errors="coerce")
web["QTY"] = pd.to_numeric(web["QTY"], errors="coerce")
catalog["QTY"] = catalog["QTY"].fillna(0)
web["QTY"] = web["QTY"].fillna(0)

#Limpieza en caracteres de clientes
catalog["custnum"] = catalog["custnum"].astype(str).str.strip()
web["custnum"] = web["custnum"].astype(str).str.strip()

#Generamos un listado de clientes unicos
ventas_clientes = pd.concat([
    catalog[["custnum"]],
    web[["custnum"]]
], ignore_index=True).drop_duplicates()

ventas_clientes["id_cliente"] = range(1, len(ventas_clientes) + 1)

catalog = catalog.merge(ventas_clientes, on="custnum", how="left")
web = web.merge(ventas_clientes, on="custnum", how="left")

#Limpieza en Catalog, se crea diccionario considerando inconsistencias encontradas y normalizando
catalog["CATALOG"] = catalog["CATALOG"].astype(str).str.strip().str.upper()
web["CATALOG"] = web["CATALOG"].astype(str).str.strip().str.upper()

map_catalog = {
    "SPORT": "SPORTS",
    "SPORST": "SPORTS",
    "SPOTS": "SPORTS",
    "TOY": "TOYS",
    "TOSY": "TOYS",
    "TOTS": "TOYS",
    "PET": "PETS",
    "PEST": "PETS",
    "PATS": "PETS",
    "PRTS": "PETS",
    "SOFTWAR": "SOFTWARE",
    "SOFTWARS": "SOFTWARE",
    "SOFTWARES": "SOFTWARE",
    "GARDNING": "GARDENING",
    "COLECTIBLES": "COLLECTIBLES",
    "COLLECTIBLE": "COLLECTIBLES",
    "COLLECTABLES": "COLLECTIBLES"
}

catalog["CATALOG"] = catalog["CATALOG"].replace(map_catalog)
web["CATALOG"] = web["CATALOG"].replace(map_catalog)

categorias_validas = ["SPORTS", "PETS", "TOYS", "GARDENING", "SOFTWARE", "COLLECTIBLES"]

catalog["CATALOG_VALIDO"] = catalog["CATALOG"].isin(categorias_validas)
web["CATALOG_VALIDO"] = web["CATALOG"].isin(categorias_validas)

print(catalog["CATALOG"].value_counts())
print(web["CATALOG"].value_counts())

print(catalog[catalog["CATALOG_VALIDO"] == False][["CATALOG", "PCODE"]].head())
print(web[web["CATALOG_VALIDO"] == False][["CATALOG", "PCODE"]].head())

#Estadarizando PCODE en Datasets
catalog["PCODE"] = catalog["PCODE"].astype(str).str.strip().str.upper()
web["PCODE"] = web["PCODE"].astype(str).str.strip().str.upper()
products["PCODE"] = products["PCODE"].astype(str).str.strip().str.upper()

catalog["PCODE"] = catalog["PCODE"].str.replace("O","0",regex=False)
web["PCODE"] = web["PCODE"].str.replace("O","0",regex=False)

catalog["PCODE_VALIDO"] = catalog["PCODE"].isin(products["PCODE"])
web["PCODE_VALIDO"] = web["PCODE"].isin(products["PCODE"])

print(catalog["PCODE_VALIDO"].value_counts())
print(web["PCODE_VALIDO"].value_counts())

print(catalog[catalog["PCODE_VALIDO"] == False][["PCODE","CATALOG"]].head())
print(web[web["PCODE_VALIDO"] == False][["PCODE","CATALOG"]].head())

#Eliminar registros nulos
print("Catalog total inicial:", len(catalog))
print("Web total inicial:", len(web))
null_catalog = catalog[catalog[["PCODE","CATALOG"]].isnull().any(axis=1)]
null_web = web[web[["PCODE","CATALOG"]].isnull().any(axis=1)]

print("Catalog nulos:", len(null_catalog))
print("Web nulos:", len(null_web))
invalid_qty_catalog = catalog[catalog["QTY"] < 0]
invalid_qty_web = web[web["QTY"] < 0]

print("Catalog QTY inválido:", len(invalid_qty_catalog))
print("Web QTY inválido:", len(invalid_qty_web))

catalog = catalog.dropna(subset=["PCODE","CATALOG"]) 
web = web.dropna(subset=["PCODE","CATALOG"]) 
catalog = catalog[catalog["QTY"] >= 0] 
web = web[web["QTY"] >= 0]

#Mostrar primeras filas
print("CATALOG ORDERS")
print(catalog.head())
print("\nWEB ORDERS")
print(web.head())
print("\nPRODUCTS")
print(products.head())
#Parte de Análisis
print("TIPOS DE DATOS")
print("Catalog")
print(catalog.dtypes)
print("Web")
print(web.dtypes)
print("Products")
print(products.dtypes)

print("RESUMEN ESTADISTICO")
print("Catalog")
print(catalog.describe(include='all'))
print("Web")
print(web.describe(include='all'))
print("Products")
print(products.describe(include='all'))

print("VALORES NULOS")
print("Catalog")
print(catalog.isnull().sum())
print("Web")
print(web.isnull().sum())
print("Products")
print(products.isnull().sum())

print("VALORES UNICOS")
print("Catalog")
print(catalog.nunique())
print("Web")
print(web.nunique())
print("Products")
print(products.nunique())

print("DISTRIBUCION CATEGORIAS")
catalog.columns = ["id", "invoice", "fecha", "catalogo", "pcode", "qty", "cliente"]
web.columns = ["id", "invoice", "pcode", "fecha", "catalogo", "qty", "cliente"]
print("Catalog")
print(catalog["catalogo"].value_counts())
print("Web")
print(web["catalogo"].value_counts())
print(web.columns)

print("RELACION PRODUCTO CANTIDAD")
print("Catalog")
print(catalog.groupby("pcode")["qty"].sum().sort_values(ascending=False).head())
print("Web")
print(web.groupby("pcode")["qty"].sum().sort_values(ascending=False).head())


############################
#Carga a SQL
from sqlalchemy import create_engine
usuario = "postgres"
password = "admin"
host = "localhost"
puerto = "5432"
db = "ETL_DW"

engine = create_engine(f"postgresql+psycopg2://{usuario}:{password}@{host}:{puerto}/{db}")

# AGREGAR CANAL
catalog["canal"] = "CATALOGO"
web["canal"] = "WEB"
# UNIFICAR VENTAS
ventas = pd.concat([catalog, web], ignore_index=True)
# LIMPIEZA PRODUCTS
products["PRICE"] = pd.to_numeric(products["PRICE"], errors="coerce")
products["COST"] = pd.to_numeric(products["COST"], errors="coerce")

# DIMENSIONES
dim_producto = products[["PCODE","TYPE","DESCRIP","PRICE","COST","supplier"]].drop_duplicates()
dim_producto = dim_producto.rename(columns={
    "PCODE": "pcode",
    "TYPE": "type",
    "DESCRIP": "descrip",
    "PRICE": "price",
    "COST": "cost"
})
dim_tiempo = ventas[["DATE"]].drop_duplicates()
dim_tiempo["anio"] = dim_tiempo["DATE"].dt.year
dim_tiempo["mes"] = dim_tiempo["DATE"].dt.month
dim_tiempo["dia"] = dim_tiempo["DATE"].dt.day
dim_tiempo["trimestre"] = dim_tiempo["DATE"].dt.quarter
dim_tiempo = dim_tiempo.rename(columns={"DATE": "date_value"})
dim_cliente = ventas[["custnum"]].drop_duplicates()
dim_cliente = dim_cliente.dropna(subset=["custnum"])
dim_canal = ventas[["canal"]].drop_duplicates()
dim_catalogo = ventas[["CATALOG"]].drop_duplicates()
dim_catalogo = dim_catalogo.rename(columns={"CATALOG": "catalog"})

# CARGA DIMENSIONES
dim_canal.to_sql("dim_canal", engine, if_exists="append", index=False)
dim_catalogo.to_sql("dim_catalogo", engine, if_exists="append", index=False)
dim_producto.to_sql("dim_producto", engine, if_exists="append", index=False)
dim_tiempo.to_sql("dim_tiempo", engine, if_exists="append", index=False)
dim_cliente.to_sql("dim_cliente", engine, if_exists="append", index=False)

# RECUPERAR ID GENERADO EN POSTGRESQL
dim_producto_db = pd.read_sql("SELECT id_producto, pcode, price, cost FROM dim_producto", engine)
dim_tiempo_db = pd.read_sql("SELECT id_tiempo, date_value FROM dim_tiempo", engine)
dim_tiempo_db["date_value"] = pd.to_datetime(dim_tiempo_db["date_value"])
dim_cliente_db = pd.read_sql("SELECT id_cliente, custnum FROM dim_cliente", engine)
dim_canal_db = pd.read_sql("SELECT id_canal, canal FROM dim_canal", engine)
dim_catalogo_db = pd.read_sql("SELECT id_catalogo, catalog FROM dim_catalogo", engine)

# JOINS
ventas = ventas.merge(dim_producto_db, left_on="PCODE", right_on="pcode", how="inner")
ventas = ventas.merge(dim_tiempo_db, left_on="DATE", right_on="date_value", how="inner")
ventas = ventas.merge(dim_cliente_db, on="custnum", how="inner")
ventas = ventas.merge(dim_canal_db, on="canal", how="inner")
ventas = ventas.merge(dim_catalogo_db, left_on="CATALOG", right_on="catalog", how="inner")

# MÉTRICAS
ventas["importe_venta"] = ventas["QTY"] * ventas["price"]
ventas["costo_total"] = ventas["QTY"] * ventas["cost"]
ventas["margen"] = ventas["importe_venta"] - ventas["costo_total"]


print(ventas.columns)
print(ventas["DATE"].dtype)
print(dim_tiempo_db["date_value"].dtype)



# TBLA DE HECHOS
fact_ventas = ventas[[
    "INV",
    "id_producto",
    "id_tiempo",
    "id_cliente",
    "id_canal",
    "id_catalogo",
    "QTY",
    "importe_venta",
    "costo_total",
    "margen"
]].copy()

fact_ventas = fact_ventas.rename(columns={
    "INV": "invoice",
    "QTY": "qty"
})

fact_ventas.to_sql("fact_ventas", engine, if_exists="append", index=False)

print("Carga completa OK")
print("Filas cargadas:", len(fact_ventas))